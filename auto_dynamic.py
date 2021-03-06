# -*- coding: utf8 -*-

import os

import sys

from DynamicAnalyzer.drozer.ass_report import AssReport
from DynamicAnalyzer.drozer.ass_module_dynamic import AssDynamic
from DynamicAnalyzer.drozer.ass_module_deny import AssDeny
import shutil
import MobSF.settings as SETTINGS
os.environ.update({"DJANGO_SETTINGS_MODULE": "MobSF.settings"})
from DynamicAnalyzer.pyWebProxy.pywebproxy import Proxy
from DynamicAnalyzer.views.android.android_avd import avd_load_wait
from DynamicAnalyzer.views.android.android_avd import refresh_avd
from DynamicAnalyzer.views.android.android_dyn_shared import connect
from DynamicAnalyzer.views.android.android_dyn_shared import install_and_run
from DynamicAnalyzer.views.android.android_dyn_shared import web_proxy
from DynamicAnalyzer.views.android.android_dyn_shared import get_identifier
from DynamicAnalyzer.views.android.android_virtualbox_vm import refresh_vm
import json
from mass_static_analysis import genMD5
from MobSF.utils import getADB
import signal
from StaticAnalyzer.views.android.manifest_analysis import get_manifest
from StaticAnalyzer.views.android.manifest_analysis import manifest_data as get_manifest_data
from StaticAnalyzer.views.shared_func import Unzip
import subprocess
import time
import traceback
from Analysis_x_logcat.analysis import analysis_x_logcat


BASE_DIR = './'
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads/')
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads/')
DYNAMIC_TOOL_DIR = os.path.join(BASE_DIR, 'DynamicAnalyzer/tools/')
STATIC_TOOL_DIR = os.path.join(BASE_DIR, 'StaticAnalyzer/tools/')


def get_static_info(file_path):

    file_md5 = genMD5(file_path)
    print 'file_md5:', file_md5
    
    unzip_dir = UPLOAD_DIR + file_md5 + '/'
    unzip_result = Unzip(file_path, unzip_dir)
    print 'len(unzip_result):', len(unzip_result)
    
    apk_path = unzip_dir + 'app.apk'
    shutil.copy(file_path, apk_path)
    
    manifest_xml = get_manifest(unzip_dir, STATIC_TOOL_DIR, '', True)
    print 'manifest_xml:', manifest_xml
    
    manifest_data = get_manifest_data(manifest_xml)
    print 'manifest_data["packagename"]:', manifest_data['packagename']
    print 'manifest_data["application_name"]:', manifest_data['application_name']
    print 'manifest_data["mainactivity"]:', manifest_data['mainactivity']
    
    manifest_data['file_md5'] = file_md5
    manifest_data['apk_path'] = apk_path
    return manifest_data

def init_environment(adb):
    Proxy('', '', '', '')
    if SETTINGS.ANDROID_DYNAMIC_ANALYZER == "MobSF_REAL_DEVICE":
        print "\n[INFO] MobSF will perform Dynamic Analysis on real Android Device"
    elif SETTINGS.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
        # adb, avd_path, reference_name, dup_name, emulator
        refresh_avd(adb, SETTINGS.AVD_PATH, SETTINGS.AVD_REFERENCE_NAME,
                    SETTINGS.AVD_DUP_NAME, SETTINGS.AVD_EMULATOR)
    else:
        # Refersh VM
        refresh_vm(SETTINGS.UUID, SETTINGS.SUUID, SETTINGS.VBOX)
    return

def set_web_proxy(file_md5):
    app_dir = UPLOAD_DIR + file_md5 + '/'
    if SETTINGS.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
        proxy_ip = '127.0.0.1'
    else:
        proxy_ip = SETTINGS.PROXY_IP  # Proxy IP
    port = str(SETTINGS.PORT)  # Proxy Port
    web_proxy(app_dir, proxy_ip, port)
    return

def connect_device(adb):
    # AVD only needs to wait, vm needs the connect function
    if SETTINGS.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
        if not avd_load_wait(adb):
            print "\n[WARNING] ADB Load Wait Failed"
            exit()
    else:
        connect(DYNAMIC_TOOL_DIR)
    return


