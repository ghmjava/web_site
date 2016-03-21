# coding=utf-8
import os
import commands
#import hashlib

#def GetFileMd5(f):
#    myhash = hashlib.md5()
#    while True:
#        b = f.read(8096)
#        if not b :
#            break
#        myhash.update(b)
#    return myhash.hexdigest()
#
#def md5_file(a_file):
#    m = hashlib.md5()
#    m.update(a_file.read())
#    return m.hexdigest()

def get_md5(file_path):
    ret = os.system('ls %s' %file_path)
    if 0 != ret:
        return ""
    ret = commands.getstatusoutput('md5 %s' %file_path)
    if 0 != ret[0]:
        return ""
    return ret[1].split(' = ')[1]

