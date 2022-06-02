import asyncio
import json
import logging
import os
import re
import time

import aiohttp
import feedparser
import requests
import tweepy
from apiclient.discovery import build
from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.db.utils import IntegrityError
from django.http import HttpResponse
from pyppeteer.browser import Browser
from pyppeteer.launcher import launch
from pyppeteer.page import Page

from .account_validator import *
from .models import *

# Necessary to load data from DB
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

logger = logging.getLogger(__name__)

from django.conf import settings

YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
YOUTUBE_API_SERVICE_NAME = settings.YOUTUBE_API_SERVICE_NAME
YOUTUBE_API_VERSION = settings.YOUTUBE_API_VERSION
YOUTUBE_CHANNEL_ID = settings.YOUTUBE_CHANNEL_ID

CONNPASS_LOGIN_USERNAME = settings.CONNPASS_LOGIN_USERNAME
CONNPASS_LOGIN_PASSWORD = settings.CONNPASS_LOGIN_PASSWORD

TWITTER_CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET = settings.TWITTER_CONSUMER_SECRET
TWITTER_ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET = settings.TWITTER_ACCESS_TOKEN_SECRET

SLACK_WEBHOOK_URL = settings.SLACK_WEBHOOK_URL
SLACK_MENTION_ADDRESS = settings.SLACK_MENTION_ADDRESS


def index(request):
    return HttpResponse("ok")


async def get_connpass_member_async():
    async with aiohttp.ClientSession() as session:
        communities = Community.objects.all()
        for community in communities:
            async with session.get(community.url) as resp:
                source = await resp.text()
                soup = BeautifulSoup(source, 'html5lib')
                list_amount = soup.find_all('span', {'class': "amount"})
                logger.debug(str(list_amount[len(list_amount) - 1].get_text()))
                try:
                    DailyCommunityMember(community_id=community,
                                         member_count=list_amount[len(list_amount) - 1].get_text()).save()
                except IntegrityError:
                    logger.warning('Already Exists.')


async def connpass_member(request):
    loop = asyncio.get_event_loop()
    loop.create_task(get_connpass_member_async())

    return HttpResponse("ok")


def get_youtube_subscriber():
    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=YOUTUBE_API_KEY,
        cache_discovery=False
    )

    response = youtube.search().list(
        part="snippet",
        channelId=YOUTUBE_CHANNEL_ID,
        maxResults=1,
        order="date"
    ).execute()

    for item in response.get("items", []):
        if item["id"]["kind"] != "youtube#video":
            continue

    logger.debug(json.dumps(item, indent=2, ensure_ascii=False))

    channel_id = response['items'][0]['snippet']['channelId']

    res2 = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    ).execute()

    logger.debug(res2['items'][0]['statistics']['subscriberCount'])

    DailyYoutubeSubscriber(member_count=int(res2['items'][0]['statistics']['subscriberCount'])).save()


async def youtube_subscriber(request):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, get_youtube_subscriber)

    return HttpResponse("ok")


