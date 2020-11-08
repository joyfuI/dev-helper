# -*- coding: utf-8 -*-
#########################################################
# python
import os
import sys
import subprocess
import traceback
import platform
import glob
import shutil
import requests
import json
from threading import Thread
import sqlite3
from collections import OrderedDict

# third-party
import lxml.html

# sjva 공용, 패키지
from framework import path_data, app, celery
from framework.util import Util
#########################################################

class Logic(object):
    @staticmethod
    def plugin_load():
        # 편의를 위해 json 파일 생성
        from .plugin import plugin_info
        Util.save_from_dict_to_json(plugin_info, os.path.join(os.path.dirname(__file__), 'info.json'))

    @staticmethod
    def plugin_unload():
        pass

#########################################################

    @staticmethod
    def get_app_config():
        try:
            config = {}
            for key, value in app.config.items():
                config[key] = value
            del config['SECRET_KEY']    # 해당 키가 있으면 보이지 않고 오류 발생.. 무슨 마법이지;
            config = json.dumps(config, sort_keys=True, indent=4, default=lambda x: str(x))
            config = config.replace('\n', '<br>').replace('  ', '&nbsp;&nbsp;')
            return config
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return ''

    @staticmethod
    def get_platform():
        try:
            platform_list = []
            platform_list.append(['platform.machine()', platform.machine()])
            platform_list.append(['platform.node()', platform.node()])
            platform_list.append(['platform.platform()', platform.platform()])
            platform_list.append(['platform.processor()', platform.processor()])
            platform_list.append(['platform.python_build()', platform.python_build()])
            platform_list.append(['platform.python_compiler()', platform.python_compiler()])
            platform_list.append(['platform.python_branch()', platform.python_branch()])
            platform_list.append(['platform.python_implementation()', platform.python_implementation()])
            platform_list.append(['platform.python_revision()', platform.python_revision()])
            platform_list.append(['platform.python_version()', platform.python_version()])
            platform_list.append(['platform.python_version_tuple()', platform.python_version_tuple()])
            platform_list.append(['platform.release()', platform.release()])
            platform_list.append(['platform.system()', platform.system()])
            platform_list.append(['platform.version()', platform.version()])
            platform_list.append(['platform.uname()', platform.uname()])
            return platform_list
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return []

    @staticmethod
    def get_sys():
        try:
            sys_list = []
            sys_list.append(['sys.argv', sys.argv])
            sys_list.append(['sys.executable', sys.executable])
            sys_list.append(['sys.path', sys.path])
            sys_list.append(['sys.platform', sys.platform])
            return sys_list
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return []

    @staticmethod
    def get_package_list():
        try:
            output = subprocess.check_output([sys.executable, '-m', 'pip', 'list'], universal_newlines=True).rstrip()
            packages = []
            for i in output.split('\n')[2:]:
                packages.append(i.strip().split())
            return packages
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return []

    @staticmethod
    def py_package_install(name):
        try:
            print('pip install --upgrade %s', name)
            output = subprocess.check_output([sys.executable, '-m', 'pip', 'install', '--upgrade', name],
                                             universal_newlines=True).rstrip()
            print(output)
            return output
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return ''

    @staticmethod
    def py_package_uninstall(name):
        try:
            print('pip uninstall -y %s', name)
            output = subprocess.check_output([sys.executable, '-m', 'pip', 'uninstall', '-y', name],
                                             universal_newlines=True).rstrip()
            print(output)
            return output
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return ''

    @staticmethod
    def get_db_list():
        try:
            dbs = []
            for i in glob.glob(os.path.join(path_data, 'db', '*.db')):
                dbs.append(os.path.splitext(os.path.basename(i))[0])
            dbs.sort()
            return dbs
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return []

    @staticmethod
    def get_db_dict(name):
        try:
            db_dict = {}
            db_attr = {}
            connect = sqlite3.connect(os.path.join(path_data, 'db', '%s.db' % name))
            cursor = connect.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            for table in tables:
                cursor.execute("SELECT * FROM '%s'" % table)
                rows = cursor.fetchall()
                cols = [col[0] for col in cursor.description]
                db_attr[table] = cols

                tuples = []
                for row in rows:
                    tuple = OrderedDict()
                    for col in cols:
                        tuple[col] = row[cols.index(col)]
                    tuples.append(tuple)
                db_dict[table] = tuples

            connect.close()
            return db_dict, db_attr
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return {}

    @staticmethod
    def get_log_list():
        try:
            logs = []
            for i in glob.glob(os.path.join(path_data, 'log', '*.log')):
                logs.append(os.path.splitext(os.path.basename(i))[0])
            logs.sort()
            return logs
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return []

    @staticmethod
    def log_delete(log):
        try:
            for i in glob.glob(os.path.join(path_data, 'log', log + '.log*')):
                os.remove(i)
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())

    @staticmethod
    def get_ffmpeg_new():
        try:
            html = requests.get('https://johnvansickle.com/ffmpeg/', allow_redirects=True).text
            root = lxml.html.fromstring(html)
            git_master = root.xpath('//table/tr[1]/th[1]/text()')[0][21:]
            release = root.xpath('//table/tr[1]/th[2]/text()')[0][9:]
            return git_master, release
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return '', ''

    @staticmethod
    def ffmpeg_update(type, name):
        try:
            if platform.machine() == 'x86_64' and app.config['config']['running_type'] == 'docker': # 도커 환경에서만
                if type == 'git':
                    url = 'https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz'
                    dir = 'ffmpeg-git-' + name + '-amd64-static'
                elif type == 'release':
                    url = 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'
                    dir = 'ffmpeg-' + name + '-amd64-static'
                else:
                    return {'success': False, 'message': '잘못된 타입'}
                args = (url, dir)
                if app.config['config']['use_celery']:
                    Logic.ffmpeg_download.apply_async(args=args)
                else:
                    Thread(target=Logic.ffmpeg_download, args=args).start()
            else:
                return {'success': False, 'message': '지원하지 않는 시스템'}
            return {'success': True}
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return {'success': False, 'message': e}

    @staticmethod
    @celery.task
    def ffmpeg_download(url, dir):
        filename = os.path.join(path_data, 'download_tmp', 'ffmpeg-amd64-static.tar.xz')
        response = requests.get(url, allow_redirects=True)
        with open(filename, 'wb') as f:
            f.write(response.content)    # 다운로드
        # 아 zx 압축해제가 파이썬 3.3부터 지원하넹...
        print('tar xvfJ %s -C %s' % (filename, os.path.join(path_data, 'download_tmp')))
        output = subprocess.check_output(['tar', 'xvfJ', filename, '-C', os.path.join(path_data, 'download_tmp')],
                                         universal_newlines=True)
        print(output)
        # 덮어쓰기
        # print('mv %s %s' % (os.path.join(path_data, 'download_tmp', dir, 'ffmpeg'), '/usr/bin/ffmpeg'))
        # shutil.move(os.path.join(path_data, 'download_tmp', dir, 'ffmpeg'), '/usr/bin/ffmpeg')
        # print('mv %s %s' % (os.path.join(path_data, 'download_tmp', dir, 'ffprobe'), '/usr/bin/ffprobe'))
        # shutil.move(os.path.join(path_data, 'download_tmp', dir, 'ffprobe'), '/usr/bin/ffprobe')
        # print('mv %s %s' % (os.path.join(path_data, 'download_tmp', dir, 'qt-faststart'), '/usr/bin/qt-faststart'))
        # shutil.move(os.path.join(path_data, 'download_tmp', dir, 'qt-faststart'), '/usr/bin/qt-faststart')
        print('mv %s %s' % (os.path.join(path_data, 'download_tmp', dir, 'ffmpeg'), os.path.join(path_data, 'download', 'ffmpeg')))
        shutil.move(os.path.join(path_data, 'download_tmp', dir, 'ffmpeg'), os.path.join(path_data, 'download', 'ffmpeg'))
        # 다운로드 삭제
        print('rm %s' % filename)
        os.remove(filename)
        print('rm -r %s' % os.path.join(path_data, 'download_tmp', dir))
        shutil.rmtree(os.path.join(path_data, 'download_tmp', dir))
