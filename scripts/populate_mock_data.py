"""
Mock Data Population Script for Hand Hygiene Compliance System
Generates sample employees, wash events, and alerts for demonstration
"""

import sys
import os
from datetime import datetime, timedelta
import random
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import db

# Mock data
DEPARTMENTS = {
    'ICU': {'target': 90.0, 'employees': ['Dr. Sarah Chen', 'Nurse Emily Watson', 'Dr. Michael Johnson']},
    'ER': {'target': 85.0, 'employees': ['Dr. James Smith', 'Nurse Maria Garcia']},
    'General Ward': {'target': 80.0, 'employees': ['Dr. Lisa Anderson', 'Nurse John Brown', 'Nurse David Wilson']},
    'Pediatrics': {'target': 85.0, 'employees': ['Dr. Rachel Green', 'Nurse Anna White']}
}

ROLES = {
    'Dr.': 'Doctor',
    'Nurse': 'Nursing Staff'
}

def create_mock_employees():
    """Create mock employee records"""
    print("Creating mock employees...")
    
    employees_created = []
    emp_counter = 1000
    
    for dept, data in DEPARTMENTS.items():
        for name in data['employees']:
            emp_id = f'EMP{emp_counter}'
            role = 'Doctor' if name.startswith('Dr.') else'Nursing Staff'
            
            try:
                db.create_employee(
                    employee_id=emp_id,
                    name=name,
                    role=role,
                    department=dept
                )
                employees_created.append({
                    'id': emp_id,
                    'name': name,
                    'department': dept,
                    'role': role
                })
                print(f"  ✓ Created: {name} ({emp_id}) - {dept}")
                emp_counter += 1
            except Exception as e:
                print(f"  ✗ Failed to create {name}: {e}")
    
    return employees_created

def generate_wash_events(employees):
    """Generate mock wash events for the past 7 days"""
    print("\nGenerating wash events...")
    
    events_created = 0
    
    for emp in employees:
        # Random number of events per employee (5-15)
        num_events = random.randint(5, 15)
        
        for i in range(num_events):
            # Random time in past 7 days
            days_ago = random.randint(0, 6)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            event_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # Random duration (15-30 seconds mostly, some less than 20)
            duration = random.choice([
                random.uniform(8, 15),    # 30% non-compliant (< 20s)
                random.uniform(20, 35),   # 70% compliant (>= 20s)
            ]) if random.random() < 0.7 else random.uniform(20, 35)
            
            compliant = duration >= 20
            
            try:
                db.log_wash_event(
                    employee_id=emp['id'],
                    start_time=event_time.isoformat(),
                    end_time=(event_time + timedelta(seconds=duration)).isoformat(),
                    duration=duration,
                    compliant=compliant,
                    hand_movement_score=random.uniform(0.5, 1.0),
                    station_id='main'
                )
                events_created += 1
            except Exception as e:
                print(f"  ✗ Failed to create event for {emp['name']}: {e}")
    
    print(f"  ✓ Created {events_created} wash events")
    return events_created

def generate_alerts(employees):
    """Generate mock alerts for employees"""
    print("\nGenerating sample alerts...")
    
    alerts_created = 0
    
    # Find employees with low compliance
    for emp in employees:
        emp_data = db.get_employee(emp['id'])
        
        # Create alerts for low compliance employees
        if emp_data and emp_data['compliance_rate'] < 70:
            try:
                db.create_alert(
                    emp['id'],
                    'TRAINING_REQUIRED',
                    f"Compliance rate is {emp_data['compliance_rate']:.1f}%. Training session required."
                )
                alerts_created += 1
                print(f"  ✓ Alert created for {emp['name']}: Low compliance")
            except Exception as e:
                print(f"  ✗ Failed to create alert: {e}")
        
        # Create reminder alerts for some employees
        if random.random() < 0.3:
            try:
                db.create_alert(
                    emp['id'],
                    'REMINDER',
                    "Please remember to wash hands before patient contact."
                )
                alerts_created += 1
            except Exception as e:
                print(f"  ✗ Failed to create reminder: {e}")
    
    print(f"  ✓ Created {alerts_created} alerts")
    return alerts_created