async def get_connpass_registration_async():
    # Can confirm real behavior with GUI
    # browser: Browser = await launch(headless=False)
    browser: Browser = await launch()

    try:
        page: Page = await browser.newPage()

        yesterday = datetime.date.today() - datetime.timedelta(days=1)

        await page.goto('https://connpass.com/login/')
        await page.type('input[name="username"]', CONNPASS_LOGIN_USERNAME)
        await page.type('input[name="password"]', CONNPASS_LOGIN_PASSWORD)
        login_btn = await page.querySelector("#login_form > p:nth-child(6) > button")
        await asyncio.gather(login_btn.click(), page.waitForNavigation())

        events = Event.objects.filter(date__range=[yesterday, yesterday + datetime.timedelta(days=365)])
        for event in events:
            url = 'https://connpass.com/event/%s/stats/' % (event.event_id)
            logger.debug(url)

            await asyncio.wait([page.goto(url), page.waitForNavigation()])
            await page.waitFor(1000)
            stat_page_content = await page.content()

            soup = BeautifulSoup(stat_page_content, 'html5lib')
            pv = soup.find('p', {'class': "PageviewsHero"})
            logger.debug(pv.get_text())
            unique = soup.find('p', {'class': "VisitorsHero"})
            logger.debug(unique.get_text())
            attendee = soup.find('p', {'class': "ParticipationsHero"})
            logger.debug(attendee.get_text())

            event.view = int(pv.get_text())
            event.unique = int(unique.get_text())
            event.attendee = int(attendee.get_text())
            event.save()

        finished_events = Event.objects.filter(date__range=[yesterday - datetime.timedelta(days=5), yesterday],
                                               first_visitor=-1)

        if len(finished_events) > 0:

            member_all = ConnpassMember.objects.all()

            for finished_event in finished_events:
                logger.debug(finished_event.name)

                url = finished_event.url + "participation/"
                await asyncio.wait([page.goto(url), page.waitForNavigation()])
                await page.waitFor(1000)

                all_member_url_a_tag = []
                see_more_link = await page.querySelector(
                    "#main > div.applicant_area > div.participation_table_area.mb_20 > table > tbody > tr.empty > td > a")
                if see_more_link == None:
                    logger.debug("less than 100 applicants")
                    stat_page_content = await page.content()
                    soup = BeautifulSoup(stat_page_content, 'html5lib')
                    all_member_url_a_tag = soup.find_all('a', attrs={"class": "image_link",
                                                                     'href': re.compile('^https://connpass.com/user/')})
                else:
                    logger.debug("more than 100 applicants")

                    see_more_link_text = await page.evaluate('(see_more_link) => see_more_link.getAttribute("href")',
                                                             see_more_link)

                    count_attendee_span = await page.querySelector(
                        "#main > div.applicant_area > div.participation_table_area.mb_20 > table > thead > tr > th > span.participants_count")
                    count_attendee = await page.evaluate('(count_attendee_span) => count_attendee_span.textContent',
                                                         count_attendee_span)

                    for i in range(1, int(int(str(count_attendee).split("人")[0]) / 100) + 1 + 1):
                        url = see_more_link_text + "?page=" + str(i)
                        logger.debug(url)

                        await asyncio.wait([page.goto(url), page.waitForNavigation()])
                        await page.waitFor(1000)
                        stat_page_content = await page.content()
                        soup = BeautifulSoup(stat_page_content, 'html5lib')
                        all_member_url_a_tag.extend(soup.find_all('a', attrs={"class": "image_link",
                                                                              'href': re.compile(
                                                                                  '^https://connpass.com/user/')}))

                count_new_member = 0
                for event_member_profile_url_a_tag in all_member_url_a_tag:
                    exists = False
                    for member in member_all:
                        if member.profile_url == event_member_profile_url_a_tag['href'].replace('/open/',
                                                                                                '/') and member.community_id == finished_event.community_id:
                            exists = True
                            break

                    if exists is False:
                        logger.debug("new member")
                        count_new_member += 1

                        ConnpassMember(community_id_id=finished_event.community_id_id,
                                       profile_url=event_member_profile_url_a_tag['href'].replace('/open/', '/')).save()

                finished_event.first_visitor = count_new_member
                finished_event.save()


    finally:
        await browser.close()

    return HttpResponse("ok")


async def connpass_registration(request):
    loop = asyncio.get_event_loop()
    loop.create_task(get_connpass_registration_async())

    return HttpResponse("ok")


def get_tweet():
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    twitter_tags = TwitterTag.objects.all()
    query_tags = []
    for tag in twitter_tags:
        query_tags.append(tag.name)

    query = ' OR '.join(query_tags)

    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    for tweet in tweepy.Cursor(api.search, q=query, count=200,
                               lang="ja",
                               since=str(yesterday)).items():
        for hashtag in tweet.entities['hashtags']:
            if '#' + hashtag['text'].upper() in query_tags:
                logger.debug(tweet.text)

                try:
                    tag_instance = TwitterTag.objects.get(
                        name='#' + hashtag['text'].upper())
                    text = 'https://twitter.com/%s/status/%s' % (tweet.user.screen_name, tweet.id_str)
                    logger.debug(text)
                    TwitterPost(name=text,
                                url=tweet.id_str, tag_id=tag_instance, user_id=tweet.user.screen_name,
                                follower_count=tweet.user.followers_count).save()
                except IntegrityError:
                    logger.warning("Already exists")

    return HttpResponse("ok")


async def tweet(request):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, get_tweet)

    return HttpResponse("ok")


