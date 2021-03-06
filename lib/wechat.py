# -*- coding:utf-8 -*-
import os
import time
import logging
from hashlib import sha1
from httplib2 import Http
from urllib import urlencode
import json
import requests

from lock import Lock

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
    raw_group_url = 'https://api.weixin.qq.com/cgi-bin/groups/%s?access_token=%s'
    raw_send_url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s'
    raw_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s'
    raw_user_url = 'https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s&next_openid=%s'
    all_data_type = ('image', 'voice', 'thumb', 'video')
    token = Token()
    def __init__(self, appid, passcode, secret, token_path, init_token=True):
       self.log = logging.getLogger(self.__class__.__name__)
       self.appid = appid
       self.passcode = passcode
       self.secret = secret
       self.token_url = self.raw_token_url % (appid, passcode)
       self.http = Http()
       self.token_last_update = None
       self.access_token = None
       self.token_expire = None
       self.token_path = token_path
       self.lock_token = Lock("wechat", "token")
       if init_token:
           self.refresh_token()
       else:
           self.check_token()

    def verify(self, signature, timestamp, nonce):
        if type(signature) not in [str, unicode]:
            self.log.error("signature is not string: %s" % (str(type(signature))))
            return False
        if type(timestamp) not in [str, unicode]:
            self.log.error("timestamp is not string")
            return False
        if type(nonce) not in [str, unicode]:
            self.log.error("nonce is not string")
            return False
        clist = [self.secret, timestamp, nonce]
        clist.sort()
        content = ''
        for item in clist:
            content += item
        sh = sha1()
        sh.update(content)
        hexdigest = sh.hexdigest()
        if signature != hexdigest:
            self.log.error("sha1sum mismatch: %s - %s" % (signature, hexdigest))
            return False
        else:
            return True

    def refresh_token(self):
        self.log.info("Refreshing token ...")
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
            with self.lock_token:
                with open(self.token_path, 'wb') as fd:
                    fd.write(json.dumps([self.access_token, self.token_expire]))

    def check_token(self):
        if not os.path.exists(self.token_path):
            self.refresh_token()
        with self.lock_token:
            with open(self.token_path, 'rb') as fd:
                data = fd.read()
        token, expire = json.loads(data)
        if int(time.time()) > expire:
            self.refresh_token()
        else:
            self.access_token = token.encode('utf-8')
            self.token_expire = expire

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

    def check_error(self, resp, content, err_type):
        if resp['status'] != '200':
            raise WeChatError("Failed to create menu ...")
        try:
            data = json.loads(content)
        except:
            raise WeChatError("Failed to load json response: %s" % content)
        if err_type == 'menu':
            try:
                err = data['errcode']
                msg = data['errmsg']
            except KeyError:
                raise WeChatError("Failed to find errcode: %s" % str(data))
            if err != 0:
                raise WeChatError("Request failed: %s" % str(data))
        elif err_type == 'group':
            group = None
            try:
                group = data['group']
            except KeyError:
                try:
                    err = data['errcode']
                    msg = data['errmsg']
                except KeyError:
                    raise WeChatError("Failed to find errcode: %s" % str(data))
                raise WeChatError("Error message: %s" % str(data))
        elif err_type == 'groups':
            groups = None
            try:
                groups = data['groups']
            except KeyError:
                try:
                    err = data['errcode']
                    msg = data['errmsg']
                except KeyError:
                    raise WeChatError("Failed to find errcode: %s" % str(data))
                raise WeChatError("Error message: %s" % str(data))
        elif err_type == 'groupid':
            groupid = None
            try:
                groupid = data['groupid']
            except KeyError:
                try:
                    err = data['errcode']
                    msg = data['errmsg']
                except KeyError:
                    raise WeChatError("Failed to find errcode: %s" % str(data))
                raise WeChatError("Error message: %s" % str(data))
        elif err_type == 'info':
            groupid = None
            try:
                groupid = data['openid']
            except KeyError:
                try:
                    err = data['errcode']
                    msg = data['errmsg']
                except KeyError:
                    raise WeChatError("Failed to find errcode: %s" % str(data))
                raise WeChatError("Error message: %s" % str(data))
        elif err_type == 'data':
            tmp = None
            try:
                tmp = data['data']
            except KeyError:
                try:
                    err = data['errcode']
                    msg = data['errmsg']
                except KeyError:
                    raise WeChatError("Failed to find errcode: %s" % str(data))
                raise WeChatError("Error message: %s" % str(data))

    def send_message(self, user, msg):
        url = self.raw_send_url % self.token
        msgtype = msg.keys()[0]
        data = {'touser': user, 'msgtype': msgtype, msgtype: msg[msgtype]}
        s = json.dumps(data, ensure_ascii=False)
        resp, content = self.http.request(url, method="POST", body=s)
        self.check_error(resp, content, 'menu')

    def send(self, user, msg):
        if type(msg) != dict:
            if type(msg) not in [tuple, list]:
                raise WeChatError("Msg is not dict or list: %s" % str(msg))
        if type(msg) in [tuple, list]:
            for m in msg:
                if type(m) != dict:
                    raise WeChatError("Msg item is not dict: %s" % str(m))
                if len(m.keys()) != 1:
                    raise WeChatError("Msg can only has one key: %s" % str(m))
                self.send_message(user, m)
        else:
            self.send_message(user, msg)

    def create_menu(self, menu):
        url = self.raw_menu_url % self.token
        s = json.dumps(menu, ensure_ascii=False)
        resp, content = self.http.request(url, method="POST", body=s)
        self.check_error(resp, content, 'menu')

    def create_group(self, group_name):
        url = self.raw_group_url % ('create', self.token)
        data = {'group': {'name': group_name}}
        s = json.dumps(data, ensure_ascii=False)
        resp, content = self.http.request(url, method="POST", body=s)
        self.check_error(resp, content, 'group')

    def get_group_list(self):
        url = self.raw_group_url % ('get', self.token)
        resp, content = self.http.request(url, method="GET")
        self.check_error(resp, content, 'groups')
        return json.loads(content)['groups']

    def get_group_id(self, user):
        url = self.raw_group_url % ('getid', self.token)
        data = {'openid': user}
        s = json.dumps(data)
        resp, content = self.http.request(url, method="POST", body=s)
        self.check_error(resp, content, 'getid')
        return json.loads(content)['groupid']

    def update_group(self, group_id, name):
        url = self.raw_group_url % ('update', self.token)
        data = {'group': {'id': group_id, 'name': name}}
        s = json.dumps(data)
        resp, content = self.http.request(url, method="POST", body=s)
        # !! stupid wechat API design ... reuse 'menu' here
        self.check_error(resp, content, 'menu')

    def move_user(self, openid, group_id):
        url = self.raw_group_url % ('members/update', self.token)
        data = {'openid': openid, 'to_groupid': group_id}
        s = json.dumps(data)
        resp, content = self.http.request(url, method="POST", body=s)
        # !! stupid wechat API design ... reuse 'menu' here
        self.check_error(resp, content, 'menu')

    def get_info(self, openid):
        url = self.raw_info_url % (self.token, openid)
        resp, content = self.http.request(url, method="GET")
        self.check_error(resp, content, 'info')
        return json.loads(content)

    def get_user_list(self):
        url = self.raw_user_url % (self.token, '')
        resp, content = self.http.request(url, method="GET")
        self.check_error(resp, content, 'data')
        data = json.loads(content)
        total = data['total']
        count = data['count']
        next_openid = data['next_openid']
        result = list(data['data']['openid'])
        while (count < total):
            url = self.raw_user_url % (self.token, next_openid.encode('utf-8'))
            resp, content = self.http.request(url, method="GET")
            self.check_error(resp, content, 'data')
            data = json.loads(content)
            count += data['count']
            result.extend(data['data']['openid'])
        result = [item.encode('utf-8') for item in result]
        return result

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    token_path = os.path.join(os.environ['HOME'], '.wechat')
    wechat = WeChat('wx0428ebd09610826e', '86105554ce1f5d2bae4d88eae2fd925e', 'test', token_path, False)
    #print(time.time())
    print(wechat.token)
    #print(wechat.token_expire)
    #with open("/home/hua/Pictures/test2.jpg", 'rb') as fd:
    #    data = fd.read()
    #media_id = wechat.upload('image', data)
    #data_download = wechat.download(media_id)
    #if data_download == data:
    #    print("Data downloading OK")
    #else:
    #    print("Data mismatch !!!")
    #################################
    menu = dict()
    menu['button'] = []
    sub_button = [{"type": "click", "name": "土豆丝", "key": "tudousi"},
                  {"type": "click", "name": "西红柿炒鸡蛋", "key": "xihongshichaojidan"},
                  {"type": "click", "name": "几个很多的西红柿炒鸡蛋", "key": "manyxihongshichaojidan"},
                  ]
    one_button = {"name": '菜单', "sub_button": sub_button}
    menu['button'].append(one_button)
    #print json.dumps(menu)
    #wechat.create_menu(menu)
    #wechat.create_group('normal')
    #print wechat.get_group_list()
    #print wechat.get_group_id('oJEaUjoHMNnKsdLLqqEw8RWX-D5k')
    #wechat.update_group(100, "super_vip")
    #print wechat.get_group_list()
    #user = 'oJEaUjoHMNnKsdLLqqEw8RWX-D5k'
    #user2 = 'abdfadfadfa'
    #wechat.move_user(user, 100)
    #print wechat.get_group_list()
    #msg = {"text": {"content": "I love this game ..."}}
    #wechat.send(user, [msg, msg])
    #print(wechat.get_info(user))
    #print(wechat.get_user_list())
    msg = {"text": {"content": "新年快乐！"}}
    print msg
    print "-=--------------------"
    print json.dumps(msg, ensure_ascii=False)
    print "-=--------------------"
    user_list = wechat.get_user_list()
    for user in user_list:
        msgtype = 'text'
        data = {'touser': user, 'msgtype': 'text', 'text': {"content": "新年快乐！"}}
        print "**********************"
        print json.dumps(msg, ensure_ascii=False)
        print data
        print json.dumps(data, ensure_ascii=False)
        print "**********************"
        try:
            wechat.send(user, msg)
        except:
            wechat.log.exception(user)
            print("Failed to send to user: %s" % user)
