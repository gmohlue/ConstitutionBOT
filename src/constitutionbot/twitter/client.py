"""Twitter API client wrapper using Tweepy."""

from typing import Optional

import tweepy

from constitutionbot.config import get_settings


class TwitterClient:
    """Wrapper for Twitter API v2 using Tweepy."""

    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[tweepy.Client] = None
        self._api: Optional[tweepy.API] = None

    @property
    def client(self) -> tweepy.Client:
        """Get or create the Tweepy v2 client."""
        if self._client is None:
            self._client = tweepy.Client(
                bearer_token=self.settings.twitter_bearer_token.get_secret_value() or None,
                consumer_key=self.settings.twitter_api_key.get_secret_value(),
                consumer_secret=self.settings.twitter_api_secret.get_secret_value(),
                access_token=self.settings.twitter_access_token.get_secret_value(),
                access_token_secret=self.settings.twitter_access_secret.get_secret_value(),
                wait_on_rate_limit=True,
            )
        return self._client

    @property
    def api(self) -> tweepy.API:
        """Get or create the Tweepy v1.1 API (for some operations)."""
        if self._api is None:
            auth = tweepy.OAuth1UserHandler(
                self.settings.twitter_api_key.get_secret_value(),
                self.settings.twitter_api_secret.get_secret_value(),
                self.settings.twitter_access_token.get_secret_value(),
                self.settings.twitter_access_secret.get_secret_value(),
            )
            self._api = tweepy.API(auth, wait_on_rate_limit=True)
        return self._api

    def verify_credentials(self) -> bool:
        """Verify that Twitter credentials are valid."""
        try:
            me = self.client.get_me()
            return me is not None and me.data is not None
        except Exception:
            return False

    def get_me(self) -> Optional[dict]:
        """Get the authenticated user's information."""
        try:
            response = self.client.get_me(
                user_fields=["name", "username", "description", "public_metrics"]
            )
            if response.data:
                return {
                    "id": response.data.id,
                    "name": response.data.name,
                    "username": response.data.username,
                }
            return None
        except Exception:
            return None

    def post_tweet(self, text: str, reply_to_id: Optional[str] = None) -> Optional[str]:
        """Post a tweet.

        Args:
            text: The tweet text (max 280 characters)
            reply_to_id: Optional tweet ID to reply to

        Returns:
            The tweet ID if successful, None otherwise
        """
        try:
            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=reply_to_id,
            )
            if response.data:
                return str(response.data["id"])
            return None
        except Exception as e:
            print(f"Failed to post tweet: {e}")
            return None

    def post_thread(self, tweets: list[str]) -> list[str]:
        """Post a thread of tweets.

        Args:
            tweets: List of tweet texts

        Returns:
            List of tweet IDs for successfully posted tweets
        """
        tweet_ids = []
        reply_to_id = None

        for tweet_text in tweets:
            tweet_id = self.post_tweet(tweet_text, reply_to_id=reply_to_id)
            if tweet_id:
                tweet_ids.append(tweet_id)
                reply_to_id = tweet_id
            else:
                # Stop if a tweet fails
                break

        return tweet_ids

    def get_mentions(
        self, since_id: Optional[str] = None, max_results: int = 100
    ) -> list[dict]:
        """Get recent mentions of the authenticated user.

        Args:
            since_id: Only return mentions newer than this ID
            max_results: Maximum number of mentions to return

        Returns:
            List of mention dictionaries
        """
        try:
            me = self.client.get_me()
            if not me or not me.data:
                return []

            response = self.client.get_users_mentions(
                id=me.data.id,
                since_id=since_id,
                max_results=max_results,
                tweet_fields=["created_at", "author_id", "conversation_id"],
                expansions=["author_id"],
            )

            if not response.data:
                return []

            # Build author lookup
            authors = {}
            if response.includes and "users" in response.includes:
                for user in response.includes["users"]:
                    authors[user.id] = user.username

            mentions = []
            for tweet in response.data:
                mentions.append({
                    "id": str(tweet.id),
                    "text": tweet.text,
                    "author_id": str(tweet.author_id),
                    "author_username": authors.get(tweet.author_id, "unknown"),
                    "created_at": tweet.created_at,
                    "conversation_id": str(tweet.conversation_id) if tweet.conversation_id else None,
                })

            return mentions

        except Exception as e:
            print(f"Failed to get mentions: {e}")
            return []

    def get_tweet_engagement(self, tweet_id: str) -> Optional[dict]:
        """Get engagement metrics for a tweet.

        Args:
            tweet_id: The tweet ID

        Returns:
            Dictionary with engagement metrics
        """
        try:
            response = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=["public_metrics"],
            )

            if response.data and response.data.public_metrics:
                metrics = response.data.public_metrics
                return {
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "quotes": metrics.get("quote_count", 0),
                }
            return None

        except Exception as e:
            print(f"Failed to get engagement: {e}")
            return None

    def delete_tweet(self, tweet_id: str) -> bool:
        """Delete a tweet.

        Args:
            tweet_id: The tweet ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.client.delete_tweet(id=tweet_id)
            return response.data.get("deleted", False)
        except Exception as e:
            print(f"Failed to delete tweet: {e}")
            return False
