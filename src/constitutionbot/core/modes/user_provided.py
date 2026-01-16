"""Mode 2: User-provided topics for content generation."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from constitutionbot.core.content.generator import ContentGenerator, GeneratedContent


class UserProvidedMode:
    """Mode 2: User provides topics for content generation.

    This mode is used when the admin specifies a topic they want
    to create content about. The bot then generates educational
    content based on that topic.

    Workflow:
    1. Admin provides a topic/question
    2. Bot finds relevant Constitution sections
    3. Generates content addressing the topic
    4. Content goes to queue for admin review
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.generator = ContentGenerator(session)

    async def generate_tweet(
        self,
        topic: str,
        section_nums: Optional[list[int]] = None,
    ) -> GeneratedContent:
        """Generate a tweet about a user-provided topic.

        Args:
            topic: The topic to create content about
            section_nums: Optional specific sections to reference

        Returns:
            GeneratedContent with the generated tweet
        """
        return await self.generator.generate_tweet(
            topic=topic,
            mode="user_provided",
            section_nums=section_nums,
        )

    async def generate_thread(
        self,
        topic: str,
        num_tweets: int = 5,
        section_nums: Optional[list[int]] = None,
    ) -> GeneratedContent:
        """Generate a thread about a user-provided topic.

        Args:
            topic: The topic to create content about
            num_tweets: Number of tweets in the thread
            section_nums: Optional specific sections to reference

        Returns:
            GeneratedContent with the generated thread
        """
        return await self.generator.generate_thread(
            topic=topic,
            num_tweets=num_tweets,
            mode="user_provided",
            section_nums=section_nums,
        )

    async def generate_script(
        self,
        topic: str,
        duration: str = "2-3 minutes",
        section_nums: Optional[list[int]] = None,
    ) -> GeneratedContent:
        """Generate a dialog script about a user-provided topic.

        Args:
            topic: The topic to create content about
            duration: Estimated duration of the script
            section_nums: Optional specific sections to reference

        Returns:
            GeneratedContent with the generated dialog script
        """
        return await self.generator.generate_script(
            topic=topic,
            mode="user_provided",
            section_nums=section_nums,
            duration=duration,
        )

    async def explain_section(
        self,
        section_num: int,
        content_type: str = "tweet",
    ) -> GeneratedContent:
        """Generate an explanation of a specific section.

        Args:
            section_num: The section number to explain
            content_type: "tweet" or "thread"

        Returns:
            GeneratedContent with the explanation
        """
        return await self.generator.explain_section(
            section_num=section_num,
            content_type=content_type,
        )

    async def generate_reply(
        self,
        mention_text: str,
        mention_author: str,
    ) -> GeneratedContent:
        """Generate a reply to a user mention.

        Args:
            mention_text: The text of the mention
            mention_author: Username of the person who mentioned

        Returns:
            GeneratedContent with the reply
        """
        return await self.generator.generate_reply(
            mention_text=mention_text,
            mention_author=mention_author,
        )

    async def regenerate_reply(
        self,
        mention_text: str,
        mention_author: str,
        previous_reply: str,
    ) -> GeneratedContent:
        """Regenerate a reply if the first one wasn't satisfactory.

        Args:
            mention_text: The text of the mention
            mention_author: Username of the person who mentioned
            previous_reply: The previous reply that needs improvement

        Returns:
            GeneratedContent with a new reply
        """
        # Add context about needing a different approach
        modified_mention = (
            f"{mention_text}\n\n"
            f"[Previous reply was: {previous_reply}. "
            f"Please generate a different, improved response.]"
        )

        return await self.generator.generate_reply(
            mention_text=modified_mention,
            mention_author=mention_author,
        )

    async def generate_comparison(
        self,
        topic1: str,
        topic2: str,
        content_type: str = "thread",
    ) -> GeneratedContent:
        """Generate content comparing two constitutional topics.

        Args:
            topic1: First topic to compare
            topic2: Second topic to compare
            content_type: "tweet" or "thread"

        Returns:
            GeneratedContent comparing the topics
        """
        comparison_topic = f"Comparing {topic1} and {topic2} in the SA Constitution"

        if content_type == "thread":
            return await self.generator.generate_thread(
                topic=comparison_topic,
                num_tweets=5,
                mode="user_provided",
            )
        else:
            return await self.generator.generate_tweet(
                topic=comparison_topic,
                mode="user_provided",
            )

    async def generate_faq_response(
        self,
        question: str,
    ) -> GeneratedContent:
        """Generate a response to a common FAQ about the Constitution.

        Args:
            question: The question to answer

        Returns:
            GeneratedContent with the answer
        """
        topic = f"FAQ: {question}"

        return await self.generator.generate_tweet(
            topic=topic,
            mode="user_provided",
        )
