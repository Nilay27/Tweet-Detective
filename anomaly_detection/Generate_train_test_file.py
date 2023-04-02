import pandas as pd
import numpy as np
import json

# Read the csv file
df = pd.read_csv('user_tweets.csv')
print(df[df.columns[1]])
num_iters = 50000

def generate_anomalous_data():
    data_df = pd.DataFrame()
    i = 1
    while i <= num_iters:
        tweet1_column = np.random.choice(df.columns)
        tweet1_column_values = df[tweet1_column].dropna().tolist()
        if len(tweet1_column_values) < 1:
            continue
        tweet2_to_6_column = np.random.choice(df.columns)
        tweet2_to_6_values = df[tweet2_to_6_column].dropna().tolist()
        if len(tweet2_to_6_values) < 5:
            continue
        print(f"{i} tweet1_column: ", tweet1_column)
        print(f"{i} tweet2_to_6_column: ", tweet2_to_6_column)

        random_tweet1 = tweet1_column_values[np.random.randint(0, len(tweet1_column_values))]
        random_tweet2_to_6 = np.random.choice(tweet2_to_6_values, 5)
        prompt = f"tweet1: {random_tweet1}, " \
               f"tweet2: {random_tweet2_to_6[0]}," \
               f"tweet3: {random_tweet2_to_6[1]}, " \
               f"tweet4: {random_tweet2_to_6[2]}, " \
               f"tweet5: {random_tweet2_to_6[3]}, " \
               f"tweet6: {random_tweet2_to_6[4]}, -> "
        completion = "0"
        data_df = pd.concat([data_df, pd.DataFrame({'prompt': [prompt], 'completion': [completion]})], ignore_index=True)
        i = i + 1
    i = 1
    while i <= num_iters:
        same_person_tweet_column = np.random.choice(df.columns)
        same_person_tweet_column_values = df[same_person_tweet_column].dropna().tolist()
        if len(same_person_tweet_column_values) < 6:
            continue
        random_tweets_by_same_person = np.random.choice(same_person_tweet_column_values, 6)
        prompt = f"tweet1: {random_tweets_by_same_person[0]}, " \
                    f"tweet2: {random_tweets_by_same_person[1]}," \
                    f"tweet3: {random_tweets_by_same_person[2]}, " \
                    f"tweet4: {random_tweets_by_same_person[3]}, " \
                    f"tweet5: {random_tweets_by_same_person[4]}, " \
                    f"tweet6: {random_tweets_by_same_person[5]}, -> "
        completion = "1"
        data_df = pd.concat([data_df, pd.DataFrame({'prompt': [prompt], 'completion': [completion]})], ignore_index=True)
        i = i + 1
    data_df.to_csv('anomalous_data.csv', index=False, header=True)



if __name__ == '__main__':
    generate_anomalous_data()
