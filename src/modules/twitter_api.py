import tweepy
import logging
from config import (
    TWITTER_API_KEY, 
    TWITTER_API_SECRET_KEY, 
    TWITTER_ACCESS_TOKEN, 
    TWITTER_ACCESS_TOKEN_SECRET
)

# Set up logging for error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_twitter_client():
    """
    Sets up and returns an authenticated Twitter API client using credentials from the config.
    """
    try:
        # Set up OAuth1 authentication using Tweepy
        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY, TWITTER_API_SECRET_KEY,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
        )
        
        # Create and return the API client
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        logger.info("Twitter API client successfully authenticated.")
        return api
    except Exception as e:
        logger.error(f"Error setting up Twitter API client: {e}")
        return None

# Function to fetch a tweet by its ID
def fetch_tweet(tweet_id):
    """
    Fetches a tweet by its tweet ID using the Twitter API.
    :param tweet_id: The ID of the tweet to fetch.
    :return: Tweet data as JSON, or None if there is an error.
    """
    api = setup_twitter_client()
    
    if not api:
        logger.error("Twitter API client setup failed. Cannot fetch tweet.")
        return None

    try:
        tweet = api.get_status(tweet_id, tweet_mode="extended")  # Get full text with 'extended' mode
        logger.info(f"Successfully fetched tweet ID: {tweet_id}")
        return tweet._json  # Return tweet data in JSON format
    except tweepy.errors.TweepyException as e:
        logger.error(f"Error fetching tweet {tweet_id}: {e}")
        return None

# Function to post a tweet
def post_tweet(status):
    """
    Posts a new tweet using the Twitter API.
    :param status: The text content of the tweet.
    :return: Response data from Twitter in JSON format, or None if there is an error.
    """
    api = setup_twitter_client()
    
    if not api:
        logger.error("Twitter API client setup failed. Cannot post tweet.")
        return None

    try:
        response = api.update_status(status=status)
        logger.info(f"Tweet successfully posted with ID: {response.id}")
        return response._json
    except tweepy.errors.TweepyException as e:
        logger.error(f"Error posting tweet: {e}")
        return None

# Example function to delete a tweet by its ID
def delete_tweet(tweet_id):
    """
    Deletes a tweet by its tweet ID using the Twitter API.
    :param tweet_id: The ID of the tweet to delete.
    :return: True if the tweet was successfully deleted, False otherwise.
    """
    api = setup_twitter_client()
    
    if not api:
        logger.error("Twitter API client setup failed. Cannot delete tweet.")
        return False

    try:
        api.destroy_status(tweet_id)
        logger.info(f"Tweet with ID {tweet_id} successfully deleted.")
        return True
    except tweepy.errors.TweepyException as e:
        logger.error(f"Error deleting tweet {tweet_id}: {e}")
        return False
