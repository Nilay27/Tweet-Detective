from user_data import user_id_map
import tweepy
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd


# Twitter API credentials
bearer_token = 'YOUR_TWITTER_BEARER_TOKEN'
client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

# function to fetch tweets from user's timeline for past 1 month using user_id_map
def fetch_tweets_for_user_id(user_id):
    tweets = []
    now = datetime.datetime.now()
    start_time = str(now - relativedelta(months=11))
    start_time = (start_time[:-7]).replace(' ', 'T') + 'Z'
    end_time = str(now - relativedelta(hours=0))
    end_time = (end_time[:-7]).replace(' ', 'T') + 'Z'
    response = client.get_users_tweets(user_id, max_results=100, start_time=start_time,end_time=end_time, exclude="retweets,replies")
    if response.data is None:
        print("No tweets found for user_id: ", user_id)
        return tweets
    for data in response.data:
        tweets.append(data.text)
    print("Fetched ", len(tweets), " tweets for user_id: ", user_id)
    return tweets

# function to call fetch_tweets_for_user_id for all users in user_id_map and
# create a dictionary of user_id and list of tweets
def fetch_tweets_for_all_users():
    user_tweets = {}
    for (index, username) in enumerate(user_id_map):
        print(index, username)
        print("Fetching tweets for user_id: ", username)
        user_tweets[username] = fetch_tweets_for_user_id(user_id_map[username])
    return user_tweets

def get_user_tweets_as_df():
    user_tweets = fetch_tweets_for_all_users()
    user_tweets_df = pd.DataFrame.from_dict(user_tweets, orient='index').transpose()
    print(user_tweets_df.head(20))
    return user_tweets_df

def save_user_tweets_as_csv():
    user_tweets_df = get_user_tweets_as_df()
    user_tweets_df.to_csv('user_tweets.csv', index=True, header=True)

if __name__ == '__main__':
    save_user_tweets_as_csv()
