import tweepy
import urllib
import re
import feedparser
import datetime
from util import *
import os
import helpers
import xml.etree.ElementTree as ET
import account
import random
from mega_util import MegaUtil

master_account = ""
accounts_list = []
api = None
m = None

def post_media(uname, lst):
    not_posted = True

    while not_posted:
        media_tweets = api.list_timeline(uname, lst.replace("_", "-"), count=100, include_rts=False)
        random.shuffle(media_tweets)
        media_tweet_object = None
        for tweet in media_tweets:
            if not tweet.retweeted and 'RT @' not in tweet.text:
                media_tweet_object = tweet
                break

        media_tweet_text = media_tweet_object.text
        media_tweet_has_media = hasattr(media_tweet_object, 'extended_entities')
        if media_tweet_has_media:
            media_tweet_media_object = media_tweet_object.extended_entities['media'][0]
            if 'video_info' in media_tweet_media_object:
                variant = None
                for v in media_tweet_media_object['video_info']['variants']:
                    if (v['content_type'] == 'video/mp4'):
                        variant = v
                        break
                if not os.path.exists("dwnld/"):
                    os.makedirs("dwnld/")
                urllib.request.urlretrieve(variant['url'], "dwnld/media.mp4")
                video = api.upload_chunked("dwnld/media.mp4", media_category="tweet_video")
                media_tweet_text = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', media_tweet_text)
                media_tweet_text = re.sub("&amp;", '&', media_tweet_text)
                try:
                    api.update_status(status=media_tweet_text, media_ids=[video.media_id])
                    print("Successfully tweeted with vid!")
                    not_posted = False
                except:
                    print("Duplicate tweet...")
            else:
                media_tweet_text = re.sub("&amp;", '&', media_tweet_text)
                try:
                    api.update_status(status=media_tweet_text)
                    print("Successfully tweeted with pic!")
                    not_posted = False
                except:
                    print("Duplicate tweet...")
        else:
            print("Tweet didn't have any media...")

def post_hiphop():
    now = datetime.datetime.now()
    m = now.month
    d = now.day

    print("Month: " , m)
    print("Day: " , d)

    feed = feedparser.parse('http://todayinhiphophistory.tumblr.com/rss')

    entries = []

    for e in feed.entries:
        mm = e.published_parsed.tm_mon
        dd = e.published_parsed.tm_mday
        if mm == m and dd == d:
            entries.append(e)

    for e in entries:
        txt = strip_tags(e.summary_detail.value)
        txt = txt.replace(":", ": ")
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', e.summary)
        urllib.request.urlretrieve(urls[0], "dwnld/hh.jpg")
        api.update_with_media(filename="dwnld/hh.jpg", status=txt)
        print(txt)
        print(urls[0])

def promo(uname):
    tweets = api.user_timeline(screen_name=uname, count=25, include_rts=False)
    f = r = 0
    for t in tweets:
        ff = rr = False
        try:
            api.create_favorite(t.id)
            f += 1
            ff = True
        except:
            pass

        try:
            api.retweet(t.id)
            r += 1
            rr = True
        except:
            pass

        if ff or rr:
            s = ""
            if ff:
                s = "Favorite"
            if rr:
                if ff:
                    s += " + Retweet"
                else:
                    s = "Retweet"

            print("Performed: " + s)
            if t is not tweets[-1]: helpers.rand_sleep(30, 90)

    if f > 0 and r > 0:
        print("Successfully liked(" + str(f) + ") and retweeted(" + str(r) + ")!")
    else:
        print("No new tweets to like and retweet...")

def retweet(uname, lst):
    accnts = api.list_members(uname, lst.replace("_", "-"))
    tweets = api.user_timeline(screen_name=random.choice(accnts).screen_name, count=25, include_rts=False)
    api.retweet(random.choice(tweets).id)
    print("Successfully retweeted!")

def post_local_media():
    links_list = []
    with open("links.txt") as f:
        links_list = f.readlines()

    if not os.path.exists("tmp/"):
        os.makedirs("tmp/")

    links_list = []
    with open("links.txt") as f:
        links_list = f.readlines()

    tmpFolder = os.path.join(os.getcwd(), "tmp")
    chrome_driver=r"C:\chromedriver\chromedriver.exe"

    if 'DYNO' in os.environ:
        chrome_driver = CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"

    for retry in range(5):
        try:
            MegaUtil.direct_download(random.choice(links_list), tmpFolder, chrome_driver)
            break
        except:
            print("Failed to make webdriver, trying again in 1 minute..")
            helpers.rand_sleep(10,15)

    #
    # accnts = api.list_members(uname, lst)
    # random.shuffle(accnts)
    # txt = msg.replace("<L>", random.choice(lnks))
    # for i in range(0, n):
    #     txt += " @" + accnts[i].screen_name

    arr = os.listdir("tmp")
    img = "tmp/" + arr[0]

    api.update_with_media(filename=img, status="")
    print("Successfully tweeted with local media!")

    for a in arr:
        os.remove("tmp/" + a)

def run_account_tasks(acc):
    auth = tweepy.OAuthHandler(acc.consumer_key, acc.consumer_secret)
    auth.set_access_token(acc.access_token, acc.access_token_secret)

    global api
    api = tweepy.API(auth)

    now = datetime.datetime.now()

    tasks = acc.tasks.get()
    tsks = tasks[now.hour]

    print("Tasklist: " + str(tsks))

    for t in tsks:
        num = 1

        if len(t) > 1:
            num = int(t[1:])
            t = t[0]

        for i in range(num):
            if t == 'm':
                post_media(account.master_account, acc.handle)
            elif t == 'h':
                post_hiphop()
            elif t == 'l':
                post_local_media()
            elif t == 'p':
                promo(account.master_account)
            elif t == 'r':
                retweet(account.master_account, acc.handle+"RT")
            else:
                print("WTF???")
            if(t is not tsks[-1]):
                helpers.rand_sleep(30, 90)

with open("data/config.xml") as f:
    e = ET.fromstringlist(["<root>", f.read(), "</root>"])
    account.set_master(e.find("master_account").text)
with open("data/accounts.xml") as f:
    e = ET.fromstringlist(["<root>", f.read(), "</root>"])
    for acc in e.findall("account"):
        a = account.Account(xml=acc)
        accounts_list.append(a)
with open("data/tasks.xml") as f:
    e = ET.fromstringlist(["<root>", f.read(), "</root>"])
    for acc in e.findall("account"):
        a = next((x for x in accounts_list if x.id == acc.get("id")), None)
        if a is not None:
            a.add_tasks(xml=acc)
        else:
            print("not found")

random.shuffle(accounts_list)

for a in accounts_list:
    print("---Running Tasks For: @" + a.handle)
    run_account_tasks(a)