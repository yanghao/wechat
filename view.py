import os
import sys
_p = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
sys.path.insert(0, _p)

from time import strftime
from webapp2 import RequestHandler, Response
from hashlib import sha1
import time
import json
import logging

from wechat import WeChat
from message import Message
from message import MessageError
from message import MessageXMLError

PASSWORD = "ilovexiaoyezi"

log = logging.getLogger("myroot")

from config import TOKEN_PATH
wechat = WeChat('wx0428ebd09610826e', '86105554ce1f5d2bae4d88eae2fd925e', TOKEN_PATH)

class WeChat(RequestHandler):
    def check_request(self):
        signature = self.request.GET.get('signature')
        timestamp = self.request.GET.get('timestamp')
        nonce = self.request.GET.get('nonce')
        if None in [signature, timestamp, nonce]:
            return False
        else:
            return wechat.verify(signature, timestamp, nonce)

    def get(self):
        result = self.check_request()
        echostr = self.request.GET.get('echostr')
        if result == False:
            self.response.write("Try harder ... ;-)")
        else:
            self.response.write(echostr)

    def post(self):
        result = self.check_request()
        if result == False:
            self.response.write("[POST] Try harder ... ;-)")
            return
        try:
            msg = Message(xml=self.request.body)
        except MessageError as e:
            self.log.info("Invalid XML content: %s" % self.request.body)
            self.response.write("[POST] Ooooops ...")
        reply = "Message Type: %s\n" % msg.xml_msg_type
        reply += "Message Data: %s" % str(msg.data)
        reply = Message.reply(reply)
        log.info(reply)
        self.response.write(reply)

class Not_Found(RequestHandler):
    def get(self):
        return Response("Not Found")
