import os
import sys
_p = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template')

import time
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mako.template import Template
from mako.lookup import TemplateLookup

message_lookup = TemplateLookup(directories=[_p])

class MessageError(Exception): pass
class MessageXMLError(MessageError): pass

TEXT = "text"
tag_to_user = "ToUserName"
tag_from_user = "FromUserName"
tag_timestamp = "CreateTime"
tag_msg_type = "MsgType"
tag_msg_id = "MsgId"
tag_content = "Content"

class Message:
    def __init__(self, to_user=None, from_user=None, content=None, xml=None):
        self.to_user = to_user
        self.from_user = from_user
        self.timestamp = int(time.time())
        self.content = content
        if content != None:
            self.msg_type = content.msg_type
        else:
            self.msg_type = None
        self.xml = xml
        self.xml_msg = None
        if xml != None:
            self._extract_info(xml)

    def _extract_info(self, xml):
        check_list = [tag_to_user, tag_from_user, tag_timestamp, tag_msg_type, tag_msg_id]
        try:
            root = ET.fromstring(xml)
        except:
            raise MessageXMLError("Invalid XML data: %s" % xml)
        self.xml_to_user = root.find(tag_to_user)
        if self.xml_to_user == None:
            raise MessageXMLError("Cannot find to_user from xml ...")
        self.xml_to_user = self.xml_to_user.text
        self.xml_from_user = root.find(tag_from_user)
        if self.xml_from_user == None:
            raise MessageXMLError("Cannot find from_user from xml ...")
        self.xml_from_user = self.xml_from_user.text
        self.xml_timestamp = root.find(tag_timestamp)
        if self.xml_timestamp == None:
            raise MessageXMLError("Cannot find CreateTime from xml ...")
        self.xml_timestamp = self.xml_timestamp.text
        self.xml_msg_type = root.find(tag_msg_type)
        if self.xml_msg_type == None:
            raise MessageXMLError("Cannot find MsgType from xml ...")
        self.xml_msg_type = self.xml_msg_type.text
        self.xml_msg_id = root.find(tag_msg_id)
        if self.xml_msg_id == None:
            raise MessageXMLError("Cannot find MsgId from xml ...")
        self.xml_msg_id = self.xml_msg_id.text

        #!!! store all the rest fields as message content
        data = {}
        for child in root:
            if child.tag in check_list:
                continue
            else:
                data[child.tag] = child.text
        self.data = data

    def reply(self, content):
        if self.xml_msg_id == None:
            raise MessageError("not initialized from xml ...")
        msg = Message(self.xml_from_user, self.xml_to_user, content)
        t = message_lookup.get_template(msg.msg_type + '.mako')
        return t.render(msg=msg)

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
    print("*******************************************************")
    test_xml = ''' <xml>
     <ToUserName><![CDATA[toUser]]></ToUserName>
      <FromUserName><![CDATA[fromUser]]></FromUserName>
       <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
         <Content><![CDATA[this is a test]]></Content>
          <MsgId>1234567890123456</MsgId>
           </xml>'''
    msg = Message(xml=test_xml)
    print(msg.reply(video))
    print(msg.data)
