import os
import traceback

from flask import Blueprint, request, render_template, redirect, jsonify
from flask_login import login_required

from framework import socketio
from framework.logger import get_logger

from .logic import Logic
from .logic_normal import LogicNormal
from .model import ModelSetting

package_name = __name__.split(".", maxsplit=1)[0]
logger = get_logger(package_name)

#########################################################
# 플러그인 공용
#########################################################
blueprint = Blueprint(
    package_name,
    package_name,
    url_prefix=f"/{package_name}",
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)

menu = {
    "main": [package_name, "NAVER NOW"],
    "sub": [["setting", "설정"], ["scheduler", "스케줄링"], ["log", "로그"]],
    "category": "service",
}

plugin_info = {
    "version": "1.1.0",
    "name": "naver_now",
    "category_name": "service",
    "developer": "joyfuI",
    "description": "NAVER NOW 다운로드",
    "home": "https://github.com/joyfuI/naver_now",
    "more": "",
}


def plugin_load():
    Logic.plugin_load()


def plugin_unload():
    Logic.plugin_unload()


#########################################################
# WEB Menu
#########################################################
@blueprint.route("/")
def home():
    return redirect(f"/{package_name}/scheduler")


@blueprint.route("/<sub>")
@login_required
def first_menu(sub):
    try:
        arg = {
            "package_name": package_name,
            "template_name": f"{package_name}_{sub}",
            "package_version": plugin_info["version"],
        }

        if sub == "setting":
            arg.update(ModelSetting.to_dict())
            return render_template(f"{package_name}_{sub}.html", arg=arg)

        elif sub == "scheduler":
            arg["save_path"] = ModelSetting.get("default_save_path")
            return render_template(f"{package_name}_{sub}.html", arg=arg)

        elif sub == "log":
            return render_template("log.html", package=package_name)
    except Exception as e:
        logger.error("Exception:%s", e)
        logger.error(traceback.format_exc())
    return render_template("sample.html", title=f"{package_name} - {sub}")


#########################################################
# For UI
#########################################################
@blueprint.route("/ajax/<sub>", methods=["POST"])
@login_required
def ajax(sub):
    logger.debug("AJAX %s %s", package_name, sub)
    try:
        # 공통 요청
        if sub == "setting_save":
            ret = ModelSetting.setting_save(request)
            return jsonify(ret)

        elif sub == "scheduler":
            go = request.form["scheduler"]
            job = request.form["sub"]
            logger.debug("scheduler:%s %s", job, go)
            if go == "true":
                Logic.scheduler_start(job)
            else:
                Logic.scheduler_stop(job)
            return jsonify(go)

        elif sub == "one_execute":
            job = request.form.get("sub")
            ret = Logic.one_execute(job)
            return jsonify(ret)

        # UI 요청
        elif sub == "list_scheduler":
            ret = LogicNormal.get_scheduler()
            return jsonify(ret)

        elif sub == "add_scheduler":
            ret = LogicNormal.add_scheduler(request.form)
            return jsonify(ret)

        elif sub == "del_scheduler":
            ret = LogicNormal.del_scheduler(request.form["id"])
            return jsonify(ret)
    except Exception as e:
        logger.error("Exception:%s", e)
        logger.error(traceback.format_exc())


#########################################################
# socketio
#########################################################
def socketio_emit(cmd, data):
    socketio.emit(cmd, data, namespace=f"/{package_name}", broadcast=True)
