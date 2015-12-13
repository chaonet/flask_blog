# -*- coding:utf-8 -*-
#!/usr/bin/env python
from migrate.versioning import api # 执行 migrate 命令
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app import db
import os.path

db.create_all()
# None

if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    # 在基本目录下创建名为 'db_repository' 的存储库
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository') # 在指定的路径创建一个空的存储库(文件夹), 第一个参数中有文件夹名，第二个参数没有实际意义……
    # 创建一个数据库，并与 存储库 关联，由存储库进行版本控制
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO) # 指定一个特定的数据库url 和 一个 存储库
else:
    # 默认情况下,数据库版本从0开始和假设是空的。如果不是空的数据库,您可以指定它从一个版本开始。
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

# api.version，显示存储库中，有效的最后版本
# [SQLAlchemy Migrate](https://sqlalchemy-migrate.readthedocs.org/en/latest/versioning.html#database-schema-versioning-workflow)