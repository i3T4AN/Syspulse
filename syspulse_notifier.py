import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class Notifier:
    
    def __init__(self, config):
        self.config = config
        self.notification_type = config.get('type', 'email')
    
    def send_digest(self, stats):
        if self.notification_type == 'email':
            return self._send_email(stats)
        elif self.notification_type == 'webhook':
            return self._send_webhook(stats)
        else:
            raise ValueError(f"Unknown notification type: {self.notification_type}")
    
    def _send_email(self, stats):
        smtp_host = self.config.get('smtp_host', 'localhost')
        smtp_port = int(self.config.get('smtp_port', 587))
        smtp_user = self.config.get('smtp_user', '')
        smtp_password = self.config.get('smtp_password', '')
        from_addr = self.config.get('from_email', 'syspulse@localhost')
        to_addr = self.config.get('to_email', '')
        
        if not to_addr:
            raise ValueError("No recipient email address configured")
        
        summary = self._generate_summary(stats)
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"SysPulse Daily Digest - {datetime.now().strftime('%Y-%m-%d')}"
        msg['From'] = from_addr
        msg['To'] = to_addr
        
        text_content = self._format_email_text(summary)
        text_part = MIMEText(text_content, 'plain')
        msg.attach(text_part)
        
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            raise Exception(f"Failed to send email: {e}")
    
    def _send_webhook(self, stats):
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for webhook notifications")
        
        webhook_url = self.config.get('webhook_url', '')
        if not webhook_url:
            raise ValueError("No webhook URL configured")
        
        summary = self._generate_summary(stats)
        
        payload = {
            'timestamp': datetime.now().isoformat(),
            'period': 'last_24h',
            'total_records': len(stats),
            'summary': summary
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            raise Exception(f"Failed to send webhook: {e}")
    
    def _generate_summary(self, stats):
        if not stats:
            return {
                'cpu': {'avg': 0, 'min': 0, 'max': 0},
                'memory': {'avg': 0, 'min': 0, 'max': 0},
                'disk': {'avg': 0, 'min': 0, 'max': 0},
                'network': {'avg': None, 'min': None, 'max': None}
            }
        
        cpu_values = [s['cpu_percent'] for s in stats]
        memory_values = [s['memory_percent'] for s in stats]
        disk_values = [s['disk_percent'] for s in stats]
        network_values = [s['network_latency_ms'] for s in stats if s.get('network_latency_ms') is not None]
        
        return {
            'cpu': {
                'avg': round(sum(cpu_values) / len(cpu_values), 2),
                'min': round(min(cpu_values), 2),
                'max': round(max(cpu_values), 2)
            },
            'memory': {
                'avg': round(sum(memory_values) / len(memory_values), 2),
                'min': round(min(memory_values), 2),
                'max': round(max(memory_values), 2)
            },
            'disk': {
                'avg': round(sum(disk_values) / len(disk_values), 2),
                'min': round(min(disk_values), 2),
                'max': round(max(disk_values), 2)
            },
            'network': {
                'avg': round(sum(network_values) / len(network_values), 2) if network_values else None,
                'min': round(min(network_values), 2) if network_values else None,
                'max': round(max(network_values), 2) if network_values else None
            }
        }
    
    def _format_email_text(self, summary):
        lines = []
        lines.append("SysPulse Daily Digest")
        lines.append("=" * 50)
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append(f"Period: Last 24 hours")
        lines.append("")
        lines.append("System Statistics Summary:")
        lines.append("-" * 50)
        lines.append(f"CPU Usage:")
        lines.append(f"  Average: {summary['cpu']['avg']}%")
        lines.append(f"  Minimum: {summary['cpu']['min']}%")
        lines.append(f"  Maximum: {summary['cpu']['max']}%")
        lines.append("")
        lines.append(f"Memory Usage:")
        lines.append(f"  Average: {summary['memory']['avg']}%")
        lines.append(f"  Minimum: {summary['memory']['min']}%")
        lines.append(f"  Maximum: {summary['memory']['max']}%")
        lines.append("")
        lines.append(f"Disk Usage:")
        lines.append(f"  Average: {summary['disk']['avg']}%")
        lines.append(f"  Minimum: {summary['disk']['min']}%")
        lines.append(f"  Maximum: {summary['disk']['max']}%")
        lines.append("")
        
        if summary['network']['avg'] is not None:
            lines.append(f"Network Latency:")
            lines.append(f"  Average: {summary['network']['avg']}ms")
            lines.append(f"  Minimum: {summary['network']['min']}ms")
            lines.append(f"  Maximum: {summary['network']['max']}ms")
            lines.append("")
        
        lines.append("=" * 50)
        lines.append("Generated by SysPulse")
        
        return "\n".join(lines)


if __name__ == '__main__':
    test_stats = [
        {
            'cpu_percent': 45.5,
            'memory_percent': 62.3,
            'disk_percent': 75.2,
            'network_latency_ms': 15.5
        },
        {
            'cpu_percent': 50.2,
            'memory_percent': 63.1,
            'disk_percent': 75.3,
            'network_latency_ms': 16.2
        }
    ]
    
    notifier = Notifier({'type': 'webhook', 'webhook_url': 'http://example.com/hook'})
    summary = notifier._generate_summary(test_stats)
    print("Summary:")
    print(json.dumps(summary, indent=2))
    
    email_text = notifier._format_email_text(summary)
    print("\nEmail Text:")
    print(email_text)
