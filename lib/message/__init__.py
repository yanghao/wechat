import os
import sys
_p = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template')

import time
from mako.template import Template
from mako.lookup import TemplateLookup

message_lookup = TemplateLookup(directories=[_p])

class MessageError(Exception): pass

class Message:
    def __init__(self, to_user, from_user, content):
        self.to_user = to_user
        self.from_user = from_user
        self.timestamp = int(time.time())
        self.msg_type = content.msg_type
        self.content = content

    def __str__(self):
        t = message_lookup.get_template(self.msg_type + '.mako')
        return t.render(msg=self)

class Content:
    def __init__(self): pass

class TextContent(Content):
    msg_type = 'text'
    def __init__(self, msg):
        self.content = msg

class NewsContent(Content):
    msg_type = 'news'
    def __init__(self, news_list):
        self.news_count = len(news_list)
        for item in news_list:
            self.validate(item)
        self.news = news_list

    def validate(self, item):
        if type(item) != dict:
            raise MessageError("Only dict is accepted")
        keys = item.keys()
        for i in ['title', 'desc', 'pic_url', 'url']:
            if i not in keys:
                raise MessageError("key not found in message item: %s" % i)

class PhotoContent(Content):
    msg_type = 'image'
    def __init__(self, media_id):
        self.media_id = media_id

class VoiceContent(Content):
    msg_type = 'voice'
    def __init__(self, media_id):
        self.media_id = media_id

class MusicContent(Content):
    msg_type = 'music'
    def __init__(self, title, media_id, desc, url, url_hq=None):
        self.title = title
        self.media_id = media_id
        self.desc = desc
        self.url = url
        self.url_hq = url_hq

class VideoContent(Content):
    msg_type = 'video'
    def __init__(self, media_id, media_title, media_desc):
        self.media_id = media_id
        self.media_title = media_title
        self.media_desc = media_desc

if __name__ == '__main__':
    print("=======================================================")
    text_content = TextContent("I love this game ...")
    msg = Message('xiaoyezi', 'hua', text_content)
    print(str(msg))
    print("=======================================================")
    news = {'title': 'test titile', 'desc': "test description",
                 'pic_url': 'test pic url', 'url': 'url ...'}
    news_list = [news, news, news]
    news_content = NewsContent(news_list)
    print(str(Message('xiaoyezi', 'hua', news_content)))
    print("=======================================================")
    photo = PhotoContent(3)
    print(str(Message('xiaoyezi', 'hua', photo)))
    print("=======================================================")
    voice = VoiceContent(888)
    print(str(Message('xiaoyezi', 'hua', voice)))
    print("=======================================================")
    music = MusicContent("music title", 77, "music description", 'url low quality', 'url_hq ...')
    print(Message('xiaoyezi', 'hua', music))
    print("=======================================================")
    video = VideoContent(8, "test media title", "This is a test only video ...")
    print(str(Message('xiaoyezi', 'hua', video)))
