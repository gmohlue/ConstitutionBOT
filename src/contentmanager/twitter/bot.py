"""Main bot runner that coordinates all Twitter operations."""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

from contentmanager.config import get_settings
from contentmanager.core.modes.bot_proposed import BotProposedMode
from contentmanager.database import async_session_maker, init_db
from contentmanager.database.repositories.content_queue import ContentQueueRepository
from contentmanager.twitter.client import TwitterClient
from contentmanager.twitter.handlers.mentions import MentionMonitor
from contentmanager.twitter.handlers.poster import ContentPoster


class ContentManagerBot:
    """Main bot class that runs all Twitter operations."""

    def __init__(self):
        self.settings = get_settings()
        self.twitter = TwitterClient()
        self.mention_monitor = MentionMonitor()
        self.content_poster = ContentPoster()
        self._running = False
        self._auto_generate_task: Optional[asyncio.Task] = None

    async def initialize(self) -> bool:
        """Initialize the bot.

        Returns:
            True if initialization successful, False otherwise
        """
        # Initialize database
        await init_db()

        # Verify Twitter credentials
        if not self.twitter.verify_credentials():
            print("ERROR: Twitter credentials invalid or not configured")
            return False

        me = self.twitter.get_me()
        if me:
            print(f"Logged in as @{me['username']}")

        return True

    async def auto_generate_content(self) -> None:
        """Auto-generate content at regular intervals."""
        print(f"Starting auto-generate (interval: {self.settings.auto_generate_interval}s)")

        while self._running and self.settings.auto_generate_enabled:
            try:
                async with async_session_maker() as session:
                    mode = BotProposedMode(session)
                    result = await mode.suggest_and_generate(content_type="tweet")

                    # Add to queue
                    repo = ContentQueueRepository(session)
                    await repo.create(
                        raw_content=result.content.raw_content,
                        formatted_content=result.content.formatted_content,
                        content_type=result.content.content_type,
                        mode="bot_proposed",
                        topic=result.content.topic,
                        citations=result.content.citations,
                    )
                    await session.commit()

                    logger.info("Auto-generated content: %s", result.suggestion.topic)

            except Exception as e:
                logger.error("Error in auto-generate: %s", e, exc_info=True)

            await asyncio.sleep(self.settings.auto_generate_interval)

    async def run(self) -> None:
        """Run the bot."""
        if not await self.initialize():
            return

        self._running = True
        logger.info("Content Manager starting...")

        tasks = []

        # Start mention monitoring
        if self.settings.bot_enabled:
            tasks.append(
                asyncio.create_task(self.mention_monitor.start_monitoring())
            )
            tasks.append(
                asyncio.create_task(self.content_poster.start_posting_loop())
            )

        # Start auto-generate if enabled
        if self.settings.auto_generate_enabled:
            self._auto_generate_task = asyncio.create_task(self.auto_generate_content())
            tasks.append(self._auto_generate_task)

        if not tasks:
            print("No tasks enabled. Set BOT_ENABLED=true or AUTO_GENERATE_ENABLED=true in .env")
            return

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the bot."""
        self._running = False
        self.mention_monitor.stop_monitoring()
        self.content_poster.stop_posting()

        if self._auto_generate_task:
            self._auto_generate_task.cancel()

        print("Content Manager stopped")


async def run_bot():
    """Entry point for running the bot."""
    bot = ContentManagerBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        bot.stop()
