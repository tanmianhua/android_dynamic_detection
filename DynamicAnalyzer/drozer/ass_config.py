# -*- coding:utf-8 -*-
import sys,os
import xml.dom.minidom

#获取脚本文件的当前路径
def cur_file_dir():
     #获取脚本路径
     path = sys.path[0]
     #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
     if os.path.isdir(path):
         return path
     elif os.path.isfile(path):
         return os.path.dirname(path)
#打开xml文档
dom = xml.dom.minidom.parse(cur_file_dir()+'/config.xml')
#得到文档元素对象
configXML={}
configRoot = dom.documentElement
itemList = configRoot.getElementsByTagName('data')
for item in itemList:  
        configXML.setdefault(item.getAttribute("key"),item.getAttribute("value"));
#判断当前平台
islinux = (sys.platform != "win32") 
#程序本身路径
pinggu_dir = configXML['basedir'];
#drozee 服务器连接地址
drozer_server = "127.0.0.1:6001"

#模拟器adb连接地址
# adb_server = "127.0.0.1:53001"
# adb_server = "127.0.0.1:5555"
adb_server = "192.168.1.132:5555"

cmd_jdb = pinggu_dir+"/tool/jdb.sh"
#aapt命令
cmd_aapt = pinggu_dir+"/tool/aapt"

#anprohelper命令全路�?
cmd_anprohelper = pinggu_dir+"/tool/anprohelper.sh"

#drozer命令路径（因为需要切换）
cmd_drozer = "drozer"

#adb命令全路�?
#cmd_adb = pinggu_dir+"/tool/adb"
cmd_adb = '/home/lzyang/dynamic/android_dynamic_detection/DynamicAnalyzer/tools/adb/linux/adb'
#dex2jar命令全路�?
cmd_dex2jar = pinggu_dir+"/tool/dex2jar/d2j-dex2jar.sh"

#jar2java命令全路�?
cmd_jar2java = pinggu_dir+"/tool/jd.sh"

#sign
cmd_sign = pinggu_dir+"/tool/sign.sh"

#axml
cmd_axml = pinggu_dir+"/tool/axml.sh"

#7za
cmd_7za = pinggu_dir+"/tool/7za"

#ndk-nm
cmd_ndk_nm = pinggu_dir+"/tool/arm-linux-androideabi-nm"

#ndk-gdb
#cmd_ndk_gdb = "cmd /c C:/adt-bundle-windows-x86-20131030/sdk/android-ndk-r10d/ndk-gdb-py.cmd --adb=\""+cmd_adb+"\" -s "+adb_server+" --verbose --start --force --project="

cmd_ndk_gdb = "cmd /c "+ configXML['ndkdir'] +"ndk-gdb-py --adb=\""+cmd_adb+"\" -s "+adb_server+" --verbose --start --force --project="

#pdf模板
pdf_template = pinggu_dir+"/assets/template.pdf"
