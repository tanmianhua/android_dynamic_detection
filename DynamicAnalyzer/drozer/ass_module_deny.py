# -*- coding:utf-8 -*-
import ass_base
from ass_module import AssModule

import re,time,json,traceback
from socket import *

class AssDeny(AssModule):
    #格式添加到数组
    #[arr 需添加数组] [obj 信息]
    def addArr(self, arr, obj):
        print "add " +obj
        if obj=='':
            return False
        else:
            arr.append(obj)
            return True

    #检测组件及拒绝服务
    def run_app_package_deny(self):

        attack_deny = []

        act = self.get_launchable_activity()

        lines = self.drozer("run app.package.deny " + self.apk)
        for line in lines:
            if line.find("|") >= 0:
                info  = line.split("|")
                if len(info)>2:

                    if act != info[2]:
                        if info[0] == 'act':
                            if info[1] == 'activity':
                                self.addArr(self.attack_activities, info[2])
                            elif info[1] == 'receiver':
                                self.addArr(self.attack_receivers, info[2])
                            elif info[1] == 'service':
                                self.addArr(self.attack_services, info[2])
                            elif info[1] == 'provider':
                                self.addArr(self.attack_providers, info[2])
                        elif info[0] == 'deny':
                            self.addArr(attack_deny, info[2])

    def progress_total(self):
        return 12

    def start_app(self,package,startActivity):
        cmd = "shell am start -n "+package + "/" + startActivity
        self.adb(cmd)

    def init_agent(self):
        #repair drozer when lost session
        #self.kill_process_by_name("com.harvey.scanagent","com.harvey.scanagent/.MainActivity")
        self.start_app("com.harvey.scanagent",".MainActivity")

    def send_check_intent(self,act,array_params):
        HOST = '127.0.0.1'
        PORT = 6010

        ADDR = (HOST, PORT)


        client = socket(AF_INET, SOCK_STREAM)
        client.connect(ADDR)


        try:
            if (client != None):
                array_params['act'] = act
                data_string = json.dumps(array_params) + "\n"
                client.send(data_string.encode('utf8'))
                data = client.recv(1024)
                print "recv: " + data
                res = eval(data)
                return res

        except:
            traceback.print_exc()
            print 'error'

        return None

    def doCheck(self,act,type):

        self.init_agent()

        time.sleep(1)

        # # # 关闭需要检测的应用
        # self.kill_process_by_name(self.apk)
        # #
        intent = {}
        intent['type'] = type
        intent['packageName'] = self.apk
        intent['className'] = act
        #
        intent['mod'] = "null"
        res = self.send_check_intent('IntentFuzzer', intent)
        if (res != None) and (res['code'] == 0) and (res['info'] == "ok:1"):
            print "find deny :"
            self.addArr(self.attack_deny, act)
            self.kill_process_by_name(self.apk)
            return
        else:
            print "not deny"

        time.sleep(1)

        self.init_agent()

        time.sleep(1)

        # 关闭需要检测的应用
        self.kill_process_by_name(self.apk)

        #
        intent['mod'] = "se"
        res = self.send_check_intent('IntentFuzzer', intent)
        if (res != None) and (res['code'] == 0) and (res['info'] == "ok:1"):
            print "find deny :"
            self.addArr(self.attack_deny, act)
        else:
            print "not deny"

        self.kill_process_by_name(self.apk)

    def run(self):

        #获取apk package name
        self.report.progress("获取包名")
        self.apk = ''
        ret = self.get_package_info()
        lines = ret.splitlines()
        if len(lines)>0:
            self.apk = ass_base.get_val(lines[0], "package: name='")
            self.apk = ass_base.get_val(self.apk, "' version", False)
        
        if self.apk == '':
            print(self.i18n('无法获取包名'))
            return 2

        try:


            self.attack_activities = []
            self.attack_receivers = []
            self.attack_providers = []
            self.attack_services = []

            self.attack_deny = []

            #检测导出组件
            self.adb("forward tcp:6001 tcp:31415")
            self.run_app_package_deny()

            self.adb("forward tcp:6010 tcp:30000")

            if len(self.attack_activities) > 0:
                # C2017040004	应用安全	Activity安全
                self.report.addCheckItem('C2017040004', self.attack_activities)

            if len(self.attack_receivers) > 0:
                # C2017040005	应用安全	Broadcast Receiver安全
                self.report.addCheckItem('C2017040005', self.attack_receivers)

            if len(self.attack_providers) > 0:
                # C2017040007	应用安全	Content Provider安全
                self.report.addCheckItem('C2017040007', self.attack_providers)

            if len(self.attack_services) > 0:
                # C2017040006	应用安全	Service安全
                self.report.addCheckItem('C2017040006', self.attack_services)

            for act in self.attack_activities:
                self.doCheck(act,"activity")
                time.sleep(1)

            for act in self.attack_services:
                self.doCheck(act,"service")
                time.sleep(1)

            for act in self.attack_receivers:
                self.doCheck(act,"receiver")
                time.sleep(1)

            if len(self.attack_deny)>0:
                # C2017040003	应用安全	本地拒绝服务
                self.report.addCheckItem('C2017040003', self.attack_deny)

        except:
            traceback.print_exc()






