import psutil
import socket
import time
from datetime import datetime


class StatsCollector:
    
    def __init__(self, ping_host='8.8.8.8', ping_port=53):
        self.ping_host = ping_host
        self.ping_port = ping_port
    
    def get_cpu_percent(self, interval=1):
        return psutil.cpu_percent(interval=interval)
    
    def get_memory_usage(self):
        mem = psutil.virtual_memory()
        return {
            'percent': mem.percent,
            'used_gb': mem.used / (1024 ** 3),
            'total_gb': mem.total / (1024 ** 3)
        }
    
    def get_disk_usage(self, path='/'):
        disk = psutil.disk_usage(path)
        return {
            'percent': disk.percent,
            'used_gb': disk.used / (1024 ** 3),
            'total_gb': disk.total / (1024 ** 3)
        }
    
    def get_uptime_seconds(self):
        boot_time = psutil.boot_time()
        return time.time() - boot_time
    
    def get_network_latency(self):
        try:
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.ping_host, self.ping_port))
            sock.close()
            latency_ms = (time.time() - start) * 1000
            return round(latency_ms, 2)
        except (socket.timeout, socket.error):
            return None
    
    def collect_all(self):
        cpu = self.get_cpu_percent(interval=0.5)
        memory = self.get_memory_usage()
        disk = self.get_disk_usage()
        uptime = self.get_uptime_seconds()
        latency = self.get_network_latency()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': round(cpu, 2),
            'memory_percent': round(memory['percent'], 2),
            'memory_used_gb': round(memory['used_gb'], 2),
            'memory_total_gb': round(memory['total_gb'], 2),
            'disk_percent': round(disk['percent'], 2),
            'disk_used_gb': round(disk['used_gb'], 2),
            'disk_total_gb': round(disk['total_gb'], 2),
            'uptime_seconds': int(uptime),
            'network_latency_ms': latency
        }


if __name__ == '__main__':
    collector = StatsCollector()
    stats = collector.collect_all()
    
    print("System Statistics:")
    print(f"Timestamp: {stats['timestamp']}")
    print(f"CPU: {stats['cpu_percent']}%")
    print(f"Memory: {stats['memory_percent']}% ({stats['memory_used_gb']:.2f}GB / {stats['memory_total_gb']:.2f}GB)")
    print(f"Disk: {stats['disk_percent']}% ({stats['disk_used_gb']:.2f}GB / {stats['disk_total_gb']:.2f}GB)")
    print(f"Uptime: {stats['uptime_seconds']}s")
    print(f"Network Latency: {stats['network_latency_ms']}ms" if stats['network_latency_ms'] else "Network Latency: N/A")
