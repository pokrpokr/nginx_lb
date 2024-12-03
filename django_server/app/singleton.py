class Singleton(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ProjectList(metaclass=Singleton):
    def __init__(self):
        self._projects = []
        self._initialized = False
    
    def initialize(self, range_value):
        """初始化项目列表，确保只初始化一次"""
        if not self._initialized:
            self._projects = [{
                'name': f'project{i}',
                'description': f'project{i} description',
            } for i in range(1, range_value+1)]
            self._initialized = True
            print(f"Initialized ProjectList with {range_value} projects")  # 添加日志
    
    @property
    def projects(self):
        """获取所有项目"""
        return self._projects
    
    def get_project(self, project_id):
        """获取特定项目"""
        try:
            return self._projects[project_id - 1]
        except IndexError:
            return None
    
    def is_initialized(self):
        """检查是否已初始化"""
        return self._initialized