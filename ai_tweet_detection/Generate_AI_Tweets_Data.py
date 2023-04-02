import pandas as pd
import openai
import re
import threading
import time
import numpy as np

# Read the csv file
df = pd.read_csv('./user_tweets.csv')
tweets = df.stack().dropna()
num_iters = 250

class AITweetGenerator(object):
    def __init__(self):
        openai.api_key = "YOUR_OPEN_AI_TOKEN"
        try:
            self.df = pd.read_csv('./ai_tweets.csv')
        except:
            self.df = pd.DataFrame(columns=['ai_tweet', 'human_tweet'])

    def generate_tweet(self, tweet):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": f"Identify the context of the tweet: {tweet},"
                            f"generate a tweet on the same context."
                 },
            ]

        )
        result = ''
        for choice in response.choices:
            result += choice.message.content
            result = result.lower()
            if 'tweet:' in result:
                result = result.split('tweet:')[1]
            result = re.sub(r'#[\w\d]+|https?://\S+', '', result)

        self.df = pd.concat([self.df, pd.DataFrame({'ai_tweet': [result], 'human_tweet':[tweet]})], ignore_index=True)

    def save_to_csv(self):
        self.df.to_csv('ai_tweets.csv', index=False)
        print("number of tweets generated till now ", len(self.df))

    def return_df(self):
        return self.df

    def generate_tweets_in_parallel(self, tweets):
        threads = []
        for tweet in tweets:
            thread = threading.Thread(target=self.generate_tweet, args=[tweet])
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

def clean_tweet(tweet):
    tweet_without_hashtags_and_links = re.sub(r'#[\w\d]+|https?://\S+', '', tweet)
    finalTweet = tweet_without_hashtags_and_links.replace('\n', '').replace('\r', '')
    finalTweet = finalTweet.lower()
    if len(finalTweet) > 50:
        return finalTweet
    else:
        return None

if __name__ == '__main__':
    i = 0
    ai_tweet_generator = AITweetGenerator()

    while i < num_iters:
        print("sleeping for 1.5 seconds, iteration ", i)
        time.sleep(2)

        try:
            random_tweets = np.random.choice(tweets, 1000)
            # Check for duplicates between clean tweets and df['human_tweets']
            df_ai_tweets = pd.read_csv('./ai_tweets.csv')
            human_tweets = set(df_ai_tweets['human_tweet'])
            random_tweets = [tweet for tweet in random_tweets if tweet not in human_tweets]
            if len(random_tweets) > 20:
                random_tweets = random_tweets[:20]
            cleaned_tweets = list(filter(None, [clean_tweet(tweet) for tweet in random_tweets]))
            ai_tweet_generator.generate_tweets_in_parallel(cleaned_tweets)
            ai_tweet_generator.save_to_csv()
            i += 1
        except Exception as e:
            continue

    # df_ai_tweets = ai_tweet_generator.return_df()
    # print(len(df_ai_tweets))
    # # drop duplicates with respect human_tweet
    # df_ai_tweets = df_ai_tweets.drop_duplicates(subset=['human_tweet'])
    # print(len(df_ai_tweets))
    # df_ai_tweets.to_csv('ai_tweets.csv', index=False)