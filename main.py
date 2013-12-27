import webapp2

from view import WeChat

urls = [ (r'/?', WeChatHome),
         (r'/wechat/?', WeChat),
         (r'/.*', Not_Found),
]

application = webapp2.WSGIApplication(urls, debug=True)
