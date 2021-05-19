import os
import traceback
import json

from flask import Blueprint, request, render_template, redirect, jsonify
from flask_login import login_required

from framework import path_app_root, path_data

try:
    from logic import Logic
except:
    from .logic import Logic
#########################################################
# 플러그인 공용
#########################################################
blueprint = Blueprint(package_name, package_name, url_prefix='/%s' % package_name,
                      template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                      static_folder=os.path.join(os.path.dirname(__file__), 'static'))

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
        arg = {
            'package_name': package_name,
            'template_name': '%s_%s' % (package_name, sub)
        }

        if sub == 'info':
            arg['path_app_root'] = path_app_root
            arg['path_data'] = path_data
            arg['config'] = Logic.get_app_config()
            arg['platform'] = Logic.get_platform()
            arg['sys'] = Logic.get_sys()
            return render_template('%s_%s.html' % (package_name, sub), arg=arg)

        elif sub == 'py':
            arg['packages'] = Logic.get_package_list()
            return render_template('%s_%s.html' % (package_name, sub), arg=arg)

        elif sub == 'db':
            return redirect('/%s/%s/sjva' % (package_name, sub))

        elif sub == 'log':
            return redirect('/%s/%s/framework' % (package_name, sub))

        elif sub == 'lib':
            arg['ffmpeg_git'], arg['ffmpeg_release'] = Logic.get_ffmpeg_new()
            return render_template('%s_%s.html' % (package_name, sub), arg=arg)

        elif sub == 'macro':
            return render_template('%s_%s.html' % (package_name, sub), arg=arg)
    except Exception as e:
        print('Exception:%s', e)
        print(traceback.format_exc())
    return render_template('sample.html', title='%s - %s' % (package_name, sub))


@blueprint.route('/<sub>/<sub2>')
@login_required
def second_menu(sub, sub2):
    try:
        arg = {
            'package_name': package_name,
            'template_name': '%s_%s' % (package_name, sub)
        }

        if sub == 'db':
            arg['dbs'] = Logic.get_db_list()
            if sub2 in arg['dbs']:
                arg['db'] = sub2
                arg['tables'], arg['cols'] = Logic.get_db_dict(sub2)
                arg['first_table'] = list(arg['tables'].keys())[0]
                return render_template('%s_%s.html' % (package_name, sub), arg=arg)

        elif sub == 'log':
            arg['logs'] = Logic.get_log_list()
            if sub2 in arg['logs']:
                arg['log'] = sub2
                return render_template('%s_%s.html' % (package_name, sub), arg=arg)
    except Exception as e:
        print('Exception:%s', e)
        print(traceback.format_exc())
    return render_template('sample.html', title='%s - %s - %s' % (package_name, sub, sub2))


#########################################################
# For UI
#########################################################
@blueprint.route('/ajax/<sub>', methods=['POST'])
@login_required
def ajax(sub):
    print('AJAX %s %s', package_name, sub)
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
        elif sub == 'edit_db':
            data = request.form
            if 'origin_data' in data and 'req_data' in data:
                req_data = json.loads(data['req_data'])
                db = data['db']
                table = data['table']
                origin_data = json.loads(data['origin_data'])
                result = Logic.edit_db(db, table, origin_data, req_data)
                return jsonify(result)
            return jsonify('fail')
        elif sub == 'delete_db':
            data = request.form
            if 'req_data' in data:
                req_data = json.loads(data['req_data'])
                db = data['db']
                table = data['table']
                result = Logic.delete_db(db, table, req_data)
                return jsonify(result)
            return jsonify('fail')

    except Exception as e:
        print('Exception:%s', e)
        print(traceback.format_exc())
