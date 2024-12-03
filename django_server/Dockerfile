FROM python:3.9

# 安装 supervisor
RUN apt-get update && apt-get install -y supervisor

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装依赖
RUN pip install -r requirements.txt

# 复制 supervisor 配置文件
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 创建日志目录
RUN mkdir -p /var/log

# 设置权限
RUN chmod +x startup.sh

# 暴露端口
EXPOSE 8001 8002 8003 8004 8005

# 使用 supervisor 启动服务
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
