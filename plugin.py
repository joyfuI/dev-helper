# -*- coding: utf-8 -*-
#########################################################
# python
import os
import traceback

# third-party
from flask import Blueprint, request, render_template, redirect, jsonify
from flask_login import login_required

# sjva 공용
from framework import path_app_root, path_data
from framework.logger import get_logger

# 패키지
package_name = __name__.split('.')[0]
logger = get_logger(package_name)
from .logic import Logic

#########################################################
# 플러그인 공용
#########################################################
blueprint = Blueprint(package_name, package_name, url_prefix='/%s' % package_name, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

menu = {
    'main': [package_name, '플러그인 개발'],
    'sub': [
        ['info', '정보'], ['py', '파이썬'], ['db', '데이터베이스'], ['log', '로그'], ['lib', '라이브러리'], ['macro', '템플릿 매크로']
    ],
    'category': 'tool'
}

plugin_info = {
    'version': 'canary',
    'name': 'dev-helper',
    'category_name': 'tool',
    'developer': 'joyfuI',
    'description': '플러그인 개발 편의을 위한 잡다한 기능',
    'home': 'https://github.com/joyfuI/dev-helper',
    'more': ''
}

def plugin_load():
    Logic.plugin_load()

def plugin_unload():
    Logic.plugin_unload()

#########################################################
# WEB Menu
#########################################################
@blueprint.route('/')
def home():
    return redirect('/%s/info' % package_name)

@blueprint.route('/<sub>')
@login_required
def first_menu(sub):
    try:
        arg = {'package_name': package_name}

        if sub == 'info':
            arg['path_app_root'] = path_app_root
            arg['path_data'] = path_data
            arg['platform'] = Logic.get_platform()
            arg['sys'] = Logic.get_sys()
            return render_template('%s_%s.html' % (package_name, sub), arg=arg)

        elif sub == 'py':
            arg['packages'] = Logic.get_package_list()
            return render_template('%s_%s.html' % (package_name, sub), arg=arg)

        elif sub == 'db':
            return redirect('/%s/%s/app.config' % (package_name, sub))

        elif sub == 'log':
            return redirect('/%s/%s/framework' % (package_name, sub))

        elif sub == 'lib':
            arg['ffmpeg_git'], arg['ffmpeg_release'] = Logic.get_ffmpeg_new()
            return render_template('%s_%s.html' % (package_name, sub), arg=arg)

        elif sub == 'macro':
            return render_template('%s_%s.html' % (package_name, sub), arg=arg)
    except Exception as e:
        logger.error('Exception:%s', e)
        logger.error(traceback.format_exc())
    return render_template('sample.html', title='%s - %s' % (package_name, sub))

@blueprint.route('/<sub>/<sub2>')
@login_required
def second_menu(sub, sub2):
    try:
        arg = {'package_name': package_name}

        if sub == 'db':
            arg['dbs'] = Logic.get_db_list()
            if sub2 == 'app.config':
                arg['config'] = Logic.get_app_config().split('\n')
                return render_template('%s_%s_app.html' % (package_name, sub), arg=arg)
            elif sub2 in arg['dbs']:
                arg['plugin'] = sub2
                return render_template('%s_%s.html' % (package_name, sub), arg=arg)

        elif sub == 'log':
            arg['logs'] = Logic.get_log_list()
            if sub2 in arg['logs']:
                arg['plugin'] = sub2
                return render_template('%s_%s.html' % (package_name, sub), arg=arg)
    except Exception as e:
        logger.error('Exception:%s', e)
        logger.error(traceback.format_exc())
    return render_template('sample.html', title='%s - %s - %s' % (package_name, sub, sub2))

#########################################################
# For UI
#########################################################
@blueprint.route('/ajax/<sub>', methods=['POST'])
@login_required
def ajax(sub):
    logger.debug('AJAX %s %s', package_name, sub)
    try:
        if sub == 'install':
            name = request.form['name']
            ret = {
                'title': name,
                'content': Logic.py_package_install(name).split('\n')
            }
            return jsonify(ret)

        elif sub == 'uninstall':
            name = request.form['name']
            ret = {
                'title': name,
                'content': Logic.py_package_uninstall(name).split('\n')
            }
            return jsonify(ret)

        elif sub == 'delete':
            log = request.form.get('log', None)
            if log is not None:
                Logic.log_delete(log)
            return jsonify([])

        elif sub == 'ffmpeg':
            type = request.form['type']
            name = request.form['name']
            ret = Logic.ffmpeg_update(type, name)
            return jsonify(ret)
    except Exception as e:
        logger.error('Exception:%s', e)
        logger.error(traceback.format_exc())
