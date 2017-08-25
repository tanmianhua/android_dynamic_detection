# -*- encoding:utf-8 -*-

from ass_i18n import ass_i18n_data
import os,codecs
import shutil
import sys
from datetime import datetime

class AssI18n(object):
    def __init__(self):
        self.apk_file=''
        self.out_path = ''

        self.language=''
        self.to_clean = True
    #i18字符格式转换 [src 原字符]
    def i18n(self, src):
#         print(self.language, src)
        try:
            return ass_i18n_data[src][self.language]
        except:
            return src
    #初始化 [argv 参数列表]
    def init(self, argv):

        self.apk_file = sys.argv[1]
        self.out_path = sys.argv[1]+".result/"

        return False
        # if len(argv)>1:
        #     #文件路径，支持中文
        #     self.apk_file = argv[1]
        #     #self.apk_file = unicode(apkstr, "utf8")
        #
        # if len(argv)>2 and argv[2]!='-':
        #     self.language = argv[2]
        #
        # self.to_clean = True
        # if len(argv)>3 and argv[3]=='dirty':
        #     self.to_clean = False
        
    def run(self):
        return True
            
    def main(self):
        if len(sys.argv)<2:
            print("usage: %s apk_file [language]" % (sys.argv[0]))
        else:
            now = datetime.now()
            self.init(sys.argv)
            self.run()
            print("Total used %d secs" % ((datetime.now() - now).total_seconds()))  

#添加引用 [path 字符]
def q(path):
    return "\""+path+"\""
#删除文件夹 [path 文件路径]
def rmdir(path, force=False):
    if force and os.path.exists(path):
        shutil.rmtree(path, True)
#创建文件夹 [path 文件路径]
def ass_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)
#删除文件 [path 文件路径]
def remove(apk_file):
    if os.path.exists(apk_file):
        os.remove(apk_file)
#截取字符 [src_str 源字符] [key 关键字] [endof 结束位置]
def get_val(src_str, key, endof=True):
    s,i = get_val2(src_str, key, endof)
    return s
#截取字符 [src_str 源字符] [begin_str 开始字符] [end_str 结束位置]
def mid_str(src_str, begin_str, end_str):
#     print(mid_str2(src_str, begin_str, end_str))
    (s,e),b = mid_str2(src_str, begin_str, end_str)
    return s
#截取字符2 [src_str 源字符] [key 关键字] [endof 结束位置] 
def get_val2(src_str, key, endof=True):
    index = src_str.find(key)
    if index >= 0:
        if endof:
            return src_str[index+len(key):].strip(),index+len(key)
        else:
            return src_str[:index].strip(),index
    else:
        return '',0
#截取字符 [src_str 源字符] [key 关键字] [endof 结束位置] 返回：开始位置
def mid_str2(src_str, begin_str, end_str):
    src_str2,begin_index = get_val2(src_str, begin_str)
    if src_str2=='':
        return ('',0),0
    
    return get_val2(src_str2, end_str, False),begin_index
#byte to utf-8 [strs 源字符] 
def b2u(strs):
    if sys.version_info.major>=3:
        return strs
    if isinstance(strs, bytes):
        try:
            return strs.decode('utf-8')
        except:
            try:
                return strs.decode('cp936')
            except:
                return strs
    return strs
# utf-8 to byte [u 源字符] 
def u2b(u):
    if sys.version_info.major>=3:
        return u
    
    try:
        return u.encode('utf-8')
    except:
        return u
#重写读取文件 [filename 文件全路径名] 
def read_file(filename):
    s = ''
    try:
        with codecs.open(filename, "r","utf-8") as f:
            s = f.read()
        #with open(filename) as f:
        #    s = f.read()
    except:
        return s
    return s
#重写写入 [filename 文件全路径名] [filestr 写入数据] [mode 方式]
def write_file(filename, filestr, mode='w'):
    try:
        if sys.version_info.major>=3:
            with open(filename, mode=mode, encoding='utf8') as f:
                f.write(filestr)
        else:
            with open(filename, mode=mode) as f:
                f.write(filestr)
        return True    
    except:
        return False
#分隔字符 [src 源字符] [sep 分隔符] [index 返回索引]
def split_empty(src, sep, index):
    srcs = src.split(sep)
    i = 0
    for dst in srcs:
        if dst=='':
            continue
#         print(i, dst)
        if i == index:
            return dst
        
        i=i+1
    
    return '' 



         
                