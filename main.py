import traceback
import os
import sys
import platform
import glob
import shutil
import tarfile
import subprocess
import json
import sqlite3
import urllib.request
from threading import Thread
from collections import OrderedDict

import lxml.html
from flask import render_template, redirect, jsonify
from flask_login import login_required

from framework import path_app_root, path_data, app, celery
from framework.common.plugin import LogicModuleBase

from .plugin import P

logger = P.logger
package_name = P.package_name
ModelSetting = P.ModelSetting


class LogicMain(LogicModuleBase):
    def __init__(self, P):
        super(LogicMain, self).__init__(P, 'info')  # 해당모듈의 기본 sub
        self.name = package_name  # 모듈명

    def process_menu(self, sub, req):
        try:
            arg = {
                'package_name': package_name,
                'sub': sub,
                'template_name': f'{package_name}_{sub}'
            }

            if sub == 'info':
                arg['path_app_root'] = path_app_root
                arg['path_data'] = path_data
                arg['config'] = LogicMain.get_app_config()
                arg['platform'] = LogicMain.get_platform()
                arg['sys'] = LogicMain.get_sys()

            elif sub == 'py':
                arg['packages'] = LogicMain.get_package_list()

            elif sub == 'db':
                return redirect(f'/{package_name}/{sub}/sjva')

            elif sub == 'logfile':
                return redirect(f'/{package_name}/{sub}/framework')

            elif sub == 'lib':
                arg['ffmpeg_git'], arg['ffmpeg_release'] = LogicMain.get_ffmpeg_new()

            elif sub == 'macro':
                pass

            return render_template(f'{package_name}_{sub}.html', arg=arg)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return render_template('sample.html', title=f'{package_name} - {sub}')

    @staticmethod
    @P.blueprint.route('/<sub>/<sub2>', methods=['GET', 'POST'])
    @login_required
    def second_menu(sub, sub2):
        try:
            arg = {
                'package_name': package_name,
                'sub': sub,
                'sub2': sub2,
                'template_name': f'{package_name}_{sub}'
            }

            if sub == 'db':
                arg['dbs'] = LogicMain.get_db_list()
                if sub2 in arg['dbs']:
                    arg['db'] = sub2
                    arg['tables'], arg['cols'] = LogicMain.get_db_dict(sub2)
                    arg['first_table'] = list(arg['tables'].keys())[0]

            elif sub == 'logfile':
                arg['logs'] = LogicMain.get_log_list()
                if sub2 in arg['logs']:
                    arg['log'] = sub2

            return render_template(f'{package_name}_{sub}.html', arg=arg)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return render_template('sample.html', title=f'{package_name} - {sub}')

    def process_ajax(self, sub, req):
        try:
            logger.debug('AJAX: %s, %s', sub, req.values)
            ret = {'ret': 'success'}

            if sub == 'install':
                name = req.form['name']
                ret['data'] = {
                    'title': name,
                    'content': LogicMain.py_package_install(name).split('\n')
                }

            elif sub == 'uninstall':
                name = req.form['name']
                ret['data'] = {
                    'title': name,
                    'content': LogicMain.py_package_uninstall(name).split('\n')
                }

            elif sub == 'delete':
                log = req.form.get('log', None)
                if log is not None:
                    LogicMain.log_delete(log)

            elif sub == 'ffmpeg':
                ffmpeg_type = req.form['type']
                name = req.form['name']
                ret['data'] = LogicMain.ffmpeg_update(ffmpeg_type, name)

            elif sub == 'edit_db':
                data = req.form
                req_data = json.loads(data['req_data'])
                db = data['db']
                table = data['table']
                origin_data = json.loads(data['origin_data'])
                ret['data'] = LogicMain.edit_db(db, table, origin_data, req_data)

            elif sub == 'delete_db':
                data = req.form
                req_data = json.loads(data['req_data'])
                db = data['db']
                table = data['table']
                ret['data'] = LogicMain.delete_db(db, table, req_data)

            return jsonify(ret)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return jsonify({'ret': 'danger', 'msg': str(e)})

    @staticmethod
    def get_app_config():
        config = {}
        for key, value in app.config.items():
            config[key] = value
        del config['SECRET_KEY']  # 해당 키가 있으면 보이지 않고 오류 발생.. 무슨 마법이지;
        config = json.dumps(config, sort_keys=True, indent=4, default=lambda x: str(x))
        config = config.replace('\n', '<br>').replace('  ', '&nbsp;&nbsp;')
        return config

    @staticmethod
    def get_platform():
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

    @staticmethod
    def get_sys():
        sys_list = [['sys.argv', sys.argv], ['sys.executable', sys.executable], ['sys.path', sys.path],
                    ['sys.platform', sys.platform]]
        return sys_list

    @staticmethod
    def get_package_list():
        output = subprocess.check_output([sys.executable, '-m', 'pip', 'list'], universal_newlines=True).rstrip()
        packages = []
        for i in output.split('\n')[2:]:
            packages.append(i.strip().split())
        return packages

    @staticmethod
    def py_package_install(name):
        logger.debug('pip install --upgrade %s', name)
        output = subprocess.check_output([sys.executable, '-m', 'pip', 'install', '--upgrade', name],
                                         universal_newlines=True).rstrip()
        logger.debug(output)
        return output

    @staticmethod
    def py_package_uninstall(name):
        logger.debug('pip uninstall -y %s', name)
        output = subprocess.check_output([sys.executable, '-m', 'pip', 'uninstall', '-y', name],
                                         universal_newlines=True).rstrip()
        logger.debug(output)
        return output

    @staticmethod
    def get_db_list():
        dbs = []
        for i in glob.glob(os.path.join(path_data, 'db', '*.db')):
            dbs.append(os.path.splitext(os.path.basename(i))[0])
        dbs.sort()
        return dbs

    @staticmethod
    def get_db_dict(name):
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
                db_tuple = OrderedDict()
                for col in cols:
                    db_tuple[col] = row[cols.index(col)]
                tuples.append(db_tuple)
            db_dict[table] = tuples

        connect.close()
        return db_dict, db_attr

    @staticmethod
    def get_log_list():
        logs = []
        for i in glob.glob(os.path.join(path_data, 'log', '*.log')):
            logs.append(os.path.splitext(os.path.basename(i))[0])
        logs.sort()
        return logs

    @staticmethod
    def log_delete(log):
        for i in glob.glob(os.path.join(path_data, 'log', log + '.log*')):
            os.remove(i)

    @staticmethod
    def get_ffmpeg_new():
        with urllib.request.urlopen('https://johnvansickle.com/ffmpeg/') as response:
            html = lxml.html.fromstring(response.read())
        git_master = html.xpath('//table/tr[1]/th[1]/text()')[0][21:]
        release = html.xpath('//table/tr[1]/th[2]/text()')[0][9:]
        return git_master, release

    @staticmethod
    def ffmpeg_update(ffmpeg_type, name):
        if platform.machine() == 'x86_64' and platform.system() == 'Linux':  # 리눅스 환경에서만
            if ffmpeg_type == 'git':
                url = 'https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz'
                path = 'ffmpeg-git-' + name + '-amd64-static'
            elif ffmpeg_type == 'release':
                url = 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'
                path = 'ffmpeg-' + name + '-amd64-static'
            else:
                return {'success': False, 'message': '잘못된 타입'}
            args = (url, path)
            if app.config['config']['use_celery']:
                LogicMain.ffmpeg_download.apply_async(args=args)
            else:
                Thread(target=LogicMain.ffmpeg_download, args=args).start()
        else:
            return {'success': False, 'message': '지원하지 않는 시스템'}
        return {'success': True}

    @staticmethod
    @celery.task
    def ffmpeg_download(url, path):
        filename = os.path.join(path_data, 'download_tmp', 'ffmpeg-amd64-static.tar.xz')
        logger.debug('download %s' % url)
        urllib.request.urlretrieve(url, filename)
        logger.debug('tar xfJ %s -C %s' % (filename, os.path.join(path_data, 'download_tmp')))
        with tarfile.open(filename) as xz:
            xz.extractall(os.path.join(path_data, 'download_tmp'))  # xz 압축해제
        # logger.debug(output)
        # 덮어쓰기
        # logger.debug('mv %s %s' % (os.path.join(path_data, 'download_tmp', path, 'ffmpeg'), '/usr/bin/ffmpeg'))
        # shutil.move(os.path.join(path_data, 'download_tmp', path, 'ffmpeg'), '/usr/bin/ffmpeg')
        # logger.debug('mv %s %s' % (os.path.join(path_data, 'download_tmp', path, 'ffprobe'), '/usr/bin/ffprobe'))
        # shutil.move(os.path.join(path_data, 'download_tmp', path, 'ffprobe'), '/usr/bin/ffprobe')
        # logger.debug('mv %s %s' % (os.path.join(path_data, 'download_tmp', path, 'qt-faststart'), '/usr/bin/qt-faststart'))
        # shutil.move(os.path.join(path_data, 'download_tmp', path, 'qt-faststart'), '/usr/bin/qt-faststart')
        logger.debug('mv %s %s' % (os.path.join(path_data, 'download_tmp', path, 'ffmpeg'),
                                   os.path.join(path_data, 'download', 'ffmpeg')))
        shutil.move(os.path.join(path_data, 'download_tmp', path, 'ffmpeg'),
                    os.path.join(path_data, 'download', 'ffmpeg'))
        # 다운로드 삭제
        logger.debug('rm %s' % filename)
        os.remove(filename)
        logger.debug('rm -r %s' % os.path.join(path_data, 'download_tmp', path))
        shutil.rmtree(os.path.join(path_data, 'download_tmp', path))

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
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
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
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return {'success': False, 'message': e}
