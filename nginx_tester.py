import requests
import random
import time
import json
from datetime import datetime

class NginxTester:
    def __init__(self, base_url="http://localhost:12345"):
        self.base_url = base_url
        self.project_count = 10  # 与 Django 项目中初始化的项目数量一致

    def log_response(self, response, endpoint):
        """记录响应信息"""
        print(f"\n[{datetime.now()}] Testing {endpoint}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        if 'port' in response.json():
            print(f"Served by port: {response.json()['port']}")

    def test_get_projects(self):
        """测试获取所有项目列表"""
        try:
            response = requests.get(f"{self.base_url}/projects/")
            self.log_response(response, "GET /projects/")
            return response.ok
        except Exception as e:
            print(f"Error testing /projects/: {e}")
            return False

    def test_get_project(self, project_id=None):
        """测试获取单个项目"""
        if project_id is None:
            project_id = random.randint(1, self.project_count)
        try:
            response = requests.get(f"{self.base_url}/project/{project_id}/")
            self.log_response(response, f"GET /project/{project_id}/")
            return response.ok
        except Exception as e:
            print(f"Error testing /project/{project_id}/: {e}")
            return False

    def test_update_project(self, project_id=None):
        """测试更新项目信息"""
        if project_id is None:
            project_id = random.randint(1, self.project_count)
        try:
            new_description = f"Updated description at {datetime.now()}"
            response = requests.post(
                f"{self.base_url}/project/{project_id}/info/",
                json={"description": new_description}
            )
            self.log_response(response, f"POST /project/{project_id}/info/")
            return response.ok
        except Exception as e:
            print(f"Error testing /project/{project_id}/info/: {e}")
            return False

    def run_random_tests(self, count=10, interval=2):
        """运行随机测试"""
        print(f"Starting random tests ({count} iterations)...")
        
        test_methods = [
            # self.test_get_projects,
            lambda: self.test_get_project(),
            lambda: self.test_update_project()
        ]

        success_count = 0
        for i in range(count):
            print(f"\nTest iteration {i + 1}/{count}")
            test_method = random.choice(test_methods)
            if test_method():
                success_count += 1
            time.sleep(interval)

        print(f"\nTest completed. Success rate: {success_count}/{count}")

    def run_sequential_tests(self, iterations=3, interval=2):
        """按顺序运行所有测试"""
        print("Starting sequential tests...")
        
        for i in range(iterations):
            print(f"\nIteration {i + 1}/{iterations}")
            
            # 测试获取项目列表
            self.test_get_projects()
            time.sleep(interval)
            
            # 测试获取随机项目
            project_id = random.randint(1, self.project_count)
            self.test_get_project(project_id)
            time.sleep(interval)
            
            # 测试更新项目
            self.test_update_project(project_id)
            time.sleep(interval)

if __name__ == "__main__":
    tester = NginxTester()
    
    # 运行随机测试
    print("=== Running Random Tests ===")
    for i in range(100):
        # random_sleep = random.randint(1, 5)
        # if i > 0 and i % 15 == 0:
        #     random_sleep = random.randint(60, 65)
        
        # print(f"Sleeping for {random_sleep} seconds")
        tester.run_random_tests(count=1, interval=1)
    
    # print("\n=== Running Sequential Tests ===")
    # tester.run_sequential_tests(iterations=3, interval=1)
