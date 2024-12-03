#!/bin/sh

# 确保日志目录存在
mkdir -p /var/log/nginx

# 创建日志文件（如果不存在）
touch /var/log/nginx/access.log
touch /var/log/nginx/error.log
touch /var/log/nginx/info.log

# 设置正确的权限
chmod 666 /var/log/nginx/*.log
chmod 777 /var/log/nginx

# 输出一些调试信息
echo "=== Checking log files and permissions ==="
ls -la /var/log/nginx/

# 测试日志写入
echo "=== Testing log write access ===" >> /var/log/nginx/error.log
echo "=== Testing log write access ===" >> /var/log/nginx/info.log

# 启动 OpenResty
echo "=== Starting OpenResty ==="
exec /usr/local/openresty/bin/openresty -g "daemon off;" 