import json
import csv
from io import StringIO
from datetime import datetime


class Reporter:
    
    def generate(self, stats, format_type='text'):
        if format_type == 'json':
            return self.generate_json(stats)
        elif format_type == 'csv':
            return self.generate_csv(stats)
        else:
            return self.generate_text(stats)
    
    def generate_json(self, stats):
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_records': len(stats),
            'statistics': stats
        }
        
        if stats:
            report['summary'] = self._calculate_summary(stats)
        
        return json.dumps(report, indent=2)
    
    def generate_csv(self, stats):
        if not stats:
            return "No data available"
        
        output = StringIO()
        
        fieldnames = list(stats[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for stat in stats:
            writer.writerow(stat)
        
        return output.getvalue()
    
    def generate_text(self, stats):
        if not stats:
            return "No data available"
        
        lines = []
        lines.append("=" * 70)
        lines.append("SYSPULSE SYSTEM STATISTICS REPORT")
        lines.append("=" * 70)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Records: {len(stats)}")
        lines.append("")
        
        if stats:
            summary = self._calculate_summary(stats)
            lines.append("SUMMARY (All Records)")
            lines.append("-" * 70)
            lines.append(f"CPU Usage:        Avg: {summary['cpu']['avg']:.2f}%  "
                        f"Min: {summary['cpu']['min']:.2f}%  "
                        f"Max: {summary['cpu']['max']:.2f}%")
            lines.append(f"Memory Usage:     Avg: {summary['memory']['avg']:.2f}%  "
                        f"Min: {summary['memory']['min']:.2f}%  "
                        f"Max: {summary['memory']['max']:.2f}%")
            lines.append(f"Disk Usage:       Avg: {summary['disk']['avg']:.2f}%  "
                        f"Min: {summary['disk']['min']:.2f}%  "
                        f"Max: {summary['disk']['max']:.2f}%")
            
            if summary['network']['avg'] is not None:
                lines.append(f"Network Latency:  Avg: {summary['network']['avg']:.2f}ms  "
                            f"Min: {summary['network']['min']:.2f}ms  "
                            f"Max: {summary['network']['max']:.2f}ms")
            lines.append("")
        
        lines.append("RECENT RECORDS (Last 10)")
        lines.append("-" * 70)
        
        for stat in stats[:10]:
            lines.append(f"\nTimestamp: {stat['timestamp']}")
            lines.append(f"  CPU:     {stat['cpu_percent']}%")
            lines.append(f"  Memory:  {stat['memory_percent']}% "
                        f"({stat['memory_used_gb']:.2f}GB / {stat['memory_total_gb']:.2f}GB)")
            lines.append(f"  Disk:    {stat['disk_percent']}% "
                        f"({stat['disk_used_gb']:.2f}GB / {stat['disk_total_gb']:.2f}GB)")
            lines.append(f"  Uptime:  {self._format_uptime(stat['uptime_seconds'])}")
            
            if stat['network_latency_ms'] is not None:
                lines.append(f"  Network: {stat['network_latency_ms']}ms")
            else:
                lines.append(f"  Network: N/A")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _calculate_summary(self, stats):
        cpu_values = [s['cpu_percent'] for s in stats]
        memory_values = [s['memory_percent'] for s in stats]
        disk_values = [s['disk_percent'] for s in stats]
        network_values = [s['network_latency_ms'] for s in stats if s['network_latency_ms'] is not None]
        
        summary = {
            'cpu': {
                'avg': sum(cpu_values) / len(cpu_values),
                'min': min(cpu_values),
                'max': max(cpu_values)
            },
            'memory': {
                'avg': sum(memory_values) / len(memory_values),
                'min': min(memory_values),
                'max': max(memory_values)
            },
            'disk': {
                'avg': sum(disk_values) / len(disk_values),
                'min': min(disk_values),
                'max': max(disk_values)
            },
            'network': {
                'avg': sum(network_values) / len(network_values) if network_values else None,
                'min': min(network_values) if network_values else None,
                'max': max(network_values) if network_values else None
            }
        }
        
        return summary
    
    def _format_uptime(self, seconds):
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{int(days)}d")
        if hours > 0:
            parts.append(f"{int(hours)}h")
        if minutes > 0:
            parts.append(f"{int(minutes)}m")
        
        return " ".join(parts) if parts else "0m"


if __name__ == '__main__':
    test_stats = [
        {
            'id': 1,
            'timestamp': '2025-10-31T10:00:00',
            'cpu_percent': 45.5,
            'memory_percent': 62.3,
            'memory_used_gb': 10.5,
            'memory_total_gb': 16.0,
            'disk_percent': 75.2,
            'disk_used_gb': 150.0,
            'disk_total_gb': 200.0,
            'uptime_seconds': 86400,
            'network_latency_ms': 15.5
        },
        {
            'id': 2,
            'timestamp': '2025-10-31T10:01:00',
            'cpu_percent': 50.2,
            'memory_percent': 63.1,
            'memory_used_gb': 10.6,
            'memory_total_gb': 16.0,
            'disk_percent': 75.2,
            'disk_used_gb': 150.0,
            'disk_total_gb': 200.0,
            'uptime_seconds': 86460,
            'network_latency_ms': 16.2
        }
    ]
    
    reporter = Reporter()
    
    print("TEXT REPORT:")
    print(reporter.generate_text(test_stats))
    print("\n\nJSON REPORT:")
    print(reporter.generate_json(test_stats))
