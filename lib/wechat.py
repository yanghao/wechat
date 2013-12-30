# -*- coding:utf-8 -*-
import time
import logging
from hashlib import sha1
from httplib2 import Http
from urllib import urlencode
import json
import requests

class WeChatError(Exception): pass

class Token(object):
    def __get__(self, obj, objtype):
        if obj.access_token == None:
            obj.refresh_token()
        obj.check_token()
        return obj.access_token

    def __set__(self, obj, value):
        raise ValueError("Cannot set a token")

class WeChat(object):
    raw_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
    raw_upload_url = 'http://file.api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s'
    raw_download_url = 'http://file.api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s'
    raw_menu_url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s'
    all_data_type = ('image', 'voice', 'thumb', 'video')
    token = Token()
    def __init__(self, appid, passcode):
       self.log = logging.getLogger(self.__class__.__name__)
       self.appid = appid
       self.passcode = passcode
       self.token_url = self.raw_token_url % (appid, passcode)
       self.http = Http()
       self.token_last_update = None
       self.access_token = None
       self.token_expire = None
       self.refresh_token()

    def verify(self, signature, timestamp, nonce):
        if type(signature) != str:
            self.log.debug("signature is not string")
            return False
        if type(timestamp) != str:
            self.log.debug("timestamp is not string")
            return False
        if type(nonce) != str:
            self.log.debug("nonce is not string")
            return False
        clist = [self.passcode, timestamp, nonce]
        clist.sort()
        content = ''
        for item in clist:
            content += item
        sh = sha1()
        sh.update(content)
        hexdigest = sh.hexdigest()
        if signature != hexdigest:
            self.log.debug("sha1sum mismatch")
            return False
        else:
            return True

    def refresh_token(self):
        resp, content = self.http.request(self.token_url)
        status = resp['status']
        if status != '200':
            self.log.error("Failed to get access token ...")
            self.log.error("Response header:")
            self.log.error(str(resp))
            self.log.error("Response body:")
            self.log.error(content)
        else:
            try:
                data = json.loads(content)
            except:
                self.log.error("Failed to load json data: %s" % content)
            try:
                access_token = data['access_token']
                expires_in = data['expires_in']
            except KeyError:
                self.log.error("json data is not as expected: %s" % str(data))
            self.token_last_update = int(time.time())
            self.token_expire = self.token_last_update + int(str(expires_in), 0)
            self.access_token = access_token.encode('utf-8')

    def check_token(self):
        if int(time.time()) > self.token_expire:
            self.refresh_token()

    def upload(self, data_type, data):
        if data_type not in self.all_data_type:
            raise WeChatError("data_type not supported: %s (%s)" % (data_type, str(self.all_data_type)))
        url = self.raw_upload_url % (self.token, data_type)
        files = {'media': ('test.jpg', data), 'type': 'image'}
        r = requests.post(url, files=files)
        if r.status_code != 200:
            raise WeChatError("Failed to get 200 response: %s, %s" % (str(r.headers), r.text))
        try:
            data_dict = json.loads(r.text)
        except:
            raise WeChatError("Failed to do json.loads on: %s" % r.text)
        try:
            media_id = data_dict['media_id']
            created_at = data_dict['created_at']
            media_type = data_dict['type']
        except KeyError as e:
            raise WeChatError("Failed to find some value in: %s (%s)" % (str(data_dict), str(e)))
        return media_id

    def download(self, media_id):
        url = self.raw_download_url % (self.token, media_id)
        resp, content = self.http.request(url)
        if resp['status'] != '200':
            raise WeChatError("Failed to retrieve media: %s" % media_id)
        return content

    def create_menu(self, menu):
        url = self.raw_menu_url % self.token
        s = json.dumps(menu, ensure_ascii=False)
        resp, content = self.http.request(url, method="POST", body=s)
        if resp['status'] != '200':
            raise WeChatError("Failed to create menu ...")
        try:
            data = json.loads(content)
        except:
            raise WeChatError("Failed to load json response: %s" % content)
        try:
            err = data['errcode']
            msg = data['errmsg']
        except KeyError:
            raise WeChatError("Failed to find errcode: %s" % str(data))
        if err != 0:
            raise WeChatError("Menu creation failed: %s" % str(data))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    wechat = WeChat('wx0428ebd09610826e', '86105554ce1f5d2bae4d88eae2fd925e')
    print(time.time())
    print(wechat.token)
    print(wechat.token_expire)
    with open("/home/hua/Pictures/test2.jpg", 'rb') as fd:
        data = fd.read()
    media_id = wechat.upload('image', data)
    data_download = wechat.download(media_id)
    if data_download == data:
        print("Data downloading OK")
    else:
        print("Data mismatch !!!")
    #################################
    menu = dict()
    menu['button'] = []
    sub_button = [{"type": "click", "name": "土豆丝", "key": "tudousi"},
                  {"type": "click", "name": "西红柿炒鸡蛋", "key": "xihongshichaojidan"},
                  {"type": "click", "name": "几个很多的西红柿炒鸡蛋", "key": "manyxihongshichaojidan"},
                  ]
    one_button = {"name": '菜单', "sub_button": sub_button}
    menu['button'].append(one_button)
    wechat.create_menu(menu)
