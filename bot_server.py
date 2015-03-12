import time
from slackclient import SlackClient
import json

import feedparser

f = open('roster.json', 'r')

roster = json.loads(f.read())

token = roster[0]['token']

sc = SlackClient(token)

def who_am_i(client):
    r = json.loads(client.api_call('auth.test'))
    if r['ok']:
        return r
    else:
        return None

def is_to_me(rtm_list_item, me):
    if rtm_list_item['type'] == 'message':
        try:
            if me['user_id'] in rtm_list_item.get('text'):
                return True
            else:
                return False
        except Exception as e:
            print me
            print rtm_list_item
            print e
            return False
    else:
        return False

def get_links(rss, num):
    r = feedparser.parse(rss)
    return r.entries[:num]

def post_links(link_objs, channel, client):
    #TODO Something different for first one
    for link in link_objs:
       client.api_call('chat.postMessage', as_user="true", unfurl_links="true", text=link['title'] + ' ' + link['link'], channel=channel)

IAM = who_am_i(sc)

if sc.rtm_connect():
    while True:
        chatter = sc.rtm_read()
        if chatter:
            at_me = [m for m in chatter if is_to_me(m, IAM)]
            if len(at_me) > 0:
                if 'news' in at_me[0]['text'].lower():
                    channel = at_me[0]['channel']
                    links = get_links('http://www.reddit.com/r/oculus/.rss', 5)
                    post_links(links, channel, sc)
        time.sleep(1)
else:
    print "Connection Failed, invalid token?"
