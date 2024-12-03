import docker
import requests
import time
import os

class ContainerManager:
    def __init__(self, base_port=8001):
        self.client = docker.from_client()
        self.base_port = base_port
        self.nginx_url = "http://nginx:80"
        self.network_name = "nginx_loadbalancer_default"  # Docker Compose 默认网络名

    def create_container(self):
        """创建新的 Django 容器"""
        # 找到可用的端口
        used_ports = self.get_used_ports()
        new_port = self.find_available_port(used_ports)
        
        # 容器配置
        container_name = f"django_server_{new_port}"
        container = self.client.containers.run(
            "django_server:latest",  # 使用已有的 Django 镜像
            environment={
                "DJANGO_SERVER_PORT": str(new_port),
                "HOST_MACHINE_IP": "host.docker.internal",
                "PYTHONUNBUFFERED": "1"
            },
            name=container_name,
            ports={f"{new_port}/tcp": new_port},
            network=self.network_name,
            detach=True
        )
        
        print(f"Created container {container_name} with port {new_port}")
        return container, new_port

    def remove_container(self, container_id):
        """移除指定的容器"""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            container.remove()
            print(f"Removed container {container_id}")
        except Exception as e:
            print(f"Error removing container: {e}")

    def get_used_ports(self):
        """获取已使用的端口"""
        used_ports = set()
        containers = self.client.containers.list()
        for container in containers:
            ports = container.attrs['NetworkSettings']['Ports']
            for port_mapping in ports.values():
                if port_mapping:
                    used_ports.add(int(port_mapping[0]['HostPort']))
        return used_ports

    def find_available_port(self, used_ports, start=8001, end=9000):
        """找到可用的端口"""
        for port in range(start, end + 1):
            if port not in used_ports:
                return port
        raise Exception("No available ports")

    def register_port(self, port):
        """向 Nginx 注册端口"""
        try:
            response = requests.post(
                f"{self.nginx_url}/register_port",
                data={"port": str(port)},
                timeout=5
            )
            if response.status_code == 200:
                print(f"Successfully registered port {port}")
                return True
            else:
                print(f"Failed to register port {port}: {response.text}")
                return False
        except Exception as e:
            print(f"Error registering port: {e}")
            return False

    def scale_up(self, count=1):
        """扩展指定数量的容器"""
        new_containers = []
        for _ in range(count):
            try:
                container, port = self.create_container()
                # 等待容器启动
                time.sleep(5)
                # 注册端口
                if self.register_port(port):
                    new_containers.append((container, port))
                else:
                    self.remove_container(container.id)
            except Exception as e:
                print(f"Error scaling up: {e}")
        return new_containers

    def scale_down(self, count=1):
        """减少指定数量的容器"""
        containers = self.client.containers.list(
            filters={"name": "django_server_"}
        )
        for container in containers[-count:]:
            self.remove_container(container.id)

if __name__ == "__main__":
    manager = ContainerManager()
    
    # 示例：扩展两个新容器
    print("Scaling up 2 containers...")
    new_containers = manager.scale_up(2)
    
    # 等待一段时间
    time.sleep(30)
    
    # 示例：减少一个容器
    print("Scaling down 1 container...")
    manager.scale_down(1) 