import os
import sys
import platform
import glob
import shutil
import traceback
import tarfile
import subprocess
import json
import sqlite3
import urllib.request
from threading import Thread
from collections import OrderedDict

import lxml.html

from framework import path_data, app, celery
from framework.util import Util


class Logic(object):
    @staticmethod
    def plugin_load():
        # 편의를 위해 json 파일 생성
        from .plugin import plugin_info
        Util.save_from_dict_to_json(plugin_info, os.path.join(os.path.dirname(__file__), 'info.json'))

    @staticmethod
    def plugin_unload():
        pass

    @staticmethod
    def get_app_config():
        try:
            config = {}
            for key, value in app.config.items():
                config[key] = value
            del config['SECRET_KEY']  # 해당 키가 있으면 보이지 않고 오류 발생.. 무슨 마법이지;
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
            platform_list = [['platform.machine()', platform.machine()], ['platform.node()', platform.node()],
                             ['platform.platform()', platform.platform()],
                             ['platform.processor()', platform.processor()],
                             ['platform.python_build()', platform.python_build()],
                             ['platform.python_compiler()', platform.python_compiler()],
                             ['platform.python_branch()', platform.python_branch()],
                             ['platform.python_implementation()', platform.python_implementation()],
                             ['platform.python_revision()', platform.python_revision()],
                             ['platform.python_version()', platform.python_version()],
                             ['platform.python_version_tuple()', platform.python_version_tuple()],
                             ['platform.release()', platform.release()], ['platform.system()', platform.system()],
                             ['platform.version()', platform.version()], ['platform.uname()', platform.uname()]]
            return platform_list
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return []

    @staticmethod
    def get_sys():
        try:
            sys_list = [['sys.argv', sys.argv], ['sys.executable', sys.executable], ['sys.path', sys.path],
                        ['sys.platform', sys.platform]]
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
                # 페이지네이션으로 처리하고 싶지만 귀찮아서 일단 500개로 제한
                cursor.execute("SELECT * FROM '%s' LIMIT 500" % table)
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
            with urllib.request.urlopen('https://johnvansickle.com/ffmpeg/') as response:
                html = lxml.html.fromstring(response.read())
            git_master = html.xpath('//table/tr[1]/th[1]/text()')[0][21:]
            release = html.xpath('//table/tr[1]/th[2]/text()')[0][9:]
            return git_master, release
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return '', ''

    @staticmethod
    def ffmpeg_update(type, name):
        try:
            if platform.machine() == 'x86_64' and platform.system() == 'Linux':  # 리눅스 환경에서만
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
        print('download %s' % url)
        urllib.request.urlretrieve(url, filename)
        print('tar xfJ %s -C %s' % (filename, os.path.join(path_data, 'download_tmp')))
        with tarfile.open(filename) as xz:
            xz.extractall(os.path.join(path_data, 'download_tmp'))  # xz 압축해제
        # print(output)
        # 덮어쓰기
        # print('mv %s %s' % (os.path.join(path_data, 'download_tmp', dir, 'ffmpeg'), '/usr/bin/ffmpeg'))
        # shutil.move(os.path.join(path_data, 'download_tmp', dir, 'ffmpeg'), '/usr/bin/ffmpeg')
        # print('mv %s %s' % (os.path.join(path_data, 'download_tmp', dir, 'ffprobe'), '/usr/bin/ffprobe'))
        # shutil.move(os.path.join(path_data, 'download_tmp', dir, 'ffprobe'), '/usr/bin/ffprobe')
        # print('mv %s %s' % (os.path.join(path_data, 'download_tmp', dir, 'qt-faststart'), '/usr/bin/qt-faststart'))
        # shutil.move(os.path.join(path_data, 'download_tmp', dir, 'qt-faststart'), '/usr/bin/qt-faststart')
        print('mv %s %s' % (os.path.join(path_data, 'download_tmp', dir, 'ffmpeg'),
                            os.path.join(path_data, 'download', 'ffmpeg')))
        shutil.move(os.path.join(path_data, 'download_tmp', dir, 'ffmpeg'),
                    os.path.join(path_data, 'download', 'ffmpeg'))
        # 다운로드 삭제
        print('rm %s' % filename)
        os.remove(filename)
        print('rm -r %s' % os.path.join(path_data, 'download_tmp', dir))
        shutil.rmtree(os.path.join(path_data, 'download_tmp', dir))

    @staticmethod
    def edit_db(db_name, table_name, origin_data, update_data):
        try:
            # DB row를 수동으로 편집하는 기능
            connect = sqlite3.connect(os.path.join(path_data, 'db', '%s.db' % db_name))
            cursor = connect.cursor()
            set_pharse = []
            for key, val in update_data.items():
                if val is not None:
                    set_pharse.append(key + " = '" + str(val).replace("'", "\\\'") + "' ")
                else:
                    set_pharse.append(key + ' = null ')

            where_pharse = []
            for key, val in origin_data.items():
                if val is not None:
                    where_pharse.append(key + " = '" + str(val).replace("'", "\\\'") + "' ")
                else:
                    where_pharse.append(key + ' IS null ')
            sql = '''
            UPDATE {} SET {} WHERE {}
            '''.format(table_name, ' , '.join(set_pharse), ' AND '.join(where_pharse))
            cursor.execute(sql)
            connect.commit()
            connect.close()
            return {'success': True}
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return {'success': False, 'message': e}

    @staticmethod
    def delete_db(db_name, table_name, delete_data):
        try:
            # DB row를 수동으로 삭제하는 기능
            connect = sqlite3.connect(os.path.join(path_data, 'db', '%s.db' % db_name))
            cursor = connect.cursor()
            where_pharse = []
            for key, val in delete_data.items():
                if val is not None:
                    where_pharse.append(key + " = '" + str(val).replace("'", "\\\'") + "' ")
                else:
                    where_pharse.append(key + ' IS null ')
            sql = '''
            DELETE FROM {} WHERE {}
            '''.format(table_name, ' AND '.join(where_pharse))
            cursor.execute(sql)
            connect.commit()
            connect.close()
            return {'success': True}
        except Exception as e:
            print('Exception:%s', e)
            print(traceback.format_exc())
            return {'success': False, 'message': e}
