# -*- coding: utf-8 -*-
# python
import traceback
import os
from datetime import datetime

# third-party

# sjva 공용
from framework import app, db, path_data
from framework.util import Util

# 패키지
from .plugin import logger, package_name

app.config['SQLALCHEMY_BINDS'][package_name] = 'sqlite:///%s' % os.path.join(path_data, 'db', '%s.db' % package_name)


class ModelSetting(db.Model):
    __tablename__ = '%s_setting' % package_name
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String, nullable=False)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    @staticmethod
    def get(key):
        try:
            return db.session.query(ModelSetting).filter_by(key=key).first().value.strip()
        except Exception as e:
            logger.error('Exception:%s %s', e, key)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_int(key):
        try:
            return int(ModelSetting.get(key))
        except Exception as e:
            logger.error('Exception:%s %s', e, key)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_bool(key):
        try:
            return ModelSetting.get(key) == 'True'
        except Exception as e:
            logger.error('Exception:%s %s', e, key)
            logger.error(traceback.format_exc())

    @staticmethod
    def set(key, value):
        try:
            item = db.session.query(ModelSetting).filter_by(key=key).with_for_update().first()
            if item is not None:
                item.value = value.strip()
                db.session.commit()
            else:
                db.session.add(ModelSetting(key, value.strip()))
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            logger.error('Error Key:%s Value:%s', key, value)

    @staticmethod
    def to_dict():
        try:
            return Util.db_list_to_dict(db.session.query(ModelSetting).all())
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def setting_save(req):
        try:
            for key, value in req.form.items():
                if key in ['scheduler', 'is_running']:
                    continue
                if key.startswith('tmp_'):
                    continue
                logger.debug('Key:%s Value:%s', key, value)
                entity = db.session.query(ModelSetting).filter_by(key=key).with_for_update().first()
                entity.value = value
            db.session.commit()
            return True
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return False

    @staticmethod
    def get_list(key):
        try:
            value = ModelSetting.get(key)
            values = [x.strip().strip() for x in value.replace('\n', '|').split('|')]
            values = Util.get_list_except_empty(values)
            return values
        except Exception as e:
            logger.error('Exception:%s %s', e, key)
            logger.error(traceback.format_exc())


class ModelScheduler(db.Model):
    __tablename__ = '%s_scheduler' % package_name
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    __bind_key__ = package_name

    id = db.Column(db.Integer, primary_key=True)
    last_time = db.Column(db.DateTime, nullable=False)
    url = db.Column(db.String, nullable=False)
    title = db.Column(db.String)
    host = db.Column(db.String)
    save_path = db.Column(db.String, nullable=False)
    filename = db.Column(db.String, nullable=False)
    interval = db.Column(db.String, nullable=False)

    def __init__(self, data):
        self.last_time = datetime.now()
        self.url = data['url']
        self.title = data['title']
        self.host = data['host']
        self.save_path = data['save_path']
        self.filename = data['filename']
        self.interval = data['interval']

    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}

    @staticmethod
    def get_list(by_dict=False):
        try:
            tmp = db.session.query(ModelScheduler).all()
            if by_dict:
                tmp = [x.as_dict() for x in tmp]
            return tmp
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def find(db_id):
        try:
            return db.session.query(ModelScheduler).filter_by(id=db_id).first()
        except Exception as e:
            logger.error('Exception:%s %s', e, db_id)
            logger.error(traceback.format_exc())

    @staticmethod
    def create(data):
        try:
            entity = ModelScheduler(data)
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            return None

    def update(self, data=None):
        try:
            if data is None:
                self.last_time = datetime.now()
            else:
                if 'save_path' in data:
                    self.save_path = data['save_path']
                if 'filename' in data:
                    self.filename = data['filename']
                if 'interval' in data:
                    self.interval = data['interval']
            db.session.commit()
            return True
        except Exception as e:
            logger.error('Exception:%s %s', e, self.id)
            logger.error(traceback.format_exc())
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            logger.error('Exception:%s %s', e, self.id)
            logger.error(traceback.format_exc())
            return False
