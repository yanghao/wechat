import os
import sys
_p = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template')

import time
from mako.template import Template
from mako.lookup import TemplateLookup

message_lookup = TemplateLookup(directories=[_p])

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

class PhotoContent(Content):
    msg_type = 'image'

class VoiceContent(Content):
    msg_type = 'voice'

class MusicContent(Content):
    msg_type = 'music'

class VideoContent(Content):
    msg_type = 'video'

if __name__ == '__main__':
    text_content = TextContent("I love this game ...")
    msg = Message('xiaoyezi', 'hua', text_content)
    print str(msg)