# monkey script 测试
def monkey_script_test(adb, app_info):
    monkey_script_pattern = '''
    type=user
    count=10
    speed=1.0
    start data >>
    captureDispatchPointer(0,0,0,200,600,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,200,600,1,1,-1,1,1,0,0)
    UserWait(1000)
    captureDispatchPointer(0,0,0,400,600,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,400,600,1,1,-1,1,1,0,0)
    UserWait(1000)
    captureDispatchPointer(0,0,0,600,600,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,600,600,1,1,-1,1,1,0,0)
    UserWait(1000)
    captureDispatchPointer(0,0,0,200,800,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,200,800,1,1,-1,1,1,0,0)
    UserWait(1000)
    captureDispatchPointer(0,0,0,600,1000,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,600,1000,1,1,-1,1,1,0,0)
    UserWait(3000)
    LaunchActivity({packagename}, {mainactivity})
    UserWait(5000)
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    Drag({screen_x_right},{screen_y_middle},{screen_x_left},{screen_y_middle},70)
    UserWait({drag_wait})
    captureDispatchPointer(0,0,0,{screen_x_middle},100,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},100,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,0,{screen_x_middle},200,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},200,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,0,{screen_x_middle},300,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},300,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,0,{screen_x_middle},400,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},400,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,0,{screen_x_middle},500,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},500,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,0,{screen_x_middle},600,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},600,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,0,{screen_x_middle},700,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},700,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,0,{screen_x_middle},800,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},800,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,0,{screen_x_middle},900,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},900,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,0,{screen_x_middle},1000,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},1000,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,0,{screen_x_middle},1100,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},1100,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,0,{screen_x_middle},1200,1,1,-1,1,1,0,0)
    captureDispatchPointer(0,0,1,{screen_x_middle},1200,1,1,-1,1,1,0,0)
    UserWait(1000)
    captureDispatchPress(4)
    captureDispatchPress(4)
    captureDispatchPress(4)
    '''
    drag_wait = 750
    packagename = app_info['packagename']
    mainactivity = app_info['mainactivity']
    if mainactivity.startswith('.'):
        mainactivity = packagename + mainactivity
    screen_x_right = 750
    screen_y_middle = 640
    screen_x_left = 50
    screen_x_middle = 400
    
    monkey_script_data = monkey_script_pattern.format(drag_wait=drag_wait, 
        packagename=packagename, mainactivity=mainactivity, 
        screen_x_right=screen_x_right, screen_y_middle=screen_y_middle, 
        screen_x_left=screen_x_left, screen_x_middle=screen_x_middle)
    
    monkey_script_file_name = os.path.join(os.path.join(UPLOAD_DIR, app_info['file_md5']), 'monkey_script.txt')
    with open(monkey_script_file_name, 'w') as f:
        f.write(monkey_script_data)
    
    subprocess.call([adb,
                     "-s",
                     get_identifier(),
                     "push",
                     monkey_script_file_name,
                     "/data/local/tmp"])
    subprocess.call([adb,
                     "-s",
                     get_identifier(),
                     "shell",
                     "monkey", "-f", 
                     "/data/local/tmp/monkey_script.txt", "1"])
    print u'\n[INFO] 跳过初始化界面'
    return

def auto_app_test(adb, app_info, file_path):

    print u'\n[INFO] 开始自动化测试...'
    
    # monkey script 测试，用于进入初始化界面
    monkey_script_test(adb, app_info)
    
    packagename = app_info['packagename']
    # monkey 测试，输出太多，重定向输出
    p = subprocess.Popen([adb, '-s', get_identifier(), 'shell', 
                'monkey', '-p', packagename, 
                '--ignore-crashes', '--ignore-timeouts', 
                '--throttle 300', '--pct-touch 30', '--pct-motion 70',
                '-v', '-v', '-v', '1000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 设置超时检查
    start_time = time.time()
    while True:
        if p.poll() is not None:
            #useless_out, useless_err = p.communicate()
            break
        if time.time() - start_time > 60:
            p.terminate()
            break
        time.sleep(0.5)

    #  TODO: 添加其他测试方法
    print u'\n[INFO] 开始drozer测试...'
    try:
        report = AssReport()
        report.modules.append(AssDynamic(report))
        report.modules.append(AssDeny(report))
        report.main()
        out_path = file_path + ".result"
        report.out_JSON_file(out_path)
    except:
        traceback.print_exc()
    return

def download_logs(adb, download_dir):
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)
    subprocess.call([adb,
                     "-s",
                     get_identifier(),
                     "pull",
                     "/data/data/de.robv.android.xposed.installer/log/error.log",
                     download_dir + "x_logcat.txt"])
    print "\n[INFO] Downloading Droidmon API Monitor Logcat logs"
    # TODO: 下载其他有用文件
    return

def dynamic_main(file_path):
    app_info = get_static_info(file_path)
    
    # 开始动态分析
    adb = getADB(DYNAMIC_TOOL_DIR)
    init_environment(adb)
    
    set_web_proxy(app_info['file_md5'])
    
    connect_device(adb)
    
    # Change True to support non-activity components
    install_and_run(DYNAMIC_TOOL_DIR, app_info['apk_path'], app_info['packagename'], app_info['mainactivity'], True)
    time.sleep(15)    
    auto_app_test(adb, app_info, file_path)
    download_dir = DOWNLOAD_DIR + app_info['file_md5'] + '/'
    download_logs(adb, download_dir)
    
    result = analysis_x_logcat(download_dir + 'x_logcat.txt', app_info)
    print u'分析结果目录：', download_dir
    return result

def print_x_log_analysis_result(result):
    print u'\n检测到敏感行为：'
    print json.dumps(result['sensitives'], indent=4, ensure_ascii=False)
    
    print u'\n检测到漏洞：'
    print json.dumps(result['vulnerabilities'], indent=4, ensure_ascii=False)
    return

def test_dynamic(file_path):
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]
    print 'file_path:', file_path
    result = dynamic_main(file_path)
    print_x_log_analysis_result(result)
    return

if __name__ == '__main__':

    if len(sys.argv) is not 1:
        try:
            file_path = sys.argv[1] + '1.apk'
            test_dynamic(file_path)
        except Exception as err:
            print traceback.format_exc()
        os.kill(os.getpid(), signal.SIGTERM)
    else:
        print 'python whatever.py [APK_FILE]'

