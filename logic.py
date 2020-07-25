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
import urllib2
import json
from threading import Thread

# third-party
import lxml.html
from sqlitedict import SqliteDict

# sjva 공용
from framework import path_data, app, celery
from framework.util import Util

# 패키지
from .plugin import logger, package_name
#########################################################

class Logic(object):
    @staticmethod
    def plugin_load():
        try:
            logger.debug('%s plugin_load', package_name)

            if platform.system() == 'Windows':  # 윈도우일 때
                pass
            else:
                pass

            # 편의를 위해 json 파일 생성
            from plugin import plugin_info
            Util.save_from_dict_to_json(plugin_info, os.path.join(os.path.dirname(__file__), 'info.json'))
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def plugin_unload():
        try:
            logger.debug('%s plugin_unload', package_name)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

#########################################################

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
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
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
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return []

    @staticmethod
    def get_package_list():
        try:
            logger.debug('pip list')
            output = subprocess.check_output([sys.executable, '-m', 'pip', 'list'], universal_newlines=True).rstrip()
            packages = []
            for i in output.split('\n')[2:]:
                packages.append(i.strip().split())
            return packages
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return []

    @staticmethod
    def py_package_install(name):
        try:
            logger.debug('pip install --upgrade %s', name)
            output = subprocess.check_output([sys.executable, '-m', 'pip', 'install', '--upgrade', name],
                                             universal_newlines=True).rstrip()
            logger.debug(output)
            return output
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return ''

    @staticmethod
    def py_package_uninstall(name):
        try:
            logger.debug('pip uninstall -y %s', name)
            output = subprocess.check_output([sys.executable, '-m', 'pip', 'uninstall', '-y', name],
                                             universal_newlines=True).rstrip()
            logger.debug(output)
            return output
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
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
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return []

    @staticmethod
    def get_app_config():
        try:
            config = {}
            for key, value in app.config.items():
                config[key] = value
            del config['SECRET_KEY']    # 해당 키가 있으면 보이지 않고 오류 발생.. 무슨 마법이지;
            config = json.dumps(config, sort_keys=True, indent=4, default=lambda x: str(x))
            return config
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return ''

    @staticmethod
    def get_db_dict(file):
        try:
            mydict = {}
            with SqliteDict(file, 'youtube-dl_setting') as sqldict:
                for key, value in sqldict.iteritems():
                    logger.debug('key: %s, value: %s' % (key, value))
                    mydict[key] = value
            logger.debug(mydict)
            return mydict
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
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
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return []

    @staticmethod
    def log_delete(log):
        try:
            for i in glob.glob(os.path.join(path_data, 'log', log + '.log*')):
                logger.debug('Delete: %s', i)
                os.remove(i)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_ffmpeg_new():
        try:
            html = urllib2.urlopen('https://johnvansickle.com/ffmpeg/').read()
            root = lxml.html.fromstring(html)
            git_master = root.xpath('//table/tr[1]/th[1]/text()')[0][21:]
            release = root.xpath('//table/tr[1]/th[2]/text()')[0][9:]
            return git_master, release
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
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
                    logger.error('잘못된 타입: ', type)
                    return {'success': False, 'message': '잘못된 타입'}
                args = (url, dir)
                if app.config['config']['use_celery']:
                    Logic.ffmpeg_download.apply_async(args=args)
                else:
                    Thread(target=Logic.ffmpeg_download, args=args).start()
            else:
                logger.error('지원하지 않는 시스템')
                return {'success': False, 'message': '지원하지 않는 시스템'}
            return {'success': True}
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return {'success': False, 'message': e}

    @staticmethod
    @celery.task
    def ffmpeg_download(url, dir):
        filename = os.path.join(path_data, 'download_tmp', 'ffmpeg-amd64-static.tar.xz')
        logger.debug(url)
        response = urllib2.urlopen(url)
        with open(filename, 'wb') as f:
            f.write(response.read())    # 다운로드
        # 아 zx 압축해제가 파이썬 3.3부터 지원하넹...
        output = subprocess.check_output(['tar', 'xvfJ', filename, '-C', os.path.join(path_data, 'download_tmp')],
                                         universal_newlines=True)
        logger.debug(output)
        # 덮어쓰기
        logger.debug('mv %s %s' % (os.path.join(path_data, 'download_tmp', dir, 'ffmpeg'), '/usr/bin/ffmpeg'))
        shutil.move(os.path.join(path_data, 'download_tmp', dir, 'ffmpeg'), '/usr/bin/ffmpeg')
        logger.debug('mv %s %s' % (os.path.join(path_data, 'download_tmp', dir, 'ffprobe'), '/usr/bin/ffprobe'))
        shutil.move(os.path.join(path_data, 'download_tmp', dir, 'ffprobe'), '/usr/bin/ffprobe')
        logger.debug('mv %s %s' % (os.path.join(path_data, 'download_tmp', dir, 'qt-faststart'), '/usr/bin/qt-faststart'))
        shutil.move(os.path.join(path_data, 'download_tmp', dir, 'qt-faststart'), '/usr/bin/qt-faststart')
        # 다운로드 삭제
        logger.debug('rm %s' % filename)
        os.remove(filename)
        logger.debug('rm -r %s' % os.path.join(path_data, 'download_tmp', dir))
        shutil.rmtree(os.path.join(path_data, 'download_tmp', dir))
