# -*- coding:utf-8 -*-
#!/usr/bin/env python

from fabric.api import *

#########################################
#   deploy for github
#########################################

def run():
    local('python run.py runserver')

def pub2hub():
    local('git status && '
            'git add . && '
            'git commit -m \'upgraded from local, update README.md & add fabfile.py & update .gitignore\' && '
            'git push origin master'
          )
