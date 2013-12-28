import os
from time import strftime
from webapp2 import RequestHandler, Response
from hashlib import sha1
import xml.etree.ElementTree as ET
import time
import json
import logging

PASSWORD = "ilovexiaoyezi"

log = logging.getLogger("myroot")

template = '''<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    <MsgId>1234567890123456</MsgId>
</xml>'''

class WeChat(RequestHandler):
    def get(self):
        #for i in self.request.GET.keys():
        #    self.response.write("%s : %s <br />" % (i, str(self.request.GET[i])))
        signature = self.request.GET.get('signature')
        timestamp = self.request.GET.get('timestamp')
        nonce = self.request.GET.get('nonce')
        echostr = self.request.GET.get('echostr')
        if None in [signature, timestamp, nonce, echostr]:
            self.response.write("Try harder ... ;-)")
        else:
            clist = ['ilovewechat', timestamp, nonce]
            clist.sort()
            content = ''
            for item in clist:
                content += item
            sh = sha1()
            sh.update(content)
            hexdigest = sh.hexdigest()
            if hexdigest != signature:
                self.response.write("signature mismatch: %s %s" % (hexdigest, signature))
            else:
                self.response.write(echostr)

    def post(self):
        try:
            root = ET.fromstring(self.request.body)
        except ET.ParseError as e:
            self.response.write(str(e))
        receiver = root.find("ToUserName")
        poster = root.find("FromUserName")
        timestamp = root.find("CreateTime")
        msg_type = root.find("MsgType")
        content = root.find("Content")
        msg_id = root.find("MsgId")

        re_root = ET.Element('xml')
        re_receiver = ET.SubElement(re_root, "ToUserName")
        re_receiver.text = poster.text
        re_poster = ET.SubElement(re_root, "FromUserName")
        re_poster.text = receiver.text
        re_timestamp = ET.SubElement(re_root, 'CreateTime')
        re_timestamp.text = str(int(time.time()))
        re_msg_type = ET.SubElement(re_root, "MsgType")
        re_msg_type.text = "text"
        re_content = ET.SubElement(re_root, "Content")
        re_content.text = "Delivered to you by Hua Yanghao:\nReceiver: %s, poster: %s, timestamp: %s, msg_type: %s, content: %s, msg_id: %s" % (receiver.text,
            poster.text, timestamp.text, msg_type.text, content.text, msg_id.text)
        re_func_flag = ET.SubElement(re_root, "FuncFlag")
        re_func_flag.text = '1'
        reply = ET.dump(re_root)
        reply = template % (poster.text, receiver.text, re_timestamp.text, re_content.text)
        log.info(reply)
        self.response.write(reply)

class Not_Found(RequestHandler):
    def get(self):
        return Response("Not Found")
