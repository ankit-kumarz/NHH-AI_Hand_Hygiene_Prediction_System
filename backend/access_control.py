"""
Access Control System for ICU and Restricted Areas
Enforces hand hygiene compliance before allowing entry
"""

from datetime import datetime, timedelta
from database import db
import logging

logger = logging.getLogger(__name__)

# Configuration
REQUIRED_WASH_DURATION = 20  # seconds (WHO standard)
WASH_VALIDITY_DURATION = 300  # 5 minutes in seconds
RECENT_WASH_THRESHOLD = 4  # hours for reminder alerts


class ICUGate:
    """
    Access control system for ICU and other restricted areas.
    Validates employee hygiene compliance before granting entry.
    """
    
    def __init__(self, gate_id='icu_main'):
        """
        Initialize ICU Gate
        
        Args:
            gate_id: Unique identifier for this gate/entry point
        """
        self.gate_id = gate_id
    
    def request_entry(self, employee_id):
        """
        Request entry to restricted area. Checks compliance before granting access.
        
        Args:
            employee_id: Employee requesting access
            
        Returns:
            dict: {
                'access_granted': bool,
                'denial_reason': str or None,
                'last_wash_time': datetime or None,
                'last_wash_duration': float or None,
                'last_wash_compliant': bool,
                'employee_name': str,
                'message': str
            }
        """
        logger.info(f"Access request from {employee_id} at {self.gate_id}")
        
        # Get employee information
        employee = db.get_employee(employee_id)
        if not employee:
            denial_reason = 'EMPLOYEE_NOT_FOUND'
            db.log_access_attempt(employee_id, self.gate_id, False, denial_reason)
            logger.warning(f"Access denied: Employee {employee_id} not found")
            return {
                'access_granted': False,
                'denial_reason': denial_reason,
                'last_wash_time': None,
                'last_wash_duration': None,
                'last_wash_compliant': False,
                'employee_name': 'Unknown',
                'message': 'Employee not found in system'
            }
        
        # Get last wash event
        history = db.get_employee_history(employee_id, limit=1)
        
        if not history:
            denial_reason = 'NO_RECENT_WASH'
            db.log_access_attempt(employee_id, self.gate_id, False, denial_reason)
            logger.warning(f"Access denied: {employee_id} has no wash events")
            return {
                'access_granted': False,
                'denial_reason': denial_reason,
                'last_wash_time': None,
                'last_wash_duration': None,
                'last_wash_compliant': False,
                'employee_name': employee['name'],
                'message': 'No hand wash events recorded. Please wash your hands first.'
            }
        
        last_wash = history[0]
        last_wash_time = datetime.fromisoformat(last_wash['timestamp'])
        time_since_wash = datetime.now() - last_wash_time
        
        # Check if wash is within validity window (5 minutes)
        if time_since_wash > timedelta(seconds=WASH_VALIDITY_DURATION):
            denial_reason = 'WASH_EXPIRED'
            db.log_access_attempt(employee_id, self.gate_id, False, denial_reason)
            logger.warning(f"Access denied: {employee_id} - wash too old ({time_since_wash})")
            return {
                'access_granted': False,
                'denial_reason': denial_reason,
                'last_wash_time': last_wash['timestamp'],
                'last_wash_duration': last_wash['duration'],
                'last_wash_compliant': bool(last_wash['compliant']),
                'employee_name': employee['name'],
                'message': f'Last wash was {int(time_since_wash.total_seconds() / 60)} minutes ago. Please wash again.'
            }
        
        # Check if last wash was compliant (20+ seconds)
        if not last_wash['compliant']:
            denial_reason = 'WASH_NOT_COMPLIANT'
            db.log_access_attempt(employee_id, self.gate_id, False, denial_reason)
            logger.warning(f"Access denied: {employee_id} - incomplete wash ({last_wash['duration']}s)")
            return {
                'access_granted': False,
                'denial_reason': denial_reason,
                'last_wash_time': last_wash['timestamp'],
                'last_wash_duration': last_wash['duration'],
                'last_wash_compliant': False,
                'employee_name': employee['name'],
                'message': f'Last wash was incomplete ({last_wash["duration"]:.1f}s). Must wash for {REQUIRED_WASH_DURATION} seconds.'
            }
        
        # Check employee compliance rate
        if employee['compliance_rate'] < 70:
            denial_reason = 'LOW_COMPLIANCE_RATE'
            db.log_access_attempt(employee_id, self.gate_id, False, denial_reason)
            logger.warning(f"Access denied: {employee_id} - low compliance ({employee['compliance_rate']:.1f}%)")
            return {
                'access_granted': False,
                'denial_reason': denial_reason,
                'last_wash_time': last_wash['timestamp'],
                'last_wash_duration': last_wash['duration'],
                'last_wash_compliant': True,
                'employee_name': employee['name'],
                'message': f'Access denied: Your compliance rate is {employee["compliance_rate"]:.1f}%. Please contact your supervisor.'
            }
        
        # All checks passed - GRANT ACCESS
        db.log_access_attempt(employee_id, self.gate_id, True, None)
        logger.info(f"Access GRANTED: {employee_id} at {self.gate_id}")
        
        return {
            'access_granted': True,
            'denial_reason': None,
            'last_wash_time': last_wash['timestamp'],
            'last_wash_duration': last_wash['duration'],
            'last_wash_compliant': True,
            'employee_name': employee['name'],
            'message': f'Welcome, {employee["name"]}! Access granted.'
        }
    
    def check_access_summary(self, employee_id):
        """
        Get current access status without logging an attempt
        Useful for checking if employee would be granted access
        
        Args:
            employee_id: Employee to check
            
        Returns:
            dict: Access status and reasons
        """
        # Similar to request_entry but without logging
        employee = db.get_employee(employee_id)
        if not employee:
            return {
                'would_grant_access': False,
                'reason': 'EMPLOYEE_NOT_FOUND',
                'employee_name': 'Unknown'
            }
        
        history = db.get_employee_history(employee_id, limit=1)
        if not history:
            return {
                'would_grant_access': False,
                'reason': 'NO_RECENT_WASH',
                'employee_name': employee['name'],
                'last_wash_time': None
            }
        
        last_wash = history[0]
        last_wash_time = datetime.fromisoformat(last_wash['timestamp'])
        time_since_wash = datetime.now() - last_wash_time
        
        if time_since_wash > timedelta(seconds=WASH_VALIDITY_DURATION):
            return {
                'would_grant_access': False,
                'reason': 'WASH_EXPIRED',
                'employee_name': employee['name'],
                'last_wash_time': last_wash['timestamp'],
                'minutes_until_required_wash': 0
            }
        
        if not last_wash['compliant']:
            return {
                'would_grant_access': False,
                'reason': 'WASH_NOT_COMPLIANT',
                'employee_name': employee['name'],
                'last_wash_time': last_wash['timestamp'],
                'last_wash_duration': last_wash['duration']
            }
        
        if employee['compliance_rate'] < 70:
            return {
                'would_grant_access': False,
                'reason': 'LOW_COMPLIANCE_RATE',
                'employee_name': employee['name'],
                'compliance_rate': employee['compliance_rate']
            }
        
        # Would grant access
        minutes_until_wash_required = int((WASH_VALIDITY_DURATION - time_since_wash.total_seconds()) / 60)
        
        return {
            'would_grant_access': True,
            'reason': 'COMPLIANCE_MET',
            'employee_name': employee['name'],
            'last_wash_time': last_wash['timestamp'],
            'minutes_until_wash_required': minutes_until_wash_required,
            'compliance_rate': employee['compliance_rate']
        }
    
    def get_access_logs(self, limit=50):
        """Get recent access attempts at this gate"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM access_logs
                WHERE gate_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (self.gate_id, limit))
            return [dict(row) for row in cursor.fetchall()]


class AccessControlManager:
    """
    Manages multiple gates and access control policies
    """
    
    def __init__(self):
        """Initialize with default gates"""
        self.gates = {
            'icu_main': ICUGate('icu_main'),
            'icu_secondary': ICUGate('icu_secondary'),
            'surgery': ICUGate('surgery'),
            'isolation': ICUGate('isolation')
        }
    
    def register_gate(self, gate_id):
        """Register a new gate"""
        if gate_id not in self.gates:
            self.gates[gate_id] = ICUGate(gate_id)
            logger.info(f"Gate registered: {gate_id}")
    
    def request_entry(self, gate_id, employee_id):
        """Request entry through a specific gate"""
        if gate_id not in self.gates:
            self.register_gate(gate_id)
        
        return self.gates[gate_id].request_entry(employee_id)
    
    def get_gate_statistics(self, gate_id):
        """Get statistics for a specific gate"""
        if gate_id not in self.gates:
            return None
        
        gate = self.gates[gate_id]
        logs = gate.get_access_logs(limit=100)
        
        granted = sum(1 for log in logs if log['access_granted'])
        denied = len(logs) - granted
        
        return {
            'gate_id': gate_id,
            'total_attempts': len(logs),
            'access_granted': granted,
            'access_denied': denied,
            'success_rate': (granted / len(logs) * 100) if logs else 0,
            'recent_logs': logs[:10]
        }


# Initialize global access control manager
access_manager = AccessControlManager()
