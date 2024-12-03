FROM openresty/openresty:alpine

# 创建日志目录
RUN mkdir -p /var/log/nginx

# 复制配置文件和启动脚本
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh

# 设置正确的权限
RUN chmod 644 /usr/local/openresty/nginx/conf/nginx.conf && \
    chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]