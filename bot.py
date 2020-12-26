import os
import traceback
from datetime import datetime

import tweepy


def log(message):
    print("[{time}] {msg}".format(time=datetime.now(), msg=message))


# Below function could be used to make lookup requests for ids 100 at a time leading to 18K lookups in each 15 minute
# window
def get_usernames(user_id, api):
    full_users = []
    u_count = len(user_id)

    try:
        for i in range(int(u_count / 100) + 1):
            end_loc = min((i + 1) * 100, u_count)
            full_users.extend(api.lookup_users(user_ids=user_id[i * 100:end_loc]))
            return full_users
    except tweepy.TweepError:
        traceback.print_exc()
        log('Something went wrong, quitting...')


def split_data(ids, api):
    chunks = [ids[x:x + 100] for x in range(0, len(ids), 100)]
    all_users = []

    for data in chunks:
        all_users.extend(get_usernames(data, api))

    return all_users


# https://stackoverflow.com/a/58234314
def main():
    auth = tweepy.OAuthHandler(os.environ.get('key'), os.environ.get('secret'))
    auth.set_access_token(os.environ.get('token'), os.environ.get('token_secret'))

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    followers_ids = []

    # Below code will request for 5000 follower ids in one request and therefore will give 75K ids in every 15 minute
    # window (as 15 requests could be made in each window).
    for user in tweepy.Cursor(api.followers_ids, screen_name="maxdotbam", count=5000).items():
        followers_ids.append(user)

    log("Obtained " + str(len(followers_ids)) + " followers ids.... converting usernames")

    full_users = split_data(followers_ids, api)

    names = []

    for us in full_users:

        nick = us.screen_name

        if len(nick) <= 7:
            names.append(nick)

    fo = open("list.txt", "w")
    fo.write('\n'.join(names))
    fo.close()

    log("done")


main()
