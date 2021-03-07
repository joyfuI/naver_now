# -*- coding: utf-8 -*-
# python
import os
import traceback
from datetime import datetime
from pytz import timezone
import threading

# third-party

# sjva 공용
from framework import db, scheduler, path_data
from framework.job import Job
from framework.util import Util

# 패키지
from .plugin import logger, package_name
from .model import ModelSetting, ModelScheduler
from .logic_normal import LogicNormal


class Logic(object):
    db_default = {
        'db_version': '1',
        'auto_start': 'False',
        'default_save_path': os.path.join(path_data, 'download', package_name),
    }

    @staticmethod
    def db_init():
        try:
            for key, value in Logic.db_default.items():
                if db.session.query(ModelSetting).filter_by(key=key).count() == 0:
                    db.session.add(ModelSetting(key, value))
            db.session.commit()
            # Logic.migration()
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def plugin_load():
        try:
            logger.debug('%s plugin_load', package_name)
            Logic.db_init()  # DB 초기화

            if ModelSetting.get_bool('auto_start'):
                for i in ModelScheduler.get_list():
                    Logic.scheduler_start(i.id)

            # 편의를 위해 json 파일 생성
            from .plugin import plugin_info
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

    @staticmethod
    def scheduler_start(job_id):
        try:
            scheduler_model = ModelScheduler.find(job_id)
            logger.debug('%s_%s scheduler_start', package_name, job_id)
            job = Job(package_name, '%s_%s' % (package_name, job_id), scheduler_model.interval,
                      Logic.scheduler_function, u"NAVER NOW 라이브 다운로드:%s" % scheduler_model.title, False, job_id)
            scheduler.add_job_instance(job)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def scheduler_stop(job_id):
        try:
            logger.debug('%s_%s scheduler_stop', package_name, job_id)
            scheduler.remove_job('%s_%s' % (package_name, job_id))
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def scheduler_function(job_id):
        try:
            LogicNormal.scheduler_function(job_id)
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def one_execute(job_id):
        try:
            if job_id is None:
                for i in ModelScheduler.get_list():
                    Logic.one_execute(i.id)
                ret = 'thread'
            else:
                if scheduler.is_include('%s_%s' % (package_name, job_id)):
                    if scheduler.is_running('%s_%s' % (package_name, job_id)):
                        ret = 'is_running'
                    else:
                        # scheduler.execute_job('%s_%s' % (package_name, job_id))
                        # 뜸들이지말고 바로 실행
                        logger.debug('execute_job:%s', '%s_%s' % (package_name, job_id))
                        job = scheduler.sched.get_job('%s_%s' % (package_name, job_id))
                        job.modify(next_run_time=datetime.now(timezone('Asia/Seoul')))
                        ret = 'scheduler'
                else:
                    # 뜸들이지말고 바로 실행
                    threading.Thread(target=Logic.scheduler_function, args=(job_id,)).start()
                    ret = 'thread'
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            ret = 'fail'
        return ret
