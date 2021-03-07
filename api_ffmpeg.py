# -*- coding: utf-8 -*-
# 최종 업데이트 20210212
# third-party
import requests

# sjva 공용, 패키지
from system.model import ModelSetting as SystemModelSetting

HOST_URL = 'http://localhost:%s' % SystemModelSetting.get('port')


class APIFFmpeg(object):
    @staticmethod
    def download(caller, id, url, filename, save_path=None):
        params = {
            'caller': caller,
            'id': id,
            'url': url,
            'filename': filename
        }
        if save_path:
            params['save_path'] = save_path
        params['token'] = SystemModelSetting.get('unique')  # sjva_token
        return requests.get('%s/ffmpeg/api/download' % HOST_URL, params=params).json()

    @staticmethod
    def stop(caller, id):
        params = {
            'caller': caller,
            'id': id
        }
        params['token'] = SystemModelSetting.get('unique')  # sjva_token
        return requests.post('%s/ffmpeg/api/stop' % HOST_URL, params=params).json()

    @staticmethod
    def status(caller, id):
        params = {
            'caller': caller,
            'id': id
        }
        params['token'] = SystemModelSetting.get('unique')  # sjva_token
        return requests.post('%s/ffmpeg/api/status' % HOST_URL, params=params).json()