async def get_qiita_post_async():
    async with aiohttp.ClientSession() as session:

        # overwrite lgtm count for a week
        a_week_ago = datetime.date.today() - datetime.timedelta(days=7)
        post_within_a_week = QiitaPost.objects.filter(date__gte=a_week_ago)

        for post in post_within_a_week:
            url = 'https://qiita.com/api/v2/items/%s/likes' % post.url.split('/')[-1]
            async with session.get(url) as resp:

                json_text = await resp.text()
                post_json = json.loads(json_text)
                logger.debug(len(post_json))

                post.lgtm = len(post_json)
                # post.save()

                if post.twitter_screen_name != "undefined":
                    try:
                        tweet_string = ""
                        tweet_template = SLACK_MENTION_ADDRESS + " \n投稿お願いします！\n\n【祝】@%s さんの記事「%s」が️%iLGTM突破！おめでとうございます！ %s #LINEDC #Qiita"

                        tweet_count_array = [100, 50, 30, 10]
                        for cnt in tweet_count_array:
                            if post.lgtm >= cnt and post.last_tweeted_lgtm_count < cnt:
                                tweet_string = tweet_template % (
                                    post.twitter_screen_name,
                                    post.name,
                                    cnt,
                                    post.url)
                                post.last_tweeted_lgtm_count = cnt
                                break

                        if tweet_string != "":
                            logger.debug(tweet_string)
                            requests.post(SLACK_WEBHOOK_URL,
                                          headers={'Content-Type': 'application/json'},
                                          data=json.dumps({"text": tweet_string}))

                    except:
                        logger.warning("Error posting to Slack")

                post.save()

        # get new tweets
        qiita_tags = QiitaTag.objects.all()
        yesterday = datetime.date.today() - datetime.timedelta(days=2)

        for qiita_tag in qiita_tags:
            url = 'https://qiita.com/api/v2/items?page=1&per_page=100&query=tag:%s+created:>%s' % \
                  (qiita_tag, str(yesterday))
            async with session.get(url) as resp:

                json_text = await resp.text()
                post_json = json.loads(json_text)

                for post in post_json:
                    post_date = parse(post['created_at'])

                    logger.debug(post['title'])

                    twitter_screen_name = 'undefined'
                    if post['user']['twitter_screen_name'] is not None:
                        twitter_screen_name = post['user']['twitter_screen_name']

                    try:
                        all_member = list(QiitaMember.objects.all().values_list('name', flat=True))
                        writer = re.findall(r'https://qiita.com/(.+?)/items/', post['url'])[0]

                        if writer not in all_member:
                            logger.debug('new writer')
                            QiitaMember(name=writer, date=post_date).save()

                            if twitter_screen_name != 'undefined':
                                tweet_template = SLACK_MENTION_ADDRESS + " \n投稿お願いします！\n\n LINEのAPIに関する記事のご執筆、ありがとうございます！s > 「%s」 by @%s さん %s #LINEDC #Qiita"
                                tweet_string = tweet_template % (
                                    post['title'],
                                    twitter_screen_name,
                                    post['url'])
                                requests.post(SLACK_WEBHOOK_URL,
                                              headers={'Content-Type': 'application/json'},
                                              data=json.dumps({"text": tweet_string}))


                        QiitaPost(name=post['title'], date=post_date, url=post['url'], tag_id=qiita_tag,
                                  lgtm=post['likes_count'],
                                  remaining_count=0, twitter_screen_name=twitter_screen_name,
                                  last_tweeted_lgtm_count=0).save()


                    except IntegrityError:
                        print("already exists")


async def qiita_post(request):
    loop = asyncio.get_event_loop()
    loop.create_task(get_qiita_post_async())

    return HttpResponse("ok")


async def get_qiita_organization_member_async():
    async with aiohttp.ClientSession() as session:
        popular_organizations = ['protoout-studio', ]

        for organization in popular_organizations:

            end = False

            for i in range(1, 100):
                url = 'https://qiita.com/organizations/%s/members?page=%i' % (organization, i)
                async with session.get(url) as resp:
                    source = await resp.text()

                    soup = BeautifulSoup(source, 'html5lib')
                    member_id_p_tag = soup.find_all('p', string=re.compile('^@'))

                    for member_id in member_id_p_tag:
                        QiitaOrganization(username=member_id.text[1:], organization=organization).save()
                        logger.debug(member_id.text)

                    if len(member_id_p_tag) == 0:
                        end = True
                        break

            if end:
                break


async def qiita_organization_member(request):
    loop = asyncio.get_event_loop()
    loop.create_task(get_qiita_organization_member_async())

    return HttpResponse("ok")


