from django.apps import AppConfig
from .singleton import ProjectList
import os

def register_port():
    import requests
    try:
        container_port = os.environ['DJANGO_SERVER_PORT']
        host_machine_ip = os.environ.get('HOST_MACHINE_IP', 'host.docker.internal')
        
        # 注册的是宿主机的端口和IP
        response = requests.post(
            'http://nginx:80/register_port',  # 使用服务名访问nginx
            data={'port': container_port}
        )
        print(f"Port {container_port} registered successfully with host {host_machine_ip}")
    except Exception as e:
        print(f"Failed to register port: {e}")

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        project_list = ProjectList()
        project_list.initialize(10)
        register_port()

