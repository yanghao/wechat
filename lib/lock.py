import os
import sys
os_version = sys.platform
if os_version != 'win32':
    import fcntl
import logging

class Lock:
    def __init__(self, lock_folder, lock_name, root='/run/lock/pylock', user=True):
        if user == True:
            if os_version == 'win32':
                pass
            else:
                root = root+'-'+str(os.getuid())
        if not os.path.isdir(root):
            os.mkdir(root)
        lock_folder_root = os.path.join(root, lock_folder)
        if not os.path.isdir(lock_folder_root):
            os.mkdir(lock_folder_root)
        self.filepath = os.path.join(lock_folder_root, lock_name)
        self.root = root
        self.lock_folder_root = lock_folder_root
        self.lock_name = lock_name
        self.fd = 0
        self.log = logging.getLogger('Lock-'+lock_folder + '.' + lock_name)

    def __enter__(self):
        self.lock()

    def __exit__(self, type, value, tracback):
        self.unlock()

    def lock(self):
        self.log.debug("Acquring lock ...")
        self.fd = open(self.filepath, 'w')
        fcntl.flock(self.fd, fcntl.LOCK_EX)
        self.log.debug("Acquired.")

    def unlock(self):
        self.log.debug("Releasing lock ...")
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        self.fd.close()
        self.log.debug("Released.")
