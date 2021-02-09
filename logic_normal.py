# -*- coding: utf-8 -*-
#########################################################
# python
import os
import re
import time
from datetime import date

# third-party
import requests

# sjva 공용
from framework import scheduler

# 패키지
from .plugin import logger, package_name
from .model import ModelSetting, ModelScheduler
from .api_ffmpeg import APIFFmpeg
#########################################################

class LogicNormal(object):
    download_list = set()

    @staticmethod
    def scheduler_function(job_id):
        scheduler_model = ModelScheduler.find(job_id)
        content_id = LogicNormal.get_content_id(scheduler_model.url)
        if content_id is None:
            logger.debug('scheduler url error %s', scheduler_model.url)
            return
        content_info = LogicNormal.get_content_info(content_id)
        if content_info is None:
            logger.debug('scheduler url error %s', scheduler_model.url)
            return
        for i in range(60):  # 10초 간격으로 최대 60번. 즉, 10분
            video_url = LogicNormal.get_video_url(content_id)
            if video_url is None:
                time.sleep(10)  # 10초 대기
                continue
            logger.debug('scheduler download %s', scheduler_model.url)
            filename = date.today().strftime('%y%m%d') + '_' + scheduler_model.filename
            download = APIFFmpeg.download(package_name, '%s_%s' % (package_name, job_id), video_url, filename,
                                          save_path=scheduler_model.save_path)
            if download['ret'] != 'success':
                logger.debug('scheduler download fail %s', download['ret'])
                logger.debug(download.get('log'))
                time.sleep(10)  # 10초 대기
                continue
            scheduler_model.update()
            break

    @staticmethod
    def get_scheduler():
        ret = []
        for scheduler_model in ModelScheduler.get_list(True):
            scheduler_model['last_time'] = scheduler_model['last_time'].strftime('%m-%d %H:%M:%S'),
            scheduler_model['path'] = os.path.join(scheduler_model['save_path'],
                                                   date.today().strftime('%y%m%d') + '_' + scheduler_model['filename'])
            scheduler_model['is_include'] = scheduler.is_include('%s_%s' % (package_name, scheduler_model['id']))
            scheduler_model['is_running'] = scheduler.is_running('%s_%s' % (package_name, scheduler_model['id']))
            ret.append(scheduler_model)
        return ret

    @staticmethod
    def add_scheduler(form):
        from .logic import Logic

        if form['db_id']:
            data = {
                'save_path': form['save_path'],
                'filename': form['filename'],
                'interval': form['interval']
            }
            ModelScheduler.find(form['db_id']).update(data)
        else:
            content_id = LogicNormal.get_content_id(form['url'])
            if content_id is None:
                logger.debug('url error %s', form['url'])
                return None
            content_info = LogicNormal.get_content_info(content_id)
            if content_info is None:
                logger.debug('url error %s', form['url'])
                return None
            data = {
                'url': 'https://now.naver.com/%s' % content_id,
                'title': content_info['description']['clova']['synonym'][0],
                'host': content_info['description']['clova']['host'][0],
                'save_path': form['save_path'],
                'filename': form['filename'],
                'interval': form['interval']
            }
            scheduler_model = ModelScheduler.create(data)
            if ModelSetting.get_bool('auto_start'):
                Logic.scheduler_start(scheduler_model.id)
        return LogicNormal.get_scheduler()

    @staticmethod
    def del_scheduler(db_id):
        logger.debug('del_scheduler %s', db_id)
        ModelScheduler.find(db_id).delete()
        return LogicNormal.get_scheduler()

    @staticmethod
    def get_content_id(url):
        pattern = re.compile(r'https?://now\.naver\.com/(\d+)')
        match = pattern.findall(url)
        if not match:
            return None
        return match[0]

    @staticmethod
    def get_content_info(content_id):
        url = 'https://now.naver.com/api/nnow/v1/stream/%s/content/' % content_id
        json = requests.get(url).json()
        if not json['contentList']:
            return None
        return json['contentList'][0]

    @staticmethod
    def get_video_url(content_id):
        url = 'https://now.naver.com/api/nnow/v1/stream/%s/livestatus/' % content_id
        json = requests.get(url).json()
        if json['status']['status'] != 'ONAIR':
            return None
        video_url = json['status']['videoStreamUrl']
        m3u8 = video_url.replace('playlist.m3u8', 'chunklist_1080p.m3u8')
        return m3u8