def generate_access_logs(employees):
    """Generate mock access control logs"""
    print("\nGenerating access control logs...")
    
    logs_created = 0
    
    for emp in employees:
        # 3-8 access attempts per employee in past 3 days
        num_attempts = random.randint(3, 8)
        
        for i in range(num_attempts):
            hours_ago = random.randint(0, 72)  # Last 3 days
            attempt_time = (datetime.now() - timedelta(hours=hours_ago)).isoformat()
            
            emp_data = db.get_employee(emp['id'])
            
            # Simulate access decisions based on compliance
            if emp_data['compliance_rate'] >= 75 and random.random() < 0.8:
                # Likely to grant
                access_granted = True
                denial_reason = None
            else:
                # Might deny
                access_granted = random.random() < 0.3
                denial_reason = random.choice(['LOW_COMPLIANCE_RATE', 'WASH_EXPIRED', 'WASH_NOT_COMPLIANT']) if not access_granted else None
            
            try:
                db.log_access_attempt(
                    emp['id'],
                    'icu_main',
                    access_granted,
                    denial_reason
                )
                logs_created += 1
            except Exception as e:
                print(f"  ✗ Failed to create access log: {e}")
    
    print(f"  ✓ Created {logs_created} access logs")
    return logs_created

def print_summary(employees, events, alerts, logs):
    """Print summary of created data"""
    print("\n" + "="*60)
    print("MOCK DATA POPULATION COMPLETE")
    print("="*60)
    print(f"\n✓ Employees Created: {len(employees)}")
    print(f"✓ Wash Events Created: {events}")
    print(f"✓ Alerts Created: {alerts}")
    print(f"✓ Access Logs Created: {logs}")
    
    # Print compliance statistics
    print("\n" + "-"*60)
    print("COMPLIANCE STATISTICS")
    print("-"*60)
    
    all_employees = db.get_all_employees()
    
    compliant = sum(1 for e in all_employees if (e['compliance_rate'] or 0) >= 85)
    good = sum(1 for e in all_employees if 70 <= (e['compliance_rate'] or 0) < 85)
    needs_attention = sum(1 for e in all_employees if (e['compliance_rate'] or 0) < 70)
    
    avg_compliance = sum(e['compliance_rate'] or 0 for e in all_employees) / len(all_employees) if all_employees else 0
    
    print(f"\nCompliance Distribution:")
    print(f"  Excellent (≥85%): {compliant} employees")
    print(f"  Good (70-84%): {good} employees")
    print(f"  Needs Attention (<70%): {needs_attention} employees")
    print(f"\nAverage Compliance Rate: {avg_compliance:.1f}%")
    
    # Print by department
    print(f"\nCompliance by Department:")
    departments = set(e['department'] for e in all_employees)
    
    for dept in sorted(departments):
        dept_emps = [e for e in all_employees if e['department'] == dept]
        avg_dept = sum(e['compliance_rate'] or 0 for e in dept_emps) / len(dept_emps) if dept_emps else 0
        print(f"  {dept}: {avg_dept:.1f}% ({len(dept_emps)} employees)")
    
    print(f"\n" + "="*60)
    print("Database: {database_path}")
    print("="*60)

if __name__ == '__main__':
    try:
        print("\n" + "="*60)
        print("HAND HYGIENE COMPLIANCE SYSTEM - MOCK DATA GENERATOR")
        print("="*60 + "\n")
        
        # Create employees
        employees = create_mock_employees()
        
        if not employees:
            print("\n✗ Failed to create employees. Aborting.")
            sys.exit(1)
        
        # Generate data
        events = generate_wash_events(employees)
        alerts = generate_alerts(employees)
        logs = generate_access_logs(employees)
        
        # Print summary
        print_summary(employees, events, alerts, logs)
        
        print("\n✓ Mock data population successful!")
        print("You can now start the system and test with the generated data.\n")
        
    except Exception as e:
        print(f"\n✗ Error during population: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
