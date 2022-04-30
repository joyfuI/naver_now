# 최종 업데이트 20220430
import requests

from system.model import ModelSetting as SystemModelSetting

HOST_URL = f"http://localhost:{SystemModelSetting.get('port')}"


class APIFFmpeg(object):
    @staticmethod
    def download(caller, key, url, filename, save_path=None):
        params = {"caller": caller, "id": key, "url": url, "filename": filename}
        if save_path:
            params["save_path"] = save_path
        params["token"] = SystemModelSetting.get("unique")  # sjva_token
        return requests.get(f"{HOST_URL}/ffmpeg/api/download", params=params).json()

    @staticmethod
    def stop(caller, key):
        params = {"caller": caller, "id": key}
        params["token"] = SystemModelSetting.get("unique")  # sjva_token
        return requests.post(f"{HOST_URL}/ffmpeg/api/stop", params=params).json()

    @staticmethod
    def status(caller, key):
        params = {"caller": caller, "id": key}
        params["token"] = SystemModelSetting.get("unique")  # sjva_token
        return requests.post(f"{HOST_URL}/ffmpeg/api/status", params=params).json()
