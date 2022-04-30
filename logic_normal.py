import os
import re
import time
from datetime import date

import requests

from framework import scheduler
from framework.logger import get_logger

from .model import ModelSetting, ModelScheduler
from .api_ffmpeg import APIFFmpeg
from .crypto_js import AES

package_name = __name__.split(".", maxsplit=1)[0]
logger = get_logger(package_name)


class LogicNormal(object):
    download_list = set()

    @staticmethod
    def scheduler_function(job_id):
        scheduler_model = ModelScheduler.find(job_id)
        content_id = LogicNormal.get_content_id(scheduler_model.url)
        if content_id is None:
            logger.debug("scheduler url error %s", scheduler_model.url)
            return
        for i in range(120):  # 10초 간격으로 최대 120번. 즉, 20분
            video_url = LogicNormal.get_video_url(content_id)
            if video_url is None:
                time.sleep(10)  # 10초 대기
                continue
            logger.debug("scheduler download %s", scheduler_model.url)
            filename = date.today().strftime("%y%m%d") + "_" + scheduler_model.filename
            download = APIFFmpeg.download(
                package_name,
                f"{package_name}_{job_id}_{i}",
                video_url,
                filename,
                save_path=scheduler_model.save_path,
            )
            if download["ret"] != "success":
                logger.debug("scheduler download fail %s", download["ret"])
                logger.debug(download.get("log"))
                time.sleep(10)  # 10초 대기
                continue
            scheduler_model.update()
            while True:
                time.sleep(5)  # 5초 대기
                status = APIFFmpeg.status(package_name, f"{package_name}_{job_id}_{i}")
                if status["ret"] != "success":
                    logger.debug("scheduler status fail %s", status["ret"])
                    logger.debug(status.get("log"))
                    return
                if status["data"]["status"] == 0:
                    continue
                if status["data"]["status"] not in [5, 6, 7]:
                    # 혹시라도 다운로드 실패하면 처음부터
                    break
                # 다운로드 성공. 탈출
                return
            continue

    @staticmethod
    def get_scheduler():
        ret = []
        for scheduler_model in ModelScheduler.get_list(True):
            scheduler_model["last_time"] = (
                scheduler_model["last_time"].strftime("%m-%d %H:%M:%S"),
            )
            scheduler_model["path"] = os.path.join(
                scheduler_model["save_path"],
                date.today().strftime("%y%m%d") + "_" + scheduler_model["filename"],
            )
            scheduler_model["is_include"] = scheduler.is_include(
                f"{package_name}_{scheduler_model['id']}"
            )
            scheduler_model["is_running"] = scheduler.is_running(
                f"{package_name}_{scheduler_model['id']}"
            )
            ret.append(scheduler_model)
        return ret

    @staticmethod
    def add_scheduler(form):
        from .logic import Logic

        pattern = re.compile(r".+\..+$")
        if form["db_id"]:
            data = {
                "save_path": form["save_path"],
                "filename": form["filename"]
                if pattern.findall(form["filename"])
                else form["filename"] + ".mp4",
                "interval": form["interval"],
            }
            scheduler_model = ModelScheduler.find(form["db_id"])
            scheduler_model.update(data)
            if scheduler.is_include(f"{package_name}_{scheduler_model.id}"):
                Logic.scheduler_stop(scheduler_model.id)
                Logic.scheduler_start(scheduler_model.id)
        else:
            content_id = LogicNormal.get_content_id(form["url"])
            if content_id is None:
                logger.debug("url error %s", form["url"])
                return None
            content_info = LogicNormal.get_content_info(content_id)
            if content_info is None:
                logger.debug("url error %s", form["url"])
                return None
            data = {
                "url": f"https://now.naver.com/player/{content_id}",
                "title": content_info["title"],
                "host": ", ".join(content_info["hosts"]),
                "save_path": form["save_path"],
                "filename": form["filename"]
                if pattern.findall(form["filename"])
                else form["filename"] + ".mp4",
                "interval": form["interval"],
            }
            scheduler_model = ModelScheduler.create(data)
            if ModelSetting.get_bool("auto_start"):
                Logic.scheduler_start(scheduler_model.id)
        return LogicNormal.get_scheduler()

    @staticmethod
    def del_scheduler(db_id):
        from .logic import Logic

        logger.debug("del_scheduler %s", db_id)
        scheduler_model = ModelScheduler.find(db_id)
        if scheduler.is_include(f"{package_name}_{scheduler_model}"):
            Logic.scheduler_stop(scheduler_model.id)
        scheduler_model.delete()
        return LogicNormal.get_scheduler()

    @staticmethod
    def get_content_id(url):
        pattern = re.compile(r"^https?://now\.naver\.com/(player/)?(\d+)")
        match = pattern.findall(url)
        if not match:
            return None
        return match[0][1]

    @staticmethod
    def get_content_info(content_id):
        url = f"https://apis.naver.com/now_web/nowcms-api-xhmac/cms/v1/streams/{content_id}/shows/"
        headers = {"Referer": "https://now.naver.com/"}
        json = requests.get(url, headers=headers).json()
        if not json["title"]:
            return None
        return json

    @staticmethod
    def get_video_url(content_id):
        url = f"https://apis.naver.com/now_web/nowapi-xhmac/nnow/v2/stream/{content_id}/livestatus/"
        headers = {"Referer": "https://now.naver.com/"}
        json = requests.get(url, headers=headers).json()
        if json["status"]["status"] != "ONAIR":
            return None
        video_url = json["status"]["streamUrl"]
        secret_key = json["status"]["color"]  # 이젠 키도 받아야함
        m3u8 = AES.decrypt(video_url, secret_key)  # 주소가 암호화 되어 있음
        return m3u8