async def get_zenn_post_async():
    async with aiohttp.ClientSession() as session:

        zenn_topics = ZennTopics.objects.all()
        for topics in zenn_topics:
            url = 'https://zenn.dev/topics/%s/feed/' % (topics)
            logger.debug(url)

            async with session.get(url) as resp:

                time.sleep(1)
                feed_text = await resp.text()
                # decoded = feed_text.decode('utf-8')
                feed = feedparser.parse(feed_text)

                cnt = 0
                for entry in feed.entries:
                    logger.debug(entry.link)
                    cnt += 1
                    if cnt > 10:
                        break

                    async with session.get(entry.link) as resp:
                        source_text = await resp.text()

                        soup = BeautifulSoup(source_text, 'html5lib')

                        like_count = 0
                        try:
                            js_body = soup.select_one('script[id=__NEXT_DATA__]')
                            js_data = json.loads(js_body.get_text())
                            logger.debug(js_data['props']['pageProps']['article']['likedCount'])
                            like_count = js_data['props']['pageProps']['article']['likedCount']
                        except:
                            logger.debug("no like count")

                        twitter_id = "undefined"
                        try:
                            if 'books' in entry.link:
                                a_twitter = soup.select('a[class^=ProfileCard_link__]')[-1]
                                logger.debug(a_twitter['href'])
                                twitter_id = a_twitter['href'].split('/')[-1]
                            else:
                                a_twitter = soup.select_one('a[class^=SidebarUserBio_linkTwitter__]')
                                logger.debug(a_twitter['href'])
                                twitter_id = a_twitter['href'].split('/')[-1]
                                logger.debug(twitter_id)

                        except:
                            logger.debug("no twitter account")

                        try:
                            ZennPost(name=entry.title, date=parse(entry.published), url=entry.link, topics_id=topics,
                                     liked=like_count,
                                     remaining_count=7, twitter_screen_name=twitter_id).save()
                        except IntegrityError:
                            logger.warning("already exists")

                            posts = ZennPost.objects.filter(url=entry.link)
                            for post in posts:
                                post.liked = like_count
                                post.twitter_screen_name = twitter_id
                                logger.debug("overwritten")
                                # post.save()

                                if int(like_count) >= 5:
                                    logger.debug('popular post')

                                    try:
                                        tweet_string = ""
                                        tweet_template = SLACK_MENTION_ADDRESS + " \n投稿お願いします！\n\n【祝】@%s さんの記事「%s」が️%iLiked突破！おめでとうございます！ %s #LINEDC #Zenn"

                                        tweet_count_array = [100, 50, 30, 10]
                                        for cnt in tweet_count_array:
                                            if post.liked >= cnt and post.last_tweeted_lgtm_count < cnt:
                                                tweet_string = tweet_template % (
                                                    post.twitter_screen_name,
                                                    post.name,
                                                    cnt,
                                                    post.url)
                                                post.last_tweeted_lgtm_count = cnt
                                                break

                                        if tweet_string != "":
                                            logger.debug(tweet_string)
                                            requests.post(
                                                SLACK_WEBHOOK_URL,
                                                headers={'Content-Type': 'application/json'},
                                                data=json.dumps({"text": tweet_string}))
                                    except:
                                        logger.warning("error posting to Slack")

                                post.save()

                        try:
                            all_member = list(ZennMember.objects.all().values_list('name', flat=True))
                            writer = ""
                            try:
                                writer = re.findall(r'https://zenn.dev/(.+?)/articles/', entry.link)[0]
                            except:
                                writer = re.findall(r'https://zenn.dev/(.+?)/books/', entry.link)[0]

                            if writer not in all_member:
                                logger.debug('new writer')
                                ZennMember(name=writer, date=post_date).save()

                                if twitter_id != 'undefined':
                                    tweet_template = SLACK_MENTION_ADDRESS + " \n投稿お願いします！\n\n LINEのAPIに関する記事のご執筆、ありがとうございます！ > 「%s」 by @%s さん %s #LINEDC #Qiita"
                                    tweet_string = tweet_template % (
                                        entry.title,
                                        twitter_id,
                                        entry.link)
                                    requests.post(SLACK_WEBHOOK_URL,
                                                  headers={'Content-Type': 'application/json'},
                                                  data=json.dumps({"text": tweet_string}))

                        except IntegrityError:
                            logger.warning("already exists")


async def zenn_post(request):
    loop = asyncio.get_event_loop()
    loop.create_task(get_zenn_post_async())

    return HttpResponse("ok")


