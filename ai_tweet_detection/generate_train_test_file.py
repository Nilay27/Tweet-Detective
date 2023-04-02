import pandas as pd
import re

# Read the csv file
df = pd.read_csv('ai_tweets.csv')
print(df.head())

def generate_train_test_file():
    data_df = pd.DataFrame()
    for index, row in df.iterrows():
        prompt = row['human_tweet']
        data_df = pd.concat([data_df, pd.DataFrame({'prompt': [prompt + ' -> '], 'completion': [1]})],
                            ignore_index=True)
        prompt = row['ai_tweet']
        data_df = pd.concat([data_df, pd.DataFrame({'prompt': [prompt + ' -> '], 'completion': [0]})],
                            ignore_index=True)
    data_df.to_csv('tweet_data.csv', index=False, header=True)

def clean_tweets(tweet):
    tweet_without_hashtags_and_links = re.sub(r'#[\w\d]+|https?://\S+', '', tweet)
    finalTweet = tweet_without_hashtags_and_links.replace('\n', '').replace('\r', '')
    finalTweet = finalTweet.lower()
    if len(finalTweet) > 100:
        return finalTweet
    else:
        return None


if __name__ == '__main__':
    df = pd.read_csv('tweet_data.csv')
    df['prompt'] = df['prompt'].apply(clean_tweets)
    df = df.dropna()
    counts = df['completion'].value_counts()
    min_count = counts.min()
    human = df[df['completion'] == 0].sample(min_count)
    ai = df[df['completion'] == 1].sample(min_count)
    df = pd.concat([human, ai], ignore_index=True)
    df.to_csv('tweet_data.csv', index=False)
