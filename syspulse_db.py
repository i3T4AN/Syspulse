import sqlite3
from pathlib import Path
from datetime import datetime, timedelta


class DBManager:
    
    def __init__(self, db_path='data/syspulse.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        schema_path = Path('schema.sql')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = f.read()
            cursor.executescript(schema)
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL NOT NULL,
                    memory_percent REAL NOT NULL,
                    memory_used_gb REAL NOT NULL,
                    memory_total_gb REAL NOT NULL,
                    disk_percent REAL NOT NULL,
                    disk_used_gb REAL NOT NULL,
                    disk_total_gb REAL NOT NULL,
                    uptime_seconds INTEGER NOT NULL,
                    network_latency_ms REAL
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON system_stats(timestamp)
            ''')
        
        conn.commit()
        conn.close()
    
    def insert_stats(self, stats):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_stats (
                timestamp, cpu_percent, memory_percent, memory_used_gb,
                memory_total_gb, disk_percent, disk_used_gb, disk_total_gb,
                uptime_seconds, network_latency_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stats['timestamp'],
            stats['cpu_percent'],
            stats['memory_percent'],
            stats['memory_used_gb'],
            stats['memory_total_gb'],
            stats['disk_percent'],
            stats['disk_used_gb'],
            stats['disk_total_gb'],
            stats['uptime_seconds'],
            stats['network_latency_ms']
        ))
        
        conn.commit()
        conn.close()
    
    def get_all_stats(self):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM system_stats ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_stats_last_hours(self, hours):
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM system_stats 
            WHERE timestamp >= ? 
            ORDER BY timestamp DESC
        ''', (cutoff,))
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_stats_last_24h(self):
        return self.get_stats_last_hours(24)
    
    def delete_old_stats(self, days):
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM system_stats WHERE timestamp < ?', (cutoff,))
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_stats_count(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM system_stats')
        count = cursor.fetchone()[0]
        
        conn.close()
        
        return count


if __name__ == '__main__':
    db = DBManager('data/test_syspulse.db')
    
    test_stats = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': 45.5,
        'memory_percent': 62.3,
        'memory_used_gb': 10.5,
        'memory_total_gb': 16.0,
        'disk_percent': 75.2,
        'disk_used_gb': 150.0,
        'disk_total_gb': 200.0,
        'uptime_seconds': 86400,
        'network_latency_ms': 15.5
    }
    
    db.insert_stats(test_stats)
    print(f"Inserted test record. Total records: {db.get_stats_count()}")
    
    stats = db.get_all_stats()
    if stats:
        print(f"\nLatest record:")
        latest = stats[0]
        print(f"  Timestamp: {latest['timestamp']}")
        print(f"  CPU: {latest['cpu_percent']}%")
        print(f"  Memory: {latest['memory_percent']}%")