async def get_connpass_new_event_async():
    async with aiohttp.ClientSession() as session:

        communities = Community.objects.all()
        for community in communities:
            url = community.url + 'ja.atom'
            logger.debug(url)

            async with session.get(url) as resp:
                feed_text = await resp.text()
                feed = feedparser.parse(feed_text)

                for entry in feed.entries:
                    logger.debug(entry.title)
                    date = re.findall(r'開催日時: (.+?) ', entry.summary)[0]
                    url = re.findall(r'https://(.*?)\?utm_campaign', entry.id)[0]
                    try:
                        Event(name=entry.title, date=datetime.date(int(date.split('/')[0]), int(date.split('/')[1]),
                                                                   int(date.split('/')[2])),
                              url='https://' + url, event_id=url.split('/')[-2], community_id=community).save()
                    except IntegrityError as e:
                        logger.warning(e)


async def connpass_new_event(request):
    loop = asyncio.get_event_loop()
    loop.create_task(get_connpass_new_event_async())

    return HttpResponse("ok")


def get_youtube_video():
    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=YOUTUBE_API_KEY,
        cache_discovery=False,
    )

    video_id_list = []

    time_after = datetime.datetime.utcnow() - datetime.timedelta(days=2)

    request = youtube.search().list(
        channelId=YOUTUBE_CHANNEL_ID,
        type='video',
        part='snippet',
        maxResults=50,
        publishedAfter=time_after.isoformat('T') + 'Z',
        order="date",
        fields="nextPageToken,items(id/videoId,snippet/title,snippet/publishedAt)"
    )

    while request:
        response = request.execute()
        logger.debug(json.dumps(response, indent=2, ensure_ascii=False))

        for item in response['items']:
            video_id = item['id']['videoId']
            video_response = youtube.videos().list(id=video_id, part='liveStreamingDetails').execute()

            is_livestreaming = True
            if video_response['items'][0].get('liveStreamingDetails') == None:
                logger.debug('not live')
                is_livestreaming = False

            date_str = item['snippet']['publishedAt'].split('T')[0]

            try:
                YoutubeVideo(title=item['snippet']['title'], url='https://www.youtube.com/watch?v=' + video_id,
                             date=datetime.date(int(date_str.split('-')[0]), int(date_str.split('-')[1]),
                                                int(date_str.split('-')[2])), livestreaming=is_livestreaming).save()
            except IntegrityError as e:
                logger.warning(e)

        request = youtube.search().list_next(request, response)

    # logger.debug(json.dumps(search_response, indent=2, ensure_ascii=False))


async def youtube_video(request):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, get_youtube_video)

    return HttpResponse("ok")


def add_leader_async():
    qiita = Qiita()
    zenn = Zenn()
    connpass = Connpass()

    # Should validate accounts prior to insert

    ar = []

    for ac in ar:
        if connpass.validate(ac) is False:
            logger.debug('Error')
            logger.debug(ac)


async def add_leader(request):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, add_leader_async)

    return HttpResponse("ok")


def get_zenn_member_all():
    all_post = ZennPost.objects.all().order_by('date')
    all_member = list(ZennMember.objects.all().values_list('name', flat=True))

    for post in all_post:
        logger.debug('%s, %s', str(post.date), post.name)
        writer = ""
        try:
            writer = re.findall(r'https://zenn.dev/(.+?)/articles/', post.url)[0]
        except:
            writer = re.findall(r'https://zenn.dev/(.+?)/books/', post.url)[0]

        logger.debug(writer)

        if writer in all_member:
            logger.debug('not new')
        else:
            logger.debug('this writer is new')

            try:
                ZennMember(name=writer, date=post.date).save()
            except IntegrityError:
                logger.debug("already exists")

    return 0


async def zenn_member_all(request):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, get_zenn_member_all)

    return HttpResponse("ok")


# @csrf_exempt Throws 'It returned an unawaited coroutine instead' Error So can't implement HTTP POST
async def do_all_job(request):
    logger.debug('do_all_job')

    loop = asyncio.get_event_loop()

    # get newly published event of Connpass
    loop.create_task(get_connpass_new_event_async())

    # get number of all Connpass Community
    loop.create_task(get_connpass_member_async())

    # get subscriber count of Youtube
    loop.run_in_executor(None, get_youtube_subscriber)

    # get attendee, UU, view of Connpass
    loop.create_task(get_connpass_registration_async())

    # get tweet has relating hashtags
    loop.run_in_executor(None, get_tweet)

    # get new qiita post and overwrite lgtm count
    loop.create_task(get_qiita_post_async())

    # get Qiita members of group to focus on
    loop.create_task(get_qiita_organization_member_async())

    # get new zenn post and overwrite liked count
    loop.create_task(get_zenn_post_async())

    # get newly published video of Youtube
    loop.run_in_executor(None, get_youtube_video)

    return HttpResponse("ok")
