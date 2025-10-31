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
);

CREATE INDEX IF NOT EXISTS idx_timestamp ON system_stats(timestamp);
CREATE INDEX IF NOT EXISTS idx_cpu_percent ON system_stats(cpu_percent);
CREATE INDEX IF NOT EXISTS idx_memory_percent ON system_stats(memory_percent);
CREATE INDEX IF NOT EXISTS idx_disk_percent ON system_stats(disk_percent);
