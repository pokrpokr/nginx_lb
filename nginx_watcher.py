import requests
import time
import matplotlib.pyplot as plt
from datetime import datetime
import json
from collections import defaultdict
import numpy as np
import gc  # 添加垃圾回收

class NginxMonitor:
    def __init__(self, nginx_url="http://localhost:12345"):
        self.nginx_url = nginx_url
        self.history = defaultdict(lambda: defaultdict(list))
        self.timestamps = []
        self.max_history_points = 20  # 减少历史点数量
        plt.style.use('ggplot')
        
        # 调整图表大小和边距
        self.fig = plt.figure(figsize=(16, 12))  # 增加图表大小
        self.gs = self.fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)  # 增加子图之间的间距
        self.axes = {
            'connections': self.fig.add_subplot(self.gs[0, 0]),
            'scores': self.fig.add_subplot(self.gs[0, 1]),
            'performance': self.fig.add_subplot(self.gs[1, 0]),
            'components': self.fig.add_subplot(self.gs[1, 1])
        }
        
        # 调整整体布局
        self.fig.set_tight_layout(True)
        plt.ion()

    def get_stats(self):
        try:
            with requests.get(f"{self.nginx_url}/status/port_stats", timeout=5) as response:
                return response.json()
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return None
        
    def clean_old_data(self):
        """清理旧数据以释放内存"""
        if len(self.timestamps) > self.max_history_points:
            excess = len(self.timestamps) - self.max_history_points
            self.timestamps = self.timestamps[excess:]
            for port in self.history:
                for metric in self.history[port]:
                    if len(self.history[port][metric]) > self.max_history_points:
                        self.history[port][metric] = self.history[port][metric][excess:]

    def update_history(self, stats):
        if not stats:
            return

        current_time = datetime.strptime(stats['current_time'], '%a, %d %b %Y %H:%M:%S GMT')
        self.timestamps.append(current_time)

        # 更新数据
        for port, data in stats['port_statistics'].items():
            metrics = {
                'active_connections': data['active_connections'],
                'score': float(data['current_score']),
                'time_score': float(data['score_components']['time_score']),
                'count_score': float(data['score_components']['count_score']),
                'operation_score': float(data['score_components']['operation_score']),
                'avg_operation_time': float(data['performance_metrics']['avg_operation_time']),
                'time_factor': float(data['performance_metrics']['time_factor'])
            }
            for metric, value in metrics.items():
                self.history[port][metric].append(value)

        # 清理旧数据
        self.clean_old_data()
        gc.collect()  # 触发垃圾回收

    def plot_metrics(self):
        if not self.timestamps:
            print("No data to plot")
            return

        # 清除所有子图的内容
        for ax in self.axes.values():
            ax.clear()

        ports = list(self.history.keys())
        x = np.arange(len(ports))
        
        try:
            # 1. 活跃连接数竖向柱状图
            ax1 = self.axes['connections']
            current_connections = [self.history[port]['active_connections'][-1] for port in ports]
            # 确保数据有效
            current_connections = [0 if np.isnan(c) else int(c) for c in current_connections]
            bars = ax1.bar(x, current_connections, width=0.6)
            ax1.set_title('Current Active Connections', pad=20)
            ax1.set_xticks(x)
            ax1.set_xticklabels([f'Port {p}' for p in ports])
            
            for bar in bars:
                height = bar.get_height()
                if not np.isnan(height):  # 只显示有效值
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}',
                            ha='center', va='bottom')

            # 2. 端口评分趋势图
            ax2 = self.axes['scores']
            display_points = min(10, len(self.timestamps))
            for port in ports:
                scores = self.history[port]['score'][-display_points:]
                # 过滤无效值
                valid_scores = [s for s in scores if not np.isnan(s)]
                if valid_scores:  # 只在有有效数据时绘图
                    ax2.plot(self.timestamps[-len(valid_scores):], 
                            valid_scores,
                            label=f'Port {port}', marker='o', linewidth=2)
            ax2.set_title('Recent Port Scores', pad=20)
            ax2.legend(loc='upper left', bbox_to_anchor=(1, 1))
            ax2.grid(True)
            plt.setp(ax2.get_xticklabels(), rotation=45)

            # 3. 性能指标
            ax3 = self.axes['performance']
            width = 0.35
            op_times = [self.history[port]['avg_operation_time'][-1] for port in ports]
            time_factors = [self.history[port]['time_factor'][-1] for port in ports]
            
            # 处理无效值
            op_times = [0 if np.isnan(t) else float(t) for t in op_times]
            time_factors = [0 if np.isnan(t) else float(t) for t in time_factors]
            
            ax3.bar(x - width/2, op_times, width, label='Avg Op Time')
            ax3.bar(x + width/2, time_factors, width, label='Time Factor')
            ax3.set_title('Current Performance Metrics', pad=20)
            ax3.set_xticks(x)
            ax3.set_xticklabels([f'Port {p}' for p in ports])
            ax3.legend()

            # 4. 评分组件饼图
            ax4 = self.axes['components']
            if ports:
                port = ports[0]
                data = [
                    self.history[port]['time_score'][-1],
                    self.history[port]['count_score'][-1],
                    self.history[port]['operation_score'][-1]
                ]
                # 处理无效值
                data = [0 if np.isnan(d) else float(d) for d in data]
                if sum(data) > 0:  # 只在有有效数据时绘制饼图
                    ax4.pie(data, labels=['Time', 'Count', 'Operation'],
                           autopct='%1.1f%%', startangle=90)
                    ax4.set_title(f'Port {port} Score Components', pad=20)

            plt.draw()
            plt.pause(0.1)

        except Exception as e:
            print(f"Error plotting metrics: {e}")
            import traceback
            traceback.print_exc()  # 打印详细的错误信息

    def run(self, interval=1):
        try:
            while True:
                stats = self.get_stats()
                self.update_history(stats)
                self.plot_metrics()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        finally:
            plt.ioff()
            plt.close()
            gc.collect()  # 最终清理

if __name__ == "__main__":
    monitor = NginxMonitor()
    monitor.run(interval=1)