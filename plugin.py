import os
import traceback

from flask import Blueprint

from framework.util import Util
from framework.logger import get_logger
from framework.common.plugin import Logic, default_route_single_module


class P(object):
    package_name = __name__.split('.')[0]
    logger = get_logger(package_name)
    logger.removeHandler(logger.handlers[0])  # 로그를 파일로 부분 제거
    blueprint = Blueprint(package_name, package_name, url_prefix=f'/{package_name}',
                          template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                          static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    # 메뉴 정의
    menu = {
        'main': [package_name, '플러그인 개발'],
        'sub': [
            ['info', '정보'], ['py', '파이썬'], ['db', '데이터베이스'], ['logfile', '로그'], ['lib', '라이브러리'], ['macro', '템플릿 매크로']
        ],
        'category': 'tool'
    }

    plugin_info = {
        'version': 'canary',
        'name': package_name,
        'category_name': 'tool',
        'icon': '',
        'developer': 'joyfuI',
        'description': '플러그인 개발 편의을 위한 잡다한 기능',
        'home': f'https://github.com/joyfuI/{package_name}',
        'more': '',
    }

    ModelSetting = None
    logic = None
    module_list = None
    home_module = 'info'  # 기본모듈


def initialize():
    try:
        Util.save_from_dict_to_json(P.plugin_info, os.path.join(os.path.dirname(__file__), 'info.json'))

        # 로드할 모듈 정의
        from .main import LogicMain
        P.module_list = [LogicMain(P)]

        P.logic = Logic(P)
        default_route_single_module(P)
    except Exception as e:
        P.logger.error('Exception:%s', e)
        P.logger.error(traceback.format_exc())


logger = P.logger
initialize()
