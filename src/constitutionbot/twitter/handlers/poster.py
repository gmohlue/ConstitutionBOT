"""Post approved content to Twitter."""

import asyncio
from typing import Optional

from constitutionbot.config import get_settings
from constitutionbot.core.content.formats import Thread
from constitutionbot.database import async_session_maker
from constitutionbot.database.models import ContentStatus
from constitutionbot.database.repositories.content_queue import ContentQueueRepository
from constitutionbot.database.repositories.post_history import PostHistoryRepository
from constitutionbot.database.repositories.reply_queue import ReplyQueueRepository
from constitutionbot.twitter.client import TwitterClient


class ContentPoster:
    """Post approved content and replies to Twitter."""

    def __init__(self):
        self.settings = get_settings()
        self.twitter = TwitterClient()
        self._running = False

    async def post_approved_content(self) -> int:
        """Post all approved content from the queue.

        Returns:
            Number of items posted
        """
        posted = 0

        async with async_session_maker() as session:
            content_repo = ContentQueueRepository(session)
            history_repo = PostHistoryRepository(session)

            approved = await content_repo.get_approved(limit=10)

            for item in approved:
                try:
                    if item.content_type == "thread":
                        # Parse and post thread
                        thread = Thread.from_storage(item.formatted_content)
                        tweet_ids = self.twitter.post_thread(
                            [t.content for t in thread.tweets]
                        )

                        if tweet_ids:
                            # Record first tweet in history
                            await history_repo.create(
                                tweet_id=tweet_ids[0],
                                content=item.formatted_content,
                                content_type="thread",
                            )
                            await content_repo.mark_posted(item.id)
                            posted += 1
                            print(f"Posted thread ({len(tweet_ids)} tweets)")
                    else:
                        # Post single tweet
                        tweet_id = self.twitter.post_tweet(item.formatted_content)

                        if tweet_id:
                            await history_repo.create(
                                tweet_id=tweet_id,
                                content=item.formatted_content,
                                content_type="tweet",
                            )
                            await content_repo.mark_posted(item.id)
                            posted += 1
                            print(f"Posted tweet: {tweet_id}")

                except Exception as e:
                    print(f"Failed to post content {item.id}: {e}")

            await session.commit()

        return posted

    async def post_approved_replies(self) -> int:
        """Post all approved replies.

        Returns:
            Number of replies posted
        """
        posted = 0

        async with async_session_maker() as session:
            reply_repo = ReplyQueueRepository(session)
            history_repo = PostHistoryRepository(session)

            approved = await reply_repo.get_approved(limit=10)

            for item in approved:
                try:
                    # Use final_reply if edited, otherwise draft
                    reply_text = item.final_reply or item.draft_reply

                    # Post as reply to the original mention
                    tweet_id = self.twitter.post_tweet(
                        text=reply_text,
                        reply_to_id=item.mention_id,
                    )

                    if tweet_id:
                        await history_repo.create(
                            tweet_id=tweet_id,
                            content=reply_text,
                            content_type="tweet",
                            is_reply=True,
                            reply_to_id=item.mention_id,
                        )
                        await reply_repo.mark_posted(item.id)
                        posted += 1
                        print(f"Posted reply to @{item.mention_author}")

                except Exception as e:
                    print(f"Failed to post reply {item.id}: {e}")

            await session.commit()

        return posted

    async def post_all(self) -> dict:
        """Post all approved content and replies.

        Returns:
            Dictionary with counts of posted items
        """
        content_count = await self.post_approved_content()
        reply_count = await self.post_approved_replies()

        return {
            "content_posted": content_count,
            "replies_posted": reply_count,
        }

    async def start_posting_loop(self, interval: int = 60) -> None:
        """Start the posting loop.

        Args:
            interval: Seconds between posting checks
        """
        self._running = True
        print(f"Starting content poster (interval: {interval}s)")

        while self._running:
            try:
                result = await self.post_all()
                total = result["content_posted"] + result["replies_posted"]
                if total > 0:
                    print(f"Posted {result['content_posted']} content, {result['replies_posted']} replies")
            except Exception as e:
                print(f"Error in posting loop: {e}")

            await asyncio.sleep(interval)

    def stop_posting(self) -> None:
        """Stop the posting loop."""
        self._running = False
        print("Content poster stopped")
