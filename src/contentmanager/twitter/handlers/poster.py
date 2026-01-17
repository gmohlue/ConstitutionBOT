"""Post approved content to Twitter."""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

from contentmanager.config import get_settings
from contentmanager.core.content.formats import Thread
from contentmanager.database import async_session_maker
from contentmanager.database.models import ContentStatus
from contentmanager.database.repositories.content_queue import ContentQueueRepository
from contentmanager.database.repositories.post_history import PostHistoryRepository
from contentmanager.database.repositories.reply_queue import ReplyQueueRepository
from contentmanager.twitter.client import TwitterClient


class ContentPoster:
    """Post approved content and replies to Twitter."""

    def __init__(self):
        self.settings = get_settings()
        self.twitter = TwitterClient()
        self._running = False

    async def post_scheduled_content(self) -> int:
        """Post all scheduled content that's due for auto-posting.

        Returns:
            Number of items posted
        """
        posted = 0

        async with async_session_maker() as session:
            content_repo = ContentQueueRepository(session)
            history_repo = PostHistoryRepository(session)

            due_items = await content_repo.get_due_for_posting()

            for item in due_items:
                try:
                    if item.content_type == "thread":
                        thread = Thread.from_storage(item.formatted_content)
                        tweet_ids = self.twitter.post_thread(
                            [t.content for t in thread.tweets]
                        )

                        if tweet_ids:
                            await history_repo.create(
                                tweet_id=tweet_ids[0],
                                content=item.formatted_content,
                                content_type="thread",
                            )
                            await content_repo.mark_posted(item.id)
                            posted += 1
                            logger.info("Auto-posted scheduled thread (%d tweets): %s", len(tweet_ids), item.topic)
                    else:
                        tweet_id = self.twitter.post_tweet(item.formatted_content)

                        if tweet_id:
                            await history_repo.create(
                                tweet_id=tweet_id,
                                content=item.formatted_content,
                                content_type=item.content_type,
                            )
                            await content_repo.mark_posted(item.id)
                            posted += 1
                            logger.info("Auto-posted scheduled content: %s", item.topic)

                except Exception as e:
                    logger.error("Failed to auto-post scheduled content %s: %s", item.id, e, exc_info=True)

            await session.commit()

        return posted

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
                            logger.info("Posted thread (%d tweets)", len(tweet_ids))
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
                            logger.info("Posted tweet: %s", tweet_id)

                except Exception as e:
                    logger.error("Failed to post content %s: %s", item.id, e, exc_info=True)

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
                        logger.info("Posted reply to @%s", item.mention_author)

                except Exception as e:
                    logger.error("Failed to post reply %s: %s", item.id, e, exc_info=True)

            await session.commit()

        return posted

    async def post_all(self) -> dict:
        """Post all approved content, scheduled content, and replies.

        Returns:
            Dictionary with counts of posted items
        """
        scheduled_count = await self.post_scheduled_content()
        content_count = await self.post_approved_content()
        reply_count = await self.post_approved_replies()

        return {
            "scheduled_posted": scheduled_count,
            "content_posted": content_count,
            "replies_posted": reply_count,
        }

    async def start_posting_loop(self, interval: int = 60) -> None:
        """Start the posting loop.

        Args:
            interval: Seconds between posting checks
        """
        self._running = True
        logger.info("Starting content poster (interval: %ds)", interval)

        while self._running:
            try:
                result = await self.post_all()
                total = result["scheduled_posted"] + result["content_posted"] + result["replies_posted"]
                if total > 0:
                    logger.info("Posted: %d scheduled, %d approved, %d replies", result['scheduled_posted'], result['content_posted'], result['replies_posted'])
            except Exception as e:
                logger.error("Error in posting loop: %s", e, exc_info=True)

            await asyncio.sleep(interval)

    def stop_posting(self) -> None:
        """Stop the posting loop."""
        self._running = False
        logger.info("Content poster stopped")
