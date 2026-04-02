"""
Alert System for Hand Hygiene Compliance Monitoring
Automatically detects non-compliance and creates alerts for supervisors
"""

from datetime import datetime, timedelta
from database import db
import logging

logger = logging.getLogger(__name__)

# Alert types
ALERT_TYPE_REMINDER = 'REMINDER'
ALERT_TYPE_TRAINING = 'TRAINING_REQUIRED'
ALERT_TYPE_SUPERVISOR = 'SUPERVISOR_NOTIFICATION'
ALERT_TYPE_ACCESS_VIOLATION = 'ACCESS_VIOLATION'


class AlertSystem:
    """
    Manages alert creation and acknowledgment for compliance violations
    """
    
    # Configuration thresholds
    COMPLIANCE_THRESHOLD = 70.0  # Minimum acceptable compliance rate (%)
    WASH_REMINDER_HOURS = 4  # Alert if no wash in X hours
    TRAINING_THRESHOLD = 60.0  # Create training alert if below this
    VIOLATION_THRESHOLD = 3  # Create supervisor alert after X violations
    
    @staticmethod
    def check_and_create_alerts(employee_id):
        """
        Check an employee for compliance issues and create appropriate alerts
        
        Args:
            employee_id: Employee to check
            
        Returns:
            list: List of alert IDs created
        """
        employee = db.get_employee(employee_id)
        if not employee:
            logger.warning(f"Alert check failed: Employee {employee_id} not found")
            return []
        
        alerts_created = []
        
        # Check 1: Compliance rate too low → TRAINING_REQUIRED
        if employee['compliance_rate'] < AlertSystem.TRAINING_THRESHOLD:
            alert_id = db.create_alert(
                employee_id,
                ALERT_TYPE_TRAINING,
                f"Compliance rate critically low at {employee['compliance_rate']:.1f}%. Training required."
            )
            alerts_created.append(alert_id)
            logger.info(f"Training alert created for {employee_id}")
        
        # Check 2: No wash in X hours → REMINDER
        if employee['last_wash_time']:
            last_wash = datetime.fromisoformat(employee['last_wash_time'])
            hours_since_wash = (datetime.now() - last_wash).total_seconds() / 3600
            
            if hours_since_wash > AlertSystem.WASH_REMINDER_HOURS:
                alert_id = db.create_alert(
                    employee_id,
                    ALERT_TYPE_REMINDER,
                    f"No hand washing event in {int(hours_since_wash)} hours. Please wash hands."
                )
                alerts_created.append(alert_id)
                logger.info(f"Reminder alert created for {employee_id}")
        else:
            # No wash events at all
            alert_id = db.create_alert(
                employee_id,
                ALERT_TYPE_REMINDER,
                "No hand washing events recorded. Please initiate hand washing."
            )
            alerts_created.append(alert_id)
        
        # Check 3: Multiple recent violations → SUPERVISOR_NOTIFICATION
        recent_violations = AlertSystem._count_recent_violations(employee_id)
        if recent_violations >= AlertSystem.VIOLATION_THRESHOLD:
            alert_id = db.create_alert(
                employee_id,
                ALERT_TYPE_SUPERVISOR,
                f"Multiple compliance violations detected ({recent_violations} in last 24 hours). Supervisor review needed."
            )
            alerts_created.append(alert_id)
            logger.warning(f"Supervisor notification alert created for {employee_id}")
        
        return alerts_created
    
    @staticmethod
    def create_access_violation_alert(employee_id, reason):
        """
        Create an alert for an access control violation
        
        Args:
            employee_id: Employee who was denied access
            reason: Reason for denial
        """
        alert_id = db.create_alert(
            employee_id,
            ALERT_TYPE_ACCESS_VIOLATION,
            f"Access denied to restricted area: {reason}"
        )
        logger.warning(f"Access violation alert created for {employee_id}: {reason}")
        return alert_id
    
    @staticmethod
    def _count_recent_violations(employee_id, hours=24):
        """
        Count incomplete wash events in the recent period
        
        Args:
            employee_id: Employee to check
            hours: Look back period in hours
            
        Returns:
            int: Number of violations (incomplete washes)
        """
        with db.get_connection() as conn:
            cursor = conn.cursor()
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT COUNT(*) as violations
                FROM wash_events
                WHERE employee_id = ? AND timestamp > ? AND compliant = 0
            ''', (employee_id, since))
            
            row = cursor.fetchone()
            return row['violations'] if row else 0
    
    @staticmethod
    def get_unacknowledged_alerts():
        """
        Get all unacknowledged alerts
        
        Returns:
            list: List of unacknowledged alerts with employee information
        """
        alerts = db.get_unacknowledged_alerts()
        logger.info(f"Retrieved {len(alerts)} unacknowledged alerts")
        return alerts
    
    @staticmethod
    def get_all_alerts(limit=100):
        """
        Get all alerts
        
        Returns:
            list: List of all alerts
        """
        return db.get_all_alerts(limit)
    
    @staticmethod
    def get_employee_alerts(employee_id, limit=20):
        """
        Get alerts for a specific employee
        
        Args:
            employee_id: Employee to get alerts for
            limit: Maximum number of alerts to retrieve
            
        Returns:
            list: List of alerts for the employee
        """
        return db.get_alerts_for_employee(employee_id, limit)
    
    @staticmethod
    def acknowledge_alert(alert_id, acknowledged_by):
        """
        Mark an alert as acknowledged
        
        Args:
            alert_id: Alert to acknowledge
            acknowledged_by: Name/ID of person acknowledging
            
        Returns:
            bool: True if successful
        """
        success = db.acknowledge_alert(alert_id, acknowledged_by)
        if success:
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        return success
    
    @staticmethod
    def get_alerts_by_type(alert_type, limit=100):
        """
        Get alerts filtered by type
        
        Args:
            alert_type: Type of alert to retrieve
            limit: Maximum number to retrieve
            
        Returns:
            list: List of alerts of the specified type
        """
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, e.name, e.department
                FROM alerts a
                LEFT JOIN employees e ON a.employee_id = e.employee_id
                WHERE a.alert_type = ?
                ORDER BY a.created_at DESC
                LIMIT ?
            ''', (alert_type, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_alerts_summary():
        """
        Get summary of alert statistics
        
        Returns:
            dict: Alert statistics
        """
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total unacknowledged
            cursor.execute('SELECT COUNT(*) as count FROM alerts WHERE acknowledged = 0')
            unacknowledged = cursor.fetchone()['count']
            
            # By type
            cursor.execute('''
                SELECT alert_type, COUNT(*) as count 
                FROM alerts 
                WHERE acknowledged = 0
                GROUP BY alert_type
            ''')
            by_type = {row['alert_type']: row['count'] for row in cursor.fetchall()}
            
            # Most alerted employees
            cursor.execute('''
                SELECT e.employee_id, e.name, COUNT(a.id) as alert_count
                FROM employees e
                LEFT JOIN alerts a ON e.employee_id = a.employee_id AND a.acknowledged = 0
                GROUP BY e.employee_id
                ORDER BY alert_count DESC
                LIMIT 5
            ''')
            top_alerted = [dict(row) for row in cursor.fetchall() if row['alert_count'] > 0]
            
            return {
                'total_unacknowledged': unacknowledged,
                'by_type': by_type,
                'top_alerted_employees': top_alerted
            }


class AlertNotificationService:
    """
    Service for sending alert notifications to supervisors
    Can be extended to send emails, SMS, push notifications, etc.
    """
    
    @staticmethod
    def notify_critical_alert(alert_id):
        """
        Send notification for critical alerts (supervisor notifications, violations)
        
        Args:
            alert_id: Alert ID to notify about
        """
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, e.name, e.department
                FROM alerts a
                LEFT JOIN employees e ON a.employee_id = e.employee_id
                WHERE a.id = ?
            ''', (alert_id,))
            alert = dict(cursor.fetchone()) if cursor.fetchone() else None
        
        if not alert:
            return False
        
        # Currently just logging - can be extended for email/SMS
        if alert['alert_type'] in [ALERT_TYPE_SUPERVISOR, ALERT_TYPE_ACCESS_VIOLATION]:
            logger.warning(f"CRITICAL ALERT: {alert['message']} - Employee: {alert['name']}, Department: {alert['department']}")
        
        return True
    
    @staticmethod
    def batch_notify_new_alerts():
        """
        Notify about all new unacknowledged critical alerts
        Called periodically (e.g., every 5 minutes)
        """
        alerts = AlertSystem.get_unacknowledged_alerts()
        critical_alerts = [a for a in alerts if a['alert_type'] in 
                          [ALERT_TYPE_SUPERVISOR, ALERT_TYPE_ACCESS_VIOLATION]]
        
        for alert in critical_alerts:
            AlertNotificationService.notify_critical_alert(alert['id'])
        
        logger.info(f"Batch notification processed: {len(critical_alerts)} critical alerts")
        return len(critical_alerts)


# Cloud-based notification extension (for future implementation)
class CloudNotificationService:
    """
    Future implementation for cloud-based notifications
    Can integrate with Azure Notification Hubs, SendGrid, Twilio, etc.
    """
    
    @staticmethod
    def send_email_alert(employee_email, alert_message):
        """Send alert via email"""
        # TODO: Implement email sending
        logger.info(f"Email alert would be sent to {employee_email}")
        pass
    
    @staticmethod
    def send_sms_alert(phone_number, alert_message):
        """Send alert via SMS"""
        # TODO: Implement SMS sending
        logger.info(f"SMS alert would be sent to {phone_number}")
        pass
    
    @staticmethod
    def send_push_notification(device_id, alert_message):
        """Send alert via push notification"""
        # TODO: Implement push notifications
        logger.info(f"Push notification would be sent to device {device_id}")
        pass


# Initialize global alert system
alert_system = AlertSystem()
