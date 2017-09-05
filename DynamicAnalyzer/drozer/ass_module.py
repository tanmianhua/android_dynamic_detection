# -*- coding:utf-8 -*-

'''

'''
import subprocess
import os
import time
import ass_config
from time import sleep
from ass_report import AssReport
from ass_base import AssI18n,rmdir,remove,write_file,mid_str,read_file,q,split_empty
from threading import Timer
from datetime import datetime
import socket
import sys
import traceback
import signal
reload(sys)
sys.setdefaultencoding('gbk')
global t

def to_kill(p):
    if not p==None:
        p.terminate()
    
class AssModule(AssI18n):
    def __init__(self, report=None):
        if report == None:
            self.report = AssReport()
        else:
            self.report = report
        
        self.print_report = True
    #运行dex2jar 反编译dex文件
    def dex2jar(self, force=False):

        java_dir = self.get_java_dir()
        rmdir(java_dir, force)
        os.mkdir(java_dir)

        #self.do_cmd(ass_config.cmd_anprohelper+" d -r -s -f "+self.anprohelper_src_dst(self.apk_file, self.apk_file+".java"))
        sleep(2)

        smali_dir = self.get_smali_dir()

        index = 1
        for parent, dirnames, filenames in os.walk(smali_dir):
            for fileName in filenames:
                if '.dex' in fileName:
                    jar_path = os.path.join(java_dir, "classes-dex2jar-" + str(index) + ".jar")
                    self.do_cmd(ass_config.cmd_dex2jar + " --force \"" + os.path.join(smali_dir,fileName) + "\" -o " + jar_path)
                    self.do_cmd(ass_config.cmd_jar2java + " " + jar_path + " \"" + os.path.join(java_dir,"java") + "\"", True)
                    index+=1


    #使用anprohelper 反编译apk源码
    def anprohelper_src_dst(self, src, dst):#获取源码
        return q(src)+' -o '+q(dst)
    #使用anprohelper 获取源码smali
    def smali(self, force=False):#获取源码smali
        self.smali_dir =self.apk_file+".smali" 
        #rmdir(self.smali_dir, force)
            
        if not os.path.exists(self.smali_dir):
            self.do_cmd(ass_config.cmd_anprohelper+" d -r -f "+self.anprohelper_src_dst(self.apk_file,self.apk_file+".smali"))
    #使用anprohelper 从新编译apk
    #[dest 生成apk文件名]
    def build_apk(self, dest):#编译apk
        remove(dest)
        self.do_cmd(ass_config.cmd_anprohelper+" b -a \""+ass_config.cmd_aapt+"\" "+self.anprohelper_src_dst(self.apk_file+".smali", self.apk_file+".tmp" ))
        if os.path.exists(self.apk_file+".tmp"):
            self.do_cmd(ass_config.cmd_sign+" "+q(self.apk_file+".tmp")+" "+q(dest))
            remove(self.apk_file+".tmp")

    #编清理反编译文件
    def clean(self):
        rmdir(self.apk_file+".smali", True)
        rmdir(self.apk_file+".java", True)
        rmdir(self.apk_file+".index", True)
        remove("classes-dex2jar.jar")

    def clean_index(self):
        rmdir(self.apk_file+".index", True)
        remove("classes-dex2jar.jar")

    def doRmDir(self,flag):
        rmdir(self.apk_file+flag, True)

    def doRemove(self,file):
        remove(file)

    def get_smali_dir(self):
        return self.apk_file + ".smali"
    def get_java_dir(self):
        return self.apk_file + ".java"

    #获取反编译内容       
    def get_package_info(self):#获取反编译内容
        if self.report.apk_info=='':
            self.report.apk_info = self.do_cmd(ass_config.cmd_aapt+" d badging \""+self.apk_file+"\"",True)
        return self.report.apk_info

    #获取包信息
    def get_package_base_info(self):#获取包信息
        self.get_package_info()
        package = mid_str(self.report.apk_info, "package: name='", "'")
        version = mid_str(self.report.apk_info, "versionName='", "'")
        label = mid_str(self.report.apk_info, "application-label:'", "'")
        return (package, version, label)
    
    #运行组件
    def get_launchable_activity(self):#运行组件
        return mid_str(self.get_package_info(), "launchable-activity: name='", "'")

    #获取主配置文件信息
    #[apk apk文件路径]
    def get_manifest(self, apk):#获取主配置文件
        axml = os.path.join(self.smali_dir, "AndroidManifest.xml")
        return self.do_cmd(ass_config.cmd_axml+" "+q(axml),True)

    #获取主配置文件信息
    #[apk apk文件路径] [out 输出路径]
    def get_all_activity(self, apk, out=''):#获取组件信息
        acts = []
        
        if len(out)==0:
            out = self.get_manifest(apk)
            
        acts_str = out.split("<activity")
        
        for i in range(1, len(acts_str)):
            act = mid_str(acts_str[i], "android:name=\"", "\"")
            if act=='':
                continue
                
            if act[0]=='.':
                act = apk+act
            
            acts.append(act)
                    
        return acts

    #执行cmd
    ##[cmdline 命令字符] [print_out 是否输出] [timeout 超时]
    #def do_cmd(self, cmdline, print_out=True, timeout=0):#执行cmd
    #    #cmdline = unicode(cmdline,"utf8")
    #    print("++++ [ CMD ] %s  " %cmdline)
    #    p=subprocess.Popen(cmdline, bufsize=0, shell=True, universal_newlines=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #    if timeout>0:
    #        t = Timer(timeout, to_kill(p))
    #        t.start()
    #    out = ''
    #    err = ''
    #    try:
    #        out,err = p.communicate()
    #    except:
    #        out = ''
    #        err = ''
            
    #    if print_out:
    #        #全部输出
    #        print(out)
    #    else:
    #        #截取输出
    #        if len(out)> 200:
    #            print(out[0:200])
    #        else:
    #            print(out)
    #    if timeout>0:
    #        t.cancel()
    #    return out

    #执行cmd linux 平台支持超时
    def handler(self,signum, frame):
        raise AssertionError

    def do_cmd(self, cmdline, print_out=True, timeout=60):#执行cmd
        #cmdline = unicode(cmdline,"utf8")
        print("++++ [ CMD ] [%d] %s  " %(timeout,cmdline))
        t_start = datetime.now()
        p=subprocess.Popen(cmdline, bufsize=0, shell=True, universal_newlines=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:

            try:
                out,err = p.communicate()
            except:
                out = ''
                err = ''

        except AssertionError:
            p.terminate()
            print('timeout')
            out = 'timeout'

        #输出命令执行时间
        print("++++ [EXE TIME] %d secs" % ((datetime.now() - t_start).total_seconds()))
        #输出控制
        if print_out:
            #全部输出
            print(out)
        else:
            #截取输出
            if len(out)> 200:
                print(out[0:200])
            else:
                print(out)
        return out

    #执行cmd linux 平台支持超时
    #[cmdline 命令字符] [print_out 是否输出] [timeout 超时] 
    def do_cmd_linux(self, cmdline, print_out=True, timeout=3600):#执行cmd
        #cmdline = unicode(cmdline,"utf8")
        print("++++ [ CMD ] [%d] %s  " %(timeout,cmdline))
        t_start = datetime.now()
        p=subprocess.Popen(cmdline, bufsize=0, shell=True, universal_newlines=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            signal.signal(signal.SIGALRM, self.handler)
            signal.alarm(timeout)
            try:
                out,err = p.communicate()
            except:
                out = ''
                err = ''
            signal.alarm(0)
        except AssertionError:
            p.terminate()
            print('timeout')
            out = 'timeout'

        #输出命令执行时间
        print("++++ [EXE TIME] %d secs" % ((datetime.now() - t_start).total_seconds())) 
        #输出控制
        if print_out:
            #全部输出
            print(out)
        else:
            #截取输出
            if len(out)> 200:
                print(out[0:200])
            else:
                print(out)
        return out


    #使用socket 发送修复指令，重启虚拟机
    def restart_avd(self):
        HOST='127.0.0.1'
        PORT=4405
        s = None
        res = ""
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)      #定义socket类型，网络通信，TCP
            s.connect((HOST,PORT))       #要连接的IP与端口
            s.sendall("restart_avd")      #把命令发送给对端
            data=s.recv(1024)     #把接收的数据定义为变量
            res = data         #输出变量
            s.close()   #关闭连接
        except:
            res = "socket error"
        if s != None:
            s.close()
        print res
        if res.find("open_ok") >=0:
            #重启成功
            return True
        return False

    #修复adb连接
    def adb_repair(self):
        self.report.LOG_OUT("start repair adb")
        adbs = " "
        if len(ass_config.adb_server)>0:
            adbs = " -s "+q(ass_config.adb_server)+" "
        self.do_cmd(ass_config.cmd_adb+adbs+"kill-server")
        time.sleep(2)
        res = self.do_cmd(ass_config.cmd_adb+adbs+"start-server")
        res = self.do_cmd(ass_config.cmd_adb+adbs+"shell aa")
        if res.find("error: device offline") >=0:
            # #修复失败
            # #--- 进一步处理
            # self.report.LOG_OUT("restart avd")
            # #使用socket 发送修复指令，重启虚拟机
            # return self.restart_avd()
            return False
        return True
    #连接adb
    def connect_adb(self):#连接adb
        if len(ass_config.adb_server)>0:
            self.do_cmd(ass_config.cmd_adb+" connect \""+ass_config.adb_server+"\"")


    def kill_process_by_name(self, packageName ,startActivity = None):
        cmd = ""
        cmds = []
        try:
            # 获取进程PID
            apk = packageName
            res = self.adb("shell \"ps | grep '" + apk + "'\"")
            if len(res) > 0:
                pids = res.split("\n")

                for pid in pids:
                    if pid.find(apk) > 0:
                        cmds.append("kill -9 " + split_empty(pid, " ", 1))

        except:
            traceback.print_exc()

        # 是否从重启
        if startActivity != None:
            cmds.append("am start -n "+ startActivity)

        if len(cmds)>0:
            cmd = "shell \"" + ' | '.join(cmds) + "\""
            self.adb(cmd)

    #连接adb   
    def adb(self, cmd, timeout=200):#连接adb
        adbs = " "
        if len(ass_config.adb_server)>0:
            adbs = " -s "+q(ass_config.adb_server)+" "
        res = self.do_cmd(ass_config.cmd_adb+adbs+cmd, True, timeout)
        if res.find("device offline")>0:
            #修复adb
            res_repair = self.adb_repair()
            if res_repair:
                #修复成功继续执行
                time.sleep(2)
                return self.adb(cmd,timeout)
            else:
                #抛出异常
                raise
        return res
    #连接CAP
    #[apk 包名] [apk_file apk文件名] [activity 组件名]
    def run_cap(self, apk, apk_file, activity, step, first_uninstall=False):#运行CAP
        if first_uninstall:
            self.uninstall(apk)
        self.install(apk_file)
        self.start_apk(apk, activity)
        sleep(5)
        self.screencap(step)
        self.uninstall(apk)

    #安装apk文件
    #[apk 包名] [apk_file apk文件名]
    def install(self, apk_file):
        #安装apk文件
        if not os.path.exists(apk_file):
            return False
        
        ret = self.adb("push \""+apk_file+"\" /data/local/tmp/check.apk",600)
        ret = self.adb("shell pm install -r /data/local/tmp/check.apk",600)
        print(ret)
        if ret.find("Success")<0 and ret.find("INSTALL_FAILED_ALREADY_EXISTS")<0:
            print(self.i18n("安装失败"))
            return False
        return True

    #卸载
    #[apk 包名] [apk_file apk文件名] 
    def uninstall(self, apk):#卸载
        #关闭阻碍进程
        cmd = ""
        try:
            #获取进程PID
            apkbrowser = "com.android.browser"
            res = self.adb("shell ps | grep \""+ apkbrowser +"\"")
            if len(res)>0:
                pids = res.split("\n")
                apid = []
                for pid in pids:
                    if pid.find(apkbrowser)>0:
                        apid.append(split_empty(pid, " ", 1))

                for pid in apid:
                    cmd = cmd + "kill -9 " + pid + " | "
        except Exception,e:
            print("not kill browser")

        return self.adb("shell \"" + cmd + "pm uninstall "+apk + "\"")
        #return self.adb("uninstall "+apk)

    #运行APK
    #[apk 包名] [activity activity名]     
    def start_apk(self, apk, activity):#运行APK
        self.adb("shell am start "+apk+"/"+activity)
    #获取截图
    #[file 截图文件名]   
    def get_screencap_file(self, file):#获取截图
        return "%d_%d_%d_%d.png" % file

    #截图
    def screnncap_one(self):#截图
        n = datetime.now()
        sf = (n.hour, n.minute, n.second, n.microsecond)
        self.adb("shell /system/bin/screencap -p /data/"+self.get_screencap_file(sf))
        return sf

    #截图 [step 步骤编号]
    def screencap(self, step):
        self.adb("shell /system/bin/screencap -p /data/screenshot.png")
        self.adb("pull /data/screenshot.png \""+self.apk_file+"_"+step+".png\"")

    def drozer_repair(self):
        #repair drozer when lost session
        self.report.LOG_OUT("start repair drozer")
        cmd = ""
        try:
        #获取进程PID
            apk = "com.mwr.dz"
            res = self.adb("shell ps | grep \""+ apk +"\"")
            if len(res)>0:
                pids = res.split("\n")
                apid = []
                for pid in pids:
                    if pid.find(apk)>0:
                        apid.append(split_empty(pid, " ", 1))

                self.report.LOG_OUT("start repair drozer")

                for pid in apid:
                    cmd = cmd + "kill -9 " + pid + " | "
        except:
            import traceback
            traceback.print_exc();
        cmd =  "shell \"" + cmd + "am start -n com.mwr.dz/com.mwr.dz.activities.MainActivity" + "\""
        self.adb("forward tcp:6001 tcp:31415")
        print(cmd)
        return self.adb(cmd)

    #使用drozer [cmd 命令行]
    def drozer(self, cmd,repair_times = 3):
        cmdline = ass_config.cmd_drozer+" console connect --server "+ass_config.drozer_server+" -c \"" + cmd + "\""
        needRepair = False
        #执行drozer命令
        out = self.do_cmd(cmdline)
        if out.find("There was a problem connecting to the drozer Server")>=0:
            needRepair = True
        elif out.find("[Errno 104] Connection reset by peer")>=0:
            needRepair = True
        elif out.find("lost your drozer session")>=0:
            needRepair = True
        elif out.find("Connection refused")>=0:
            needRepair = True
        #判断是否需要修复
        if needRepair:
            if repair_times > 0:
                repair_times = repair_times - 1
                self.drozer_repair()
                time.sleep(10)
                #重新执行命令
                self.report.LOG_OUT("re dorzer cmd")
                return self.drozer(cmd,repair_times)
        return out.splitlines()    
    #获取进程PID [apk 包名]
    def get_pid(self, apk):#获取进程PID
        self.adb("shell sleep 2")
        pids = self.adb("shell ps | grep \""+apk+"\"").split("\n")
        len_apk = len(apk)
        for pid in pids:
            if pid[-len_apk:]==apk:
                return split_empty(pid, " ", 1)
        return ''

    #添加黑代码
    #[start_activity 应用启动activity] [crack_code 黑代码]
    def crack_file(self, start_activity, crack_code):#添加黑代码

        sfile = os.path.join(self.apk_file+".smali","smali", start_activity.replace(".", os.path.sep)+".smali")
        file_str = read_file(sfile)
        if file_str=='':
            return False
        
#         self.write_file(start_activity+".smali", file_str)
        
        begin_index = file_str.find(' onCreate(Landroid/os/Bundle;)V')
        if begin_index > 0:
            end_index = file_str.find('.end method', begin_index)
            end_index = file_str.rfind('return-void', begin_index, end_index)
            
#             end_index = begin_index+len(' onCreate(Landroid/os/Bundle;)V')+2
            
            new_file_str = file_str[:end_index]+crack_code+file_str[end_index:]
            
            write_file(sfile, new_file_str)
            
            return True
        return False
  
    #检测进度标识        
    def progress_total(self):
        return 1
    
    def init(self, argv):
        super(AssModule, self).init(argv)
        self.report.init(argv)
        self.report.progress_total += self.progress_total()
        self.report.apk_info = ''
        
    def run(self):
        if not os.path.exists(self.apk_file):
            return False
        
        (p,v,l) = self.get_package_base_info()
        self.report.report.basic.packageName = p
        self.report.report.basic.appVersion = v
        self.report.report.basic.appName = l

        return True

    def main(self):
        super(AssModule, self).main()
        # if self.print_report and hasattr(self, "report"):
        #     print(self.report.getReport())

            
if __name__=="__main__":
    AssModule().main()            
