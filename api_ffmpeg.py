# 최종 업데이트 20210501
import requests

from system.model import ModelSetting as SystemModelSetting

HOST_URL = 'http://localhost:%s' % SystemModelSetting.get('port')


class APIFFmpeg(object):
    @staticmethod
    def download(caller, key, url, filename, save_path=None):
        params = {
            'caller': caller,
            'id': key,
            'url': url,
            'filename': filename
        }
        if save_path:
            params['save_path'] = save_path
        params['token'] = SystemModelSetting.get('unique')  # sjva_token
        return requests.get('%s/ffmpeg/api/download' % HOST_URL, params=params).json()

    @staticmethod
    def stop(caller, key):
        params = {
            'caller': caller,
            'id': key
        }
        params['token'] = SystemModelSetting.get('unique')  # sjva_token
        return requests.post('%s/ffmpeg/api/stop' % HOST_URL, params=params).json()

    @staticmethod
    def status(caller, key):
        params = {
            'caller': caller,
            'id': key
        }
        params['token'] = SystemModelSetting.get('unique')  # sjva_token
        return requests.post('%s/ffmpeg/api/status' % HOST_URL, params=params).json()
