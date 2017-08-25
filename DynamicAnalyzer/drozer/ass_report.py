# -*- coding: utf-8 -*-
'''
'''
import json
import ass_base

import sys,os,time,traceback
from jsonParser import JsonParser


reload(sys)
sys.setdefaultencoding( "utf-8" )


class AssEncoder(json.JSONEncoder):
    def default(self,obj):
        #convert object to a dict
        d = {}
        #d['__class__'] = obj.__class__.__name__
        #d['__module__'] = obj.__module__
        d.update(obj.__dict__)
        return d

class AssDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self,object_hook=self.dict2object)
    def dict2object(self,d):
        #convert dict to object
        if'__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            module = __import__(module_name)
            class_ = getattr(module,class_name)
            args = dict((key.encode('ascii'), value) for key, value in d.items()) #get args
            inst = class_(**args) #create new instance
        else:
            inst = d
        return inst

class Basic:
    def __init__(self):
        self.appName = ''
        self.appVersion = ''
        self.packageName = ''

class Result:
    def __init__(self):
        self.lastValue=0
        self.evaAdvice=''

class List:
    def __init__(self):
        self.items = []
        self.type = ''

class Items:
    def __init__(self):
        self.checkMethod=''
        self.checkName=''
        self.checkResult=''
        self.relatedCode=''
        self.resultComment=''

        self.id = ''
        self.detail = ''


class Report:
    def __init__(self):
        self.basic = Basic()
        self.list = [List()]
        self.result = Result()
#检测报告生成模块
class AssReport(ass_base.AssI18n):
    def __init__(self):
        self.modules = []
        self.apk_file = ''
        self.language = ''
        self.apk_info = ''
        self.inited = False
        self.title = 'APP风险评估报告' #标题

        self.result = {}
        self.result['leak']={}
        self.result['permission']={}

        # 白名单  包及子包放行
        self.white_list = ['/com/tencent/', '/com/baidu/', '/com/alipay/', '/com/unionpay/', '/cn/jpush/', '/com/ali/','/cn/sharesdk/','/org/']

    #判断是否属于白名单
    def is_in_white_list(self,str):
        for item in self.white_list:
            if str.find(item)>=0:
                return True
        return False


    def addCheckItemSingle(self, id, value):

        if self.is_in_white_list(value) == False:
            try:
                nofind = True
                if self.result['leak'].has_key(id) == False:
                    self.result['leak'][id] = []
                for d in self.result['leak'][id]:
                    if value == d:
                        nofind = False
                        break
                if nofind:
                    self.result['leak'][id].append(value)
            except:
                self.LOG_OUT("add error")

            self.LOG_OUT("find risk:" + id)

    def addCheckItem(self, id, values):
        try:
            if values == []:
                if self.result['leak'].has_key(id) == False:
                    self.result['leak'][id] = []
            else:
                for e in values:
                    if self.is_in_white_list(e) == False:
                        nofind = True
                        if self.result['leak'].has_key(id) == False:
                            self.result['leak'][id] = []
                        for d in self.result['leak'][id]:
                            if e == d:
                                nofind = False
                                break
                        if nofind:
                            self.result['leak'][id].append(e)
        except:
            self.LOG_OUT("add error")

        self.LOG_OUT("find risk:" + id)

    def addCheckPermission(self, permission):
        if any(self.result['permission']) == False:
            self.result['permission']['permission'] = permission


    def out_json(self,data,out_json_file):

        try:
            json_obj = JsonParser()
            json_obj.update(data)

            jsonStr = json_obj.dump()
            # jsonStr = json.dumps(self.result)

            self.LOG_OUT("out put :" + out_json_file)

            fl = open(out_json_file, 'w')
            fl.write(jsonStr)
            fl.close()
        except:
            traceback.print_exc()
            self.ERROR('out json error')

    def out_JSON_file(self, outPath):

        self.out_json(self.result['leak'], outPath + os.path.sep + "drozer_result.json")
        if any(self.result['permission']):
            self.out_json(self.result['permission'],outPath + os.path.sep + "permission_result.json")


    #输出当前进度
    def progress(self, subject, bFinish=False):
        self.progress_value+=1
        if self.progress_value >= self.progress_total or bFinish:
            self.progress_value = self.progress_total
        #输出进度
        #print("======= progress,%d%%,%s ============================"%(self.progress_value*100/self.progress_total, self.i18n(subject)))
        print("======= progress,%d%%,%s ============================"%(self.progress_value*100/self.progress_total, subject))

    #输出当前错误信息
    def ERROR(self, msg):
        print("**** [ ERROR ] %s ***" %msg)

    #输出运行信息
    def LOG_OUT(self, msg):
        print("---- [ LOG ] %s --- " %msg)

    def init(self, argv):
        if self.inited:
            return
        self.inited = True

        super(AssReport, self).init(argv)
        #攻击检查
        self.report = Report()
        self.report.list[0].type=self.i18n('攻击检查')

        self.progress_value = 0
        self.progress_total = 0

        for module in self.modules:
            module.init(argv)

    def run(self):

        self.LOG_OUT("====Check Start %s" % time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())))

        for module in self.modules:
            moduleName = str(module.__class__.__name__)

            self.LOG_OUT('run '+ moduleName)

            try:
                module.run()
                self.LOG_OUT("run over " + moduleName)
            except:
                traceback.print_exc()
                self.ERROR("except "+ moduleName)


        self.LOG_OUT( "====Check End %s" % time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())))
        self.progress("扫描完成", True)
