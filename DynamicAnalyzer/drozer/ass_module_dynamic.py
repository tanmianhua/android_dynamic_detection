# -*- coding:utf-8 -*-

import ass_base
from ass_module import AssModule
import re
class AssDynamic(AssModule):
    #格式添加到数组
    #[arr 需添加数组] [obj 信息]
    def addArr(self, arr, obj):
        if obj=='':
            return False
        else:
            arr.append(obj)
            return True

    #获取app包信息
    def app_package_info(self):#获取包信息
        permission_begin = False
        permission_end = False
        permission_arry = []
        self.report.report.basic.packageName = self.apk
        
        lines = self.drozer("run app.package.info -a "+self.apk)
        for line in lines:
            val = ass_base.get_val(line, 'Application Label:')
            if val!='':
                self.report.report.basic.appName = val
     
            val = ass_base.get_val(line, 'Version:')
            if val!='':
                self.report.report.basic.appVersion = val
     
            index = line.find('Uses Permissions:')
            if index>=0:
                permission_begin = True
                continue
     
            index = line.find('Defines Permissions:')
            if index>=0:
                permission_end = True
             
            if permission_begin and not permission_end:
                per = line.replace('-','').strip()
                if per == '':
                    break
                else:
                    print('['+per+']')
                    permission_arry.append(per)

        if len(permission_arry)>0:
            self.report.addCheckPermission(permission_arry)

    #获取app provider信息
    def app_provider_info(self):#获取供应信息
        cp_arr = []
        
        lines = self.drozer("run app.provider.info -a "+self.apk)
        for line in lines:
            val = ass_base.get_val(line, 'Content Provider:')
            self.addArr(cp_arr, val)
        
        return cp_arr
    #获取app 攻击面信息
    def app_package_attacksurface(self):#获取攻击面信息
        attack_activities = []
        attack_receivers = []
        attack_providers = []
        attack_services = []


        attack_debuggable = False
        attacks = 0

        launchable_activity = self.get_launchable_activity()
         
        lines = self.drozer("run app.package.attacksurface "+self.apk)
        for line in lines:

            if attack_debuggable == False:
                if line.find('is debuggable')>=0:
                    attack_debuggable = True

            val = ass_base.get_val(line, 'activities exported', False)
            if val != '' and int(val)>0:
                self.addArr(attack_activities,line)
           
            val = ass_base.get_val(line, 'broadcast receivers exported', False)
            if val != '' and int(val)>0:
                self.addArr(attack_receivers,line)
               
            val = ass_base.get_val(line, 'content providers exported', False)
            if val != '' and int(val)>0:
                self.addArr(attack_providers,line)
        
            val = ass_base.get_val(line, 'services exported', False)
            if val != '' and int(val)>0:
                self.addArr(attack_services,line)
        
        if len(attack_activities) > 0:
            # 获取activity信息
            self.app_export_activity_info(launchable_activity)

        if len(attack_receivers) > 0:
            self.app_export_broadcast_info()

        # if len(attack_providers) > 0:
        #     self.app_content_info()

        if len(attack_services) > 0:
            self.app_export_service_info()
    
        if attack_debuggable == True:
            # C2017040012 应用安全 反调试保护
            self.report.addCheckItem('C2017040012', [])

    # 获取app Broadcast信息
    def app_export_broadcast_info(self):  # 获取组件信息
        act_begin = False
        act_arr = []


        index = 1

        lines = self.drozer("run app.broadcast.info -a " + self.apk)
        for line in lines:
            if line.find("Package:") >= 0:
                act_begin = True
                continue

            info = line.strip()

            if act_begin:
                if index == 1:
                    index = 0
                    if not self.addArr(act_arr, info):
                        break
                else:
                    index = 1

        if len(act_arr) > 0:
            #C2017040005	应用安全	Broadcast Receiver安全
            self.report.addCheckItem('C2017040005', act_arr)

    # # 获取app Content信息
    # def app_content_info(self):  # 获取组件信息
    #     act_begin = False
    #     act_arr = []
    #
    #     act = self.get_launchable_activity()
    #
    #     index = 0
    #
    #     lines = self.drozer("run app.content.info -a " + self.apk)
    #     for line in lines:
    #         if line.find("Package:") >= 0:
    #             act_begin = True
    #             continue
    #
    #         info = line.strip()
    #
    #         if act_begin and act != info:
    #             if index == 1:
    #                 index = 0
    #                 if not self.addArr(act_arr, line.strip()):
    #                     break
    #             else:
    #                 index = 1
    #
    #     if len(act_arr) > 0:
    #         #C2017040007	应用安全	Content Provider安全
    #         self.report.addCheckItem('C2017040007', act_arr)

    # 获取app service信息
    def app_export_service_info(self):  # 获取组件信息
        act_begin = False
        act_arr = []

        index = 1

        lines = self.drozer("run app.service.info -a " + self.apk)
        for line in lines:
            if line.find("Package:") >= 0:
                act_begin = True
                continue

            info = line.strip()

            if act_begin:
                if index == 1:
                    index = 0
                    if not self.addArr(act_arr, info):
                        break
                else:
                    index = 1

        if len(act_arr) > 0:
            #C2017040006	应用安全	Service安全
            self.report.addCheckItem('C2017040006', act_arr)

    #获取app activity信息  
    def app_export_activity_info(self,launchable_activity):#获取组件信息
        act_begin = False
        act_arr = []

        act = launchable_activity

        index = 0

        lines = self.drozer("run app.activity.info -a "+self.apk)
        for line in lines:
            if line.find("Package:")>=0:
                act_begin = True
                continue

            info = line.strip()

            if act_begin and act != info:
                if index == 1:
                    index = 0
                    if not self.addArr(act_arr, line.strip()):
                        break
                else:
                    index = 1

        if len(act_arr)>0:
            # C2017040004	应用安全	Activity安全
            self.report.addCheckItem('C2017040004', act_arr)

        #self.report.addArrItem(act_arr, '应用存在高风险未被授权外部调用风险。此类应用暴露的活动可以通过后台静默方式被激发启用产生暴露关键或隐私数据风险。')
        
        return act_arr
    #外部启动app的activity  [activity app的activity名] 
    def app_activity_start(self, activity):#启动程序
        lines = self.drozer("run app.activity.start --component "+self.apk+" "+activity)
        for line in lines:
            val = ass_base.get_val(line, "Unable")
            if val == '':
                return False
        return True

    #三 应用资源风险评估
    def scanner_provider_finduris(self):
        all_uris = []
        access_uris = []
        uri_begin = False
        
        lines = self.drozer("run scanner.provider.finduris -a "+self.apk)
        for line in lines:
            val = ass_base.get_val(line, "to Query ")
            if val != '':
                try:
                    all_uris.index(val, )
                except ValueError:
                    all_uris.append(val)

                continue
            
            if line.find("Accessible content URIs:") >= 0:
                uri_begin = True
                continue
            
            if uri_begin:
                self.addArr(access_uris, line.strip())

        if len(access_uris)>0:

            # C2017040033	Content Provider URI脆弱点
            self.report.addCheckItem('C2017040033', access_uris)
        
        return all_uris, access_uris
    #请求uri [uri 应用内uri]
    def app_provider_query(self, uri):
        lines = self.drozer("run app.provider.query "+uri+" --projection \\\"'\\\"")
    #通过uri读取/etc/hosts [uri 应用内uri]       
    def app_provider_read(self, uri):
        lines = self.drozer("run app.provider.read "+uri+"/etc/hosts")
    #通过uri下载/etc/hosts [uri 应用内uri] 
    def app_provider_download(self, uri):
        lines = self.drozer("run app.provider.download "+uri+"/etc/hosts ./hosts")
        
    #四 应用注入风险评估  
    def scanner_provider_injection(self):
        ip_begin = False
        is_begin = False
        
        ip_arr = []
        is_arr = []
        
        lines = self.drozer("run scanner.provider.injection -a "+self.apk)
        for line in lines:
            if line.find("Injection in Projection:")>=0:
                ip_begin = True
                continue
            
            if line.find("Injection in Selection:")>=0:
                is_begin = True
                continue
        
            if ip_begin and not is_begin:
                if line.find("No ")<0:
                    self.addArr(ip_arr, line.strip())
                continue

            if is_begin:
                if line.find("No ")<0:
                    self.addArr(is_arr, line.strip())

        if len(ip_arr)>0:
            # C2017040035 反射漏洞注入风险
            self.report.addCheckItem('C2017040035', ip_arr)

        if len(is_arr)>0:
            # C2017040036 选择漏洞注入风险
            self.report.addCheckItem('C2017040036', is_arr)
            
        return ip_arr, is_arr
    #应用存在脆弱点风险检测
    def scanner_provider_traversal(self):
        vp_begin = False
        vp_arr = []
        
        lines = self.drozer("run scanner.provider.traversal -a "+self.apk)
        for line in lines:
            if line.find("Vulnerable Providers:")>=0:
                vp_begin = True
                continue
            
            if vp_begin:
                if line.find("No ")>=0:
                    break
                else:
                    self.addArr(vp_arr, line.strip())

        if len(vp_arr) > 0:
            # C2017040032	数据安全	Content Provider 目录遍历脆弱点
            self.report.addCheckItem('C2017040032', vp_arr)
        return vp_arr
    #检查sqlite是否加密
    def app_sqlite_isEnc(self):#检查sqlite是否加密
        lines = self.adb("shell ls data/data/"+ self.apk +"/databases")
        lines = lines.splitlines()
        dbfiles = []
        sql_arr = []

        dbSerach = re.compile(r'\.db$')
        encSerach = re.compile(r'encrypt') #如果加密 Error:file is encrypted or is not database
        for line in lines:
            if dbSerach.search(line):
                dbfiles.append(line)
        for dbfile in dbfiles:
            res = self.adb("shell sqlite3 /data/data/"+ self.apk +"/databases/"+ dbfile + " \".table\"")
            if not encSerach.search(res):
                self.addArr(sql_arr, "["+dbfile.strip() + "] ")

        if len(sql_arr) > 0:
            # C2017040030	数据安全	存储数据检查
            self.report.addCheckItem('C2017040030', sql_arr)
        #self.report.addArrItem(sql_arr, '应用本地sqlite存储文件未加密处理')



    def progress_total(self):
        return 12
        
    def run(self):             
        self.adb("kill-server")
        #获取apk package name
        self.report.progress("获取包名")
        apk = ''
        ret = self.get_package_info()
        lines = ret.splitlines()
        if len(lines)>0:
            apk = ass_base.get_val(lines[0], "package: name='")
            apk = ass_base.get_val(apk, "' version", False)
        
        if apk == '':
            print(self.i18n('无法获取包名'))
            return 2

        self.report.progress("安装程序")
        self.apk = apk   
        self.connect_adb()
        self.adb("forward tcp:6001 tcp:31415")
        #启动程序完成必要初始化
        self.report.progress("启动程序")
        start_activity = self.get_launchable_activity()
        self.start_apk(apk, start_activity)
               
        #获取包信息
        self.report.progress("获取包信息")
        self.app_package_info()


         #扫描非法uri
        self.report.progress("扫描非法uri")
        all_uri, access_uri = self.scanner_provider_finduris()

        #扫描注入信息
        self.report.progress("扫描注入信息")
        self.scanner_provider_injection()
        #扫描数据
        self.report.progress("扫描数据")
        self.scanner_provider_traversal()
        # #获取服务信息

        pid = self.get_pid(apk)
        if len(pid)!=0:
            #判断sqlite文件是否加密
            self.report.progress("获取sqlite信息")      
            self.app_sqlite_isEnc()

        # #检测攻击面
        # self.report.progress("检测导出组件及拒绝服务器")
        # self.run_app_package_deny()
        #
        # self.uninstall(apk)


if __name__=="__main__":
    AssDynamic().main()
