import openai
import numpy as np
import json
import tweepy
import datetime
from dateutil.relativedelta import relativedelta

class TestModel(object):
    def __init__(self):
        openai.api_key = "YOUR_OPEN_AI_TOKEN"
        self.ft_model = "ada:ft-personal-2023-03-28-17-52-51"
        self.bearer_token = 'YOUR_TWITTER_BEARER_TOKEN'
        self.client = tweepy.Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)

    def call_model(self, prompt, expected_output):
        print("prompt to model", prompt)
        response = openai.Completion.create(
            engine=self.ft_model,
            prompt=prompt,
            max_tokens=1,
            frequency_penalty=0,
            presence_penalty=0.6,
        )
        print("response from model", response['choices'][0]['text'])
        print(expected_output)

    def test_model_from_validation(self):
        validations_json_data = (open("anomalous_data_prepared_valid.jsonl").read()).splitlines()
        random_prompt = validations_json_data[np.random.randint(0, len(validations_json_data))]
        # convert random_prompt to dict
        random_prompt_dict = json.loads(random_prompt)
        self.call_model(random_prompt_dict['prompt'], random_prompt_dict['completion'])

    def get_user_tweets(self, user_id):
        tweets = []
        now = datetime.datetime.now()
        start_time = str(now - relativedelta(months=12))
        start_time = (start_time[:-7]).replace(' ', 'T') + 'Z'
        end_time = str(now - relativedelta(months=3))
        end_time = (end_time[:-7]).replace(' ', 'T') + 'Z'
        response = self.client.get_users_tweets(user_id, max_results=100, start_time=start_time,end_time=end_time, exclude=["retweets","replies"])
        if response.data is None:
            print("No tweets found for user_id: ", user_id)
            return tweets
        for data in response.data:
            tweets.append(data.text)
        return tweets

    def get_user_id_from_username(self, username):
        user_id = self.client.get_user(username=username)
        return user_id.data.id

    def create_positive_prompt(self, tweets):
        prompt = ""
        random_tweets = np.random.choice(tweets, 6, replace=False)
        for index, tweet in enumerate(random_tweets):
            prompt += "tweet" + str(index+1) + ": " + tweet + ", "
        return prompt + " -> "

    def create_negative_prompt(self, tweet1, other_tweets):
        prompt = ""
        random_tweets = np.random.choice(other_tweets, 5, replace=False)
        prompt += "tweet" + str(1) + ": " + tweet1 + ", "
        for index, tweet in enumerate(random_tweets):
            prompt += "tweet" + str(index+2) + ": " + tweet + ", "
        return prompt + " -> "

    #{"prompt":"tweet1: @CryptoTraveler1 This photo may be 1991 or 1992 ish.
    # The computer should have been bought in 1990., tweet2: @EthereanMaximus i think what may surprise
    # you is how much value the tools can add, *today*\n\nversus how little value is added by offshoring
    # the tasks\n\ni understand hype cycles well. i also think some are massively underestimating AI because
    # they think they understand where we are on a hype chart,tweet3: @KristyGlas i think the reality is not
    # everyone can be successful in every endeavor\n\nluck plays a factor, but so does understanding the
    # environment\n\ni think artists who create solely for the sake of creation don't care, but many others seek
    # engagement. some seek validation, tweet4: it will probably be 2-3 years before most workplaces REALLY start
    # integrating AI, getting models trained up on their own datasets, etc.\n\nbut the revolution could happen MUCH
    # faster\n\nyou know what you need to do to survive, and thrive... 🤖, tweet5: @peter_szilagyi i only hope other AI
    # developers\/providers catch up with GPT so that we have alternatives which are not as adulterated,
    # tweet6: @JoshBobrowsky when you factor in social upheaval, possibly\n\nbut i think some jobs will be \"stealth\"
    # replaced much more quickly\n\ni also think humans can innovate ahead of it and use it as a tool for a while,
    # but not everyone, -> ","completion":" 0"}


    def test_model_on_random_users(self, username1, username2):
        print(username1, self.get_user_id_from_username(username1))
        print(username2, self.get_user_id_from_username(username2))
        user1_tweets = self.get_user_tweets(self.get_user_id_from_username(username1))
        user2_tweets = self.get_user_tweets(self.get_user_id_from_username(username2))
        user1_prompt = self.create_positive_prompt(user1_tweets)
        user2_prompt = self.create_positive_prompt(user2_tweets)
        negative_user1_prompt = self.create_negative_prompt(user1_tweets[np.random.randint(0, len(user1_tweets))],
                                                            user2_tweets)
        self.call_model(negative_user1_prompt, " 1")


if __name__ == '__main__':
    test_model = TestModel()
    test_model.test_model_on_random_users("zishansami102","kr_nilay27")
    # test_model.test_model_from_validation()