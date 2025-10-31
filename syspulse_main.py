#!/usr/bin/env python3
import argparse
import configparser
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

from stats_collector import StatsCollector
from db_manager import DBManager
from reporter import Reporter
from notifier import Notifier


def load_config(config_path='config.ini'):
    config = configparser.ConfigParser()
    if not Path(config_path).exists():
        print(f"Warning: {config_path} not found, using defaults")
        return None
    config.read(config_path)
    return config


def collect_once(db_manager, collector):
    stats = collector.collect_all()
    db_manager.insert_stats(stats)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Stats collected")
    return stats


def run_daemon(interval, db_path, notify_enabled, notify_config):
    db_manager = DBManager(db_path)
    collector = StatsCollector()
    notifier = Notifier(notify_config) if notify_enabled else None
    
    last_notification = datetime.now()
    notification_interval = timedelta(hours=24)
    
    print(f"SysPulse daemon started (interval: {interval}s)")
    print(f"Database: {db_path}")
    print(f"Press Ctrl+C to stop\n")
    
    try:
        while True:
            collect_once(db_manager, collector)
            
            if notifier and (datetime.now() - last_notification) >= notification_interval:
                try:
                    stats = db_manager.get_stats_last_24h()
                    notifier.send_digest(stats)
                    last_notification = datetime.now()
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Daily digest sent")
                except Exception as e:
                    print(f"Error sending notification: {e}")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nSysPulse daemon stopped")


def generate_report(db_path, format_type, hours, output_file):
    db_manager = DBManager(db_path)
    reporter = Reporter()
    
    if hours:
        stats = db_manager.get_stats_last_hours(hours)
        print(f"Generating report for last {hours} hours...")
    else:
        stats = db_manager.get_all_stats()
        print("Generating report for all data...")
    
    if not stats:
        print("No data available for report")
        return
    
    report = reporter.generate(stats, format_type)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Report saved to {output_file}")
    else:
        print(report)


def main():
    parser = argparse.ArgumentParser(
        description='SysPulse - System monitoring and reporting tool'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    daemon_parser = subparsers.add_parser('start', help='Start monitoring daemon')
    daemon_parser.add_argument(
        '--interval', type=int, default=60,
        help='Collection interval in seconds (default: 60)'
    )
    daemon_parser.add_argument(
        '--config', default='config.ini',
        help='Configuration file path (default: config.ini)'
    )
    
    once_parser = subparsers.add_parser('collect', help='Collect stats once')
    once_parser.add_argument(
        '--config', default='config.ini',
        help='Configuration file path (default: config.ini)'
    )
    
    report_parser = subparsers.add_parser('report', help='Generate report')
    report_parser.add_argument(
        '--format', choices=['json', 'csv', 'text'], default='text',
        help='Report format (default: text)'
    )
    report_parser.add_argument(
        '--hours', type=int,
        help='Report for last N hours (default: all data)'
    )
    report_parser.add_argument(
        '--output', help='Output file (default: stdout)'
    )
    report_parser.add_argument(
        '--config', default='config.ini',
        help='Configuration file path (default: config.ini)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    config = load_config(args.config)
    
    if args.command == 'start':
        interval = args.interval
        db_path = config.get('database', 'path', fallback='data/syspulse.db') if config else 'data/syspulse.db'
        notify_enabled = config.getboolean('notifications', 'enabled', fallback=False) if config else False
        notify_config = dict(config['notifications']) if config and notify_enabled else {}
        
        run_daemon(interval, db_path, notify_enabled, notify_config)
    
    elif args.command == 'collect':
        db_path = config.get('database', 'path', fallback='data/syspulse.db') if config else 'data/syspulse.db'
        db_manager = DBManager(db_path)
        collector = StatsCollector()
        
        stats = collect_once(db_manager, collector)
        print(f"CPU: {stats['cpu_percent']}%")
        print(f"Memory: {stats['memory_percent']}%")
        print(f"Disk: {stats['disk_percent']}%")
        print(f"Network Latency: {stats['network_latency_ms']}ms")
    
    elif args.command == 'report':
        db_path = config.get('database', 'path', fallback='data/syspulse.db') if config else 'data/syspulse.db'
        generate_report(db_path, args.format, args.hours, args.output)


if __name__ == '__main__':
    main()
