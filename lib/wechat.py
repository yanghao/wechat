import logging
from hashlib import sha1

class WeChat:
    def __init__(self, passcode):
       self.log = logging.getLogger(self.__class__.__name__)
       self.passcode = passcode

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
