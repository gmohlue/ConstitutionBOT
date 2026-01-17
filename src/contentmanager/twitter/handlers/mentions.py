"""Monitor Twitter mentions and create reply drafts."""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

from contentmanager.config import get_settings
from contentmanager.core.modes.user_provided import UserProvidedMode
from contentmanager.database import async_session_maker
from contentmanager.database.repositories.reply_queue import ReplyQueueRepository
from contentmanager.twitter.client import TwitterClient


class MentionMonitor:
    """Monitor Twitter mentions and queue replies for approval."""

    def __init__(self):
        self.settings = get_settings()
        self.twitter = TwitterClient()
        self._last_mention_id: Optional[str] = None
        self._running = False

    async def check_mentions(self) -> int:
        """Check for new mentions and queue replies.

        Returns:
            Number of new mentions processed
        """
        mentions = self.twitter.get_mentions(since_id=self._last_mention_id)

        if not mentions:
            return 0

        processed = 0

        async with async_session_maker() as session:
            repo = ReplyQueueRepository(session)
            mode = UserProvidedMode(session)

            for mention in mentions:
                # Check if we've already processed this mention
                if await repo.mention_exists(mention["id"]):
                    continue

                # Generate a reply draft
                try:
                    content = await mode.generate_reply(
                        mention_text=mention["text"],
                        mention_author=mention["author_username"],
                    )

                    # Add to reply queue
                    await repo.create(
                        mention_id=mention["id"],
                        mention_text=mention["text"],
                        mention_author=mention["author_username"],
                        mention_author_id=mention["author_id"],
                        draft_reply=content.formatted_content,
                    )

                    processed += 1
                    logger.info("Queued reply for @%s", mention['author_username'])

                except Exception as e:
                    logger.error("Failed to process mention %s: %s", mention['id'], e, exc_info=True)

            await session.commit()

        # Update last processed ID
        if mentions:
            self._last_mention_id = mentions[0]["id"]

        return processed

    async def start_monitoring(self) -> None:
        """Start the mention monitoring loop."""
        self._running = True
        logger.info("Starting mention monitor (interval: %ds)", self.settings.mention_check_interval)

        while self._running:
            try:
                count = await self.check_mentions()
                if count > 0:
                    logger.info("Processed %d new mentions", count)
            except Exception as e:
                logger.error("Error checking mentions: %s", e, exc_info=True)

            await asyncio.sleep(self.settings.mention_check_interval)

    def stop_monitoring(self) -> None:
        """Stop the mention monitoring loop."""
        self._running = False
        logger.info("Mention monitor stopped")
