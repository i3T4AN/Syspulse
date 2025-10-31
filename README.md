# SysPulse

SysPulse is a self-contained, cross-platform system health monitor and reporter built in Python. It periodically collects system metrics such as CPU load, memory usage, disk utilization, uptime, and network latency, then stores them in a lightweight local SQLite database. SysPulse can generate reports in JSON, CSV, or plain text formats, and optionally send daily digests via email or webhook.

---

## Features

* **Cross-platform:** Runs on Windows, macOS, and Linux.
* **Lightweight:** No external services required; uses only `psutil` and `requests`.
* **Automated collection:** Periodically gathers CPU, memory, disk, and network stats.
* **Local database:** Stores metrics in SQLite for easy querying and persistence.
* **Flexible reporting:** Output summaries in JSON, CSV, or plain text.
* **Optional alerts:** Send daily digests via SMTP email or webhook.
* **Configurable retention:** Automatically purges old data based on retention settings.

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/i3t4an/SysPulse.git
cd SysPulse
pip install -r syspulse_requirements.txt
```

---

## Usage

Run SysPulse manually for a single reading:

```bash
python syspulse_main.py --once
```

Run continuously (default 60-second interval):

```bash
python syspulse_main.py
```

Generate a report:

```bash
python syspulse_main.py --report json
```

---

## Configuration

All runtime behavior is defined in `syspulse_config.txt`. Example:

```ini
[database]
path = data/syspulse.db

[collection]
interval = 60
ping_host = 8.8.8.8

[notifications]
enabled = false
type = email
smtp_host = smtp.gmail.com
smtp_port = 587
smtp_user = your_email@gmail.com
smtp_password = your_app_password
from_email = syspulse@localhost
to_email = recipient@example.com
webhook_url = https://hooks.example.com/syspulse

[maintenance]
retention_days = 30
```

---

## Database Schema

The SQLite schema is defined in `syspulse_schema.sql`:

```sql
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
```

---

## Project Structure

```
SysPulse/
├── syspulse_main.py         # Entry point and CLI
├── syspulse_stats.py        # Collects system metrics
├── syspulse_db.py           # Database management (SQLite)
├── syspulse_reporter.py     # Generates summaries
├── syspulse_notifier.py     # Handles email/webhook notifications
├── syspulse_config.txt      # Configuration file
├── syspulse_schema.sql      # SQLite table definitions
├── syspulse_requirements.txt# Dependencies
```

---

## Example Output

**JSON Report Example:**

```json
{
  "timestamp": "2025-10-31T12:00:00Z",
  "cpu_percent": 34.6,
  "memory_percent": 52.1,
  "disk_percent": 71.8,
  "uptime_seconds": 128940,
  "network_latency_ms": 23.4
}
```

**CSV Report Example:**

```csv
timestamp,cpu_percent,memory_percent,disk_percent,uptime_seconds,network_latency_ms
2025-10-31T12:00:00Z,34.6,52.1,71.8,128940,23.4
```

---

## License

MIT License © 2025 i3t4an
