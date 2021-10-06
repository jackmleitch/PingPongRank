import tweepy
import pandas as pd
import config
import io


class connectTwitter:
    def __init__(self):
        self.auth = tweepy.OAuthHandler(
            config.TWITTER_KEYS["consumer_key"], config.TWITTER_KEYS["consumer_secret"]
        )
        self.auth.set_access_token(
            config.TWITTER_KEYS["access_token_key"],
            config.TWITTER_KEYS["access_token_secret"],
        )
        self.client = tweepy.API(self.auth)
        self.clientId = self.client.me().id

    def updateRankings(self, rankings):
        self.client.update_status(status=rankings)

    def fetchRankings(self):
        tweet = self.client.user_timeline(
            self.clientId, count=1, tweet_mode="extended"
        )[0]
        data = io.StringIO(tweet.full_text)
        df = pd.read_csv(data, sep=" ")
        return df

    def text(self):
        tweet = self.client.user_timeline(self.clientId, count=1)[0]
        data = tweet.text
        print(data)

    def fetchRankingsMulti(self):
        all_tweets = []
        tweets = self.client.user_timeline(
            count=200, include_rts=False, tweet_mode="extended"
        )
        all_tweets.extend(tweets)
        oldest_id = tweets[-1].id
        while True:
            tweets = self.client.user_timeline(
                count=200,
                include_rts=False,
                max_id=oldest_id - 1,
                tweet_mode="extended",
            )
            if len(tweets) == 0:
                break
            oldest_id = tweets[-1].id
            all_tweets.extend(tweets)
        count = len(all_tweets)
        print(f"{count} tweets found and downlaoded")
        return all_tweets, count


if __name__ == "__main__":
    # df = pd.read_csv(config.PLAYERS_FILEPATH, index_col=0)
    # textRankings = df.to_csv(sep=' ', index=True, header=True)
    twitter = connectTwitter()
    # twitter.updateRankings(textRankings)
    df = twitter.fetchRankings()
    print(df)
