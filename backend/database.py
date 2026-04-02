"""
SQLite Database Layer for Hand Hygiene Compliance Monitoring System
Replaces PostgreSQL with SQLite for simplified deployment and portability
"""

import sqlite3
import os
import json
from datetime import datetime
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Default database path - can be overridden via environment variable
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'hand_hygiene.db')
DB_PATH = os.getenv('DATABASE_URL', f'sqlite:///{DEFAULT_DB_PATH}').replace('sqlite:///', '').replace('sqlite:///', '')


class Database:
    """SQLite Database Manager with context manager support"""
    
    def __init__(self, db_path=None):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file (uses env or default if not provided)
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database on first run
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        Usage: with db.get_connection() as conn: cursor = conn.cursor()
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Create all database tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Employees table - master record for each staff member
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    department TEXT NOT NULL,
                    rfid_tag TEXT,
                    compliance_rate REAL DEFAULT 0.0,
                    total_washes INTEGER DEFAULT 0,
                    last_wash_time TEXT,
                    last_wash_compliant INTEGER DEFAULT 0,
                    alert_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Wash events - individual hand washing events
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wash_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT NOT NULL,
                    station_id TEXT DEFAULT 'main',
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration REAL DEFAULT 0.0,
                    compliant INTEGER DEFAULT 0,
                    hand_movement_score REAL DEFAULT 0.0,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                )
            ''')
            
            # Access logs - track entry attempts at gates/areas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT NOT NULL,
                    gate_id TEXT DEFAULT 'icu_main',
                    access_granted INTEGER DEFAULT 0,
                    denial_reason TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                )
            ''')
            
            # Alerts - system alerts for non-compliance and access violations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    acknowledged INTEGER DEFAULT 0,
                    acknowledged_by TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
                )
            ''')
            
            # Departments - organization structure
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    compliance_target REAL DEFAULT 85.0
                )
            ''')
            
            # Daily statistics - aggregated daily data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    total_events INTEGER DEFAULT 0,
                    compliant_events INTEGER DEFAULT 0,
                    compliance_rate REAL DEFAULT 0.0
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_employee_id ON wash_events(employee_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_timestamp ON access_logs(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_employee ON alerts(employee_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_wash_timestamp ON wash_events(timestamp)')
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def backup(self, backup_path=None):
        """
        Backup SQLite database
        
        Args:
            backup_path: Path to save backup file (defaults to data/backup_<timestamp>.db)
        """
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
    
    def restore(self, backup_path):
        """
        Restore SQLite database from backup
        
        Args:
            backup_path: Path to backup file
        """
        try:
            import shutil
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Database restored from {backup_path}")
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise
    
    # ==================== EMPLOYEE OPERATIONS ====================
    
    def create_employee(self, employee_id, name, role, department, rfid_tag=None):
        """Create a new employee record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO employees (employee_id, name, role, department, rfid_tag)
                    VALUES (?, ?, ?, ?, ?)
                ''', (employee_id, name, role, department, rfid_tag))
                conn.commit()
                logger.info(f"Employee created: {employee_id}")
                return cursor.lastrowid
            except sqlite3.IntegrityError as e:
                logger.error(f"Employee already exists: {employee_id}")
                raise
    
    def get_employee(self, employee_id):
        """Get employee details by employee_id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM employees WHERE employee_id = ?', (employee_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_employees(self):
        """Get all employees with their current stats"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT e.*, COUNT(w.id) as event_count,
                       SUM(CASE WHEN w.compliant = 1 THEN 1 ELSE 0 END) as compliant_count
                FROM employees e
                LEFT JOIN wash_events w ON e.employee_id = w.employee_id
                GROUP BY e.id
                ORDER BY e.name
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_employees_by_department(self, department):
        """Get all employees in a specific department"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM employees WHERE department = ? ORDER BY name', 
                          (department,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_employee(self, employee_id, **kwargs):
        """Update employee fields"""
        allowed_fields = ['name', 'role', 'department', 'rfid_tag', 'compliance_rate', 
                         'total_washes', 'last_wash_time', 'last_wash_compliant', 'alert_count']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        set_clause = ', '.join([f'{k} = ?' for k in updates.keys()])
        values = list(updates.values()) + [employee_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE employees SET {set_clause} WHERE employee_id = ?', values)
            conn.commit()
            logger.info(f"Employee updated: {employee_id}")
            return cursor.rowcount > 0
    
    def get_employee_compliance_rate(self, employee_id):
        """Calculate current compliance rate for an employee"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as total, SUM(CASE WHEN compliant = 1 THEN 1 ELSE 0 END) as compliant
                FROM wash_events
                WHERE employee_id = ?
            ''', (employee_id,))
            row = cursor.fetchone()
            if row['total'] == 0:
                return 0.0
            return (row['compliant'] / row['total']) * 100
    
    # ==================== WASH EVENT OPERATIONS ====================
    
    def log_wash_event(self, employee_id, start_time, end_time=None, duration=0.0, 
                      compliant=False, hand_movement_score=0.0, station_id='main'):
        """Log a hand washing event"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO wash_events 
                (employee_id, station_id, start_time, end_time, duration, compliant, hand_movement_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, station_id, start_time, end_time, duration, int(compliant), hand_movement_score))
            conn.commit()
            
            # Update employee stats
            self._update_employee_wash_stats(employee_id, compliant, duration)
            
            logger.info(f"Wash event logged for {employee_id}: compliant={compliant}, duration={duration}s")
            return cursor.lastrowid
    
    def _update_employee_wash_stats(self, employee_id, compliant, duration):
        """Update employee's wash statistics after a wash event"""
        compliance_rate = self.get_employee_compliance_rate(employee_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE employees 
                SET compliance_rate = ?,
                    total_washes = total_washes + 1,
                    last_wash_time = CURRENT_TIMESTAMP,
                    last_wash_compliant = ?
                WHERE employee_id = ?
            ''', (compliance_rate, int(compliant), employee_id))
            conn.commit()
    
    def get_employee_history(self, employee_id, limit=50):
        """Get wash event history for an employee"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM wash_events
                WHERE employee_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (employee_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_wash_events_by_date_range(self, start_date, end_date):
        """Get wash events within a date range"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM wash_events
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== ACCESS CONTROL OPERATIONS ====================
    
    def log_access_attempt(self, employee_id, gate_id='icu_main', access_granted=False, 
                          denial_reason=None):
        """Log an access attempt to a restricted area"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO access_logs (employee_id, gate_id, access_granted, denial_reason)
                VALUES (?, ?, ?, ?)
            ''', (employee_id, gate_id, int(access_granted), denial_reason))
            conn.commit()
            logger.info(f"Access logged: {employee_id} -> {gate_id}: {'GRANTED' if access_granted else 'DENIED'}")
            return cursor.lastrowid
    
    def get_access_logs(self, employee_id=None, limit=100):
        """Get access logs, optionally filtered by employee"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if employee_id:
                cursor.execute('''
                    SELECT * FROM access_logs
                    WHERE employee_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (employee_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM access_logs
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== ALERT OPERATIONS ====================
    
    def create_alert(self, employee_id, alert_type, message):
        """Create an alert for an employee"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (employee_id, alert_type, message)
                VALUES (?, ?, ?)
            ''', (employee_id, alert_type, message))
            conn.commit()
            
            # Increment alert count for employee
            cursor.execute('UPDATE employees SET alert_count = alert_count + 1 WHERE employee_id = ?',
                          (employee_id,))
            conn.commit()
            
            logger.info(f"Alert created for {employee_id}: {alert_type} - {message}")
            return cursor.lastrowid
    
    def get_unacknowledged_alerts(self):
        """Get all unacknowledged alerts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, e.name, e.department
                FROM alerts a
                LEFT JOIN employees e ON a.employee_id = e.employee_id
                WHERE a.acknowledged = 0
                ORDER BY a.created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_alerts(self, limit=100):
        """Get all alerts (acknowledged and unacknowledged)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, e.name, e.department
                FROM alerts a
                LEFT JOIN employees e ON a.employee_id = e.employee_id
                ORDER BY a.created_at DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def acknowledge_alert(self, alert_id, acknowledged_by):
        """Mark an alert as acknowledged"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE alerts
                SET acknowledged = 1, acknowledged_by = ?
                WHERE id = ?
            ''', (acknowledged_by, alert_id))
            conn.commit()
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return cursor.rowcount > 0
    
    def get_alerts_for_employee(self, employee_id, limit=20):
        """Get alerts for a specific employee"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM alerts
                WHERE employee_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (employee_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== DEPARTMENT OPERATIONS ====================
    
    def create_department(self, name, compliance_target=85.0):
        """Create a new department"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO departments (name, compliance_target)
                VALUES (?, ?)
            ''', (name, compliance_target))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_departments(self):
        """Get all departments"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM departments')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_department_compliance_stats(self, department):
        """Get compliance statistics for a department"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    e.department,
                    COUNT(DISTINCT e.id) as total_employees,
                    AVG(e.compliance_rate) as avg_compliance,
                    SUM(CASE WHEN e.compliance_rate >= 85 THEN 1 ELSE 0 END) as compliant_employees,
                    SUM(CASE WHEN e.compliance_rate < 85 THEN 1 ELSE 0 END) as non_compliant_employees
                FROM employees e
                WHERE e.department = ?
                GROUP BY e.department
            ''', (department,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ==================== STATISTICS OPERATIONS ====================
    
    def get_daily_stats(self, date=None):
        """Get daily statistics"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM daily_stats WHERE date = ?', (date,))
            return dict(cursor.fetchone()) if cursor.fetchone() else None
    
    def update_daily_stats(self, date=None):
        """Calculate and update daily statistics"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate stats for the day
            cursor.execute(f'''
                SELECT 
                    COUNT(*) as total_events,
                    SUM(CASE WHEN compliant = 1 THEN 1 ELSE 0 END) as compliant_events
                FROM wash_events
                WHERE DATE(timestamp) = ?
            ''', (date,))
            row = cursor.fetchone()
            
            total = row['total_events'] or 0
            compliant = row['compliant_events'] or 0
            rate = (compliant / total * 100) if total > 0 else 0.0
            
            # Insert or update daily stats
            cursor.execute('''
                INSERT OR REPLACE INTO daily_stats (date, total_events, compliant_events, compliance_rate)
                VALUES (?, ?, ?, ?)
            ''', (date, total, compliant, rate))
            conn.commit()
            
            return {'date': date, 'total_events': total, 'compliant_events': compliant, 'compliance_rate': rate}
    
    def get_overall_stats(self):
        """Get overall system statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Employee stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_employees,
                    AVG(compliance_rate) as avg_compliance,
                    SUM(total_washes) as total_washes
                FROM employees
            ''')
            emp_stats = dict(cursor.fetchone())
            
            # Event stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_events,
                    SUM(CASE WHEN compliant = 1 THEN 1 ELSE 0 END) as compliant_events,
                    AVG(duration) as avg_duration
                FROM wash_events
            ''')
            event_stats = dict(cursor.fetchone())
            
            return {**emp_stats, **event_stats}


# Initialize global database instance
db = Database()
