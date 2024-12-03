#!/bin/bash

# 等待 Nginx 启动
sleep 5

# 启动 Django 服务
DJANGO_SERVER_PORT=8001 python manage.py runserver 0.0.0.0:8001 &
DJANGO_SERVER_PORT=8002 python manage.py runserver 0.0.0.0:8002 &
DJANGO_SERVER_PORT=8003 python manage.py runserver 0.0.0.0:8003 &
DJANGO_SERVER_PORT=8004 python manage.py runserver 0.0.0.0:8004 &
DJANGO_SERVER_PORT=8005 python manage.py runserver 0.0.0.0:8005 &

# 保持容器运行
wait
