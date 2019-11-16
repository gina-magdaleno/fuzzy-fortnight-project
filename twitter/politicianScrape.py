import tweepy
from config import tw_key, tw_secret
import pandas as pd
import json
auth = tweepy.AppAuthHandler(tw_key, tw_secret)
api = tweepy.API(auth)
politician_ids = []
with open("data/politicians_list", "r") as f:
    for line in f:
        politician_ids.append(line.strip())

has_data = []
try:
    with open("data/politicians_has_data","r") as f:
        for line in f:
            has_data.append(line.strip())
except:
    has_data = []
json_data_file = "data/pol_json_data"

def politician_scrape(pol_id):
    from math import ceil
    from time import sleep
    from datetime import datetime
    try:
        pol = api.get_user(id=pol_id)
    except:
        return None
    num_mins = ceil(max(pol.followers_count, pol.friends_count)/5000)
    num_mins_fol = ceil(pol.followers_count/5000)
    num_mins_fr = ceil(pol.friends_count/5000)
    k = 0
    statuses = []
    followers = []
    friends=[]
    fol_cur = tweepy.Cursor(api.followers_ids,id=pol.id_str, count=5000).pages()
    fr_cur = tweepy.Cursor(api.friends_ids,id=pol.id_str, count = 5000).pages()
    try:
        stat = pol.user_timeline(tweet_mode="extended", count=200)
        for t in stat:
            t.pop('user')
    except:
        stat = []
    while k < num_mins:
        try:
            if k < num_mins_fr:
                friends += next(fr_cur)
            if k < num_mins_fol:
                followers += next(fol_cur)
            k += 1
            if k < num_mins:
                sleep(60)
        except:
            sleep(60)

    out = {
        'id':pol.id,
        'id_str':pol.id_str,
        'name':pol.name,
        'screen_name':pol.screen_name,
        'location':pol.location,
        'description':pol.description,
        'friends_count':pol.friends_count,
        'followers_count':pol.followers_count,
        'created_at':pol.created_at.strftime("%Y/%m/%d"),
        'friends_ids':friends,
        'followers_ids':followers,
        'statuses':stat
    }
    return out

for id in politician_ids:
    if id in has_data:
        continue
    next_pol = politician_scrape(id)
    if next_pol:
        has_data.append(next_pol["id_str"])
        print(next_pol["id_str"]+'\n')
        with open(json_data_file, "a") as f:
            json.dump(next_pol, f)
            f.write('\n')
