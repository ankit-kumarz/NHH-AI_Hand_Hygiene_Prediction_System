"""
Enhanced Flask App with SQLite Database and Employee Tracking
Complete Employee Tracking System with Access Control
"""

import os 
import logging
from datetime import datetime
from flask import Flask, jsonify, request 
from flask_cors import CORS
from database import db
from access_control import access_manager
from alert_system import AlertSystem, AlertNotificationService
from dotenv import load_dotenv
import cv2 
import numpy as np
import base64
from ai_model_service import get_model_service

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 


def create_app(config=None):
    """
    Application factory with SQLite support
    
    Environment variables:
    - DATABASE_URL: SQLite database path (defaults to data/hand_hygiene.db)
    - FLASK_ENV: development/production
    - SECRET_KEY: Flask secret key
    """
    app = Flask(__name__)
    
    # Configuration
    if config:
        app.config.update(config)
    else:
        app.config['JSON_SORT_KEYS'] = False
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'data/hand_hygiene.db')
    
    # CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # ==================== HEALTH & STATUS ====================
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200
    
    @app.route('/', methods=['GET']) 
    def root():
        """API root endpoint"""
        return jsonify({
            'name': 'Hand Hygiene Compliance Monitoring System',
            'version': '3.0.0',
            'status': 'running',
            'database': 'SQLite', 
            'timestamp': datetime.utcnow().isoformat(),
            'features': [
                'AI Hand Detection',
                'Employee Tracking',
                'Access Control System',
                'Alert Management',
                'Compliance Analytics',
                'Real-time Dashboard'
            ], 
            'endpoints': {
                'health': '/api/health',
                'employees': 'GET /api/employees',
                'employee_detail': 'GET /api/employees/<id>',
                'employee_create': 'POST /api/employees',
                'employee_update': 'PUT /api/employees/<id>',
                'employee_history': 'GET /api/employees/<id>/history',
                'employees_by_dept': 'GET /api/employees/department/<dept>',
                'access_request': 'POST /api/access/request',
                'access_logs': 'GET /api/access/logs',
                'wash_event': 'POST /api/wash-event',
                'wash_history': 'GET /api/wash-events/<employee_id>',
                'alerts': 'GET /api/alerts',
                'alerts_unacknowledged': 'GET /api/alerts/unacknowledged',
                'alert_create': 'POST /api/alerts',
                'alert_acknowledge': 'PUT /api/alerts/<id>/acknowledge',
                'stats_overall': 'GET /api/stats/overall',
                'stats_daily': 'GET /api/stats/daily',
                'stats_department': 'GET /api/stats/department/<dept>'
            }
        }), 200
    
    # ==================== EMPLOYEE MANAGEMENT ====================
    
    @app.route('/api/employees', methods=['GET'])
    def get_all_employees():
        """Get all employees with their compliance stats"""
        try:
            employees = db.get_all_employees()
            return jsonify({
                'success': True,
                'count': len(employees),
                'employees': employees,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error fetching employees: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/employees/<employee_id>', methods=['GET'])
    def get_employee(employee_id):
        """Get specific employee details"""
        try:
            employee = db.get_employee(employee_id)
            if not employee:
                return jsonify({'success': False, 'error': 'Employee not found'}), 404
            return jsonify({'success': True, 'employee': employee}), 200
        except Exception as e:
            logger.error(f"Error fetching employee {employee_id}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/employees', methods=['POST'])
    def create_employee():
        """Create a new employee"""
        try:
            data = request.json
            required = ['employee_id', 'name', 'role', 'department']
            
            if not all(k in data for k in required):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            emp_id = db.create_employee(
                data['employee_id'],
                data['name'],
                data['role'],
                data['department'], 
                data.get('rfid_tag')
            )
            
            logger.info(f"Employee created: {data['employee_id']}")
            return jsonify({
                'success': True,
                'message': 'Employee created successfully',
                'employee_id': emp_id
            }), 201
        except Exception as e:
            logger.error(f"Error creating employee: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/employees/<employee_id>', methods=['PUT'])
    def update_employee(employee_id):
        """Update employee information"""
        try:
            data = request.json
            success = db.update_employee(employee_id, **data)
            
            if not success:
                return jsonify({'success': False, 'error': 'Employee not found'}), 404
            
            return jsonify({
                'success': True,
                'message': 'Employee updated successfully'
            }), 200
        except Exception as e:
            logger.error(f"Error updating employee {employee_id}: {e}") 
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/employees/<employee_id>/history', methods=['GET'])
    def get_employee_history(employee_id):
        """Get wash event history for an employee"""
        try:
            limit = request.args.get('limit', 50, type=int)
            history = db.get_employee_history(employee_id, limit)
            
            return jsonify({
                'success': True,
                'employee_id': employee_id,
                'count': len(history),
                'events': history,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error fetching history for {employee_id}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/employees/department/<department>', methods=['GET'])
    def get_department_employees(department):
        """Get all employees in a department"""
        try:
            employees = db.get_employees_by_department(department)
            stats = db.get_department_compliance_stats(department)
            
            return jsonify({
                'success': True,
                'department': department,
                'count': len(employees),
                'employees': employees,
                'stats': stats,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error fetching department {department}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== ACCESS CONTROL ====================
    
    @app.route('/api/access/request', methods=['POST'])
    def request_access():
        """Request access to restricted area"""
        try:
            data = request.json
            employee_id = data.get('employee_id')
            gate_id = data.get('gate_id', 'icu_main')
            
            if not employee_id:
                return jsonify({'success': False, 'error': 'Employee ID required'}), 400
            
            result = access_manager.request_entry(gate_id, employee_id)
            
            # Create alert if access denied for critical reasons
            if not result['access_granted'] and result['denial_reason'] in ['LOW_COMPLIANCE_RATE', 'WASH_NOT_COMPLIANT']:
                AlertSystem.create_access_violation_alert(employee_id, result['denial_reason'])
            
            return jsonify({
                'success': True,
                'access': result,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error processing access request: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/access/logs', methods=['GET'])
    def get_access_logs():
        """Get access attempt logs"""
        try:
            limit = request.args.get('limit', 100, type=int)
            logs = db.get_access_logs(limit=limit)
            
            return jsonify({
                'success': True,
                'count': len(logs),
                'logs': logs,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error fetching access logs: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== WASH EVENTS ====================
    
    @app.route('/api/wash-event', methods=['POST'])
    def log_wash_event():
        """Log a hand washing event"""
        try:
            data = request.json
            required = ['employee_id', 'start_time', 'duration']
            
            if not all(k in data for k in required):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            event_id = db.log_wash_event(
                data['employee_id'],
                data['start_time'],
                data.get('end_time'),
                data['duration'],
                data.get('compliant', False),
                data.get('hand_movement_score', 0.0),
                data.get('station_id', 'main')
            )
            
            # Check for compliance alerts
            AlertSystem.check_and_create_alerts(data['employee_id'])
            
            logger.info(f"Wash event logged: {data['employee_id']}")
            return jsonify({
                'success': True,
                'message': 'Wash event logged successfully',
                'event_id': event_id
            }), 201
        except Exception as e:
            logger.error(f"Error logging wash event: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/wash-events/<employee_id>', methods=['GET'])
    def get_wash_events(employee_id):
        """Get wash events for an employee"""
        try:
            limit = request.args.get('limit', 50, type=int)
            events = db.get_employee_history(employee_id, limit)
            
            return jsonify({
                'success': True,
                'employee_id': employee_id,
                'count': len(events),
                'events': events
            }), 200
        except Exception as e:
            logger.error(f"Error fetching wash events: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== ALERTS ====================
    
    @app.route('/api/alerts', methods=['GET'])
    def get_alerts():
        """Get all alerts"""
        try:
            limit = request.args.get('limit', 100, type=int)
            alerts = db.get_all_alerts(limit)
            
            return jsonify({
                'success': True,
                'count': len(alerts),
                'alerts': alerts,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/alerts/unacknowledged', methods=['GET'])
    def get_unacknowledged_alerts():
        """Get unacknowledged alerts"""
        try:
            alerts = db.get_unacknowledged_alerts()
            summary = AlertSystem.get_alerts_summary()
            
            return jsonify({
                'success': True,
                'count': len(alerts),
                'alerts': alerts,
                'summary': summary,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error fetching unacknowledged alerts: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/alerts', methods=['POST'])
    def create_alert():
        """Create an alert"""
        try:
            data = request.json
            required = ['employee_id', 'alert_type', 'message']
            
            if not all(k in data for k in required):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            alert_id = db.create_alert(
                data['employee_id'],
                data['alert_type'],
                data['message']
            )
            
            return jsonify({
                'success': True,
                'message': 'Alert created successfully',
                'alert_id': alert_id
            }), 201
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/alerts/<alert_id>/acknowledge', methods=['PUT'])
    def acknowledge_alert(alert_id):
        """Acknowledge an alert"""
        try:
            data = request.json
            acknowledged_by = data.get('acknowledged_by', 'system')
            
            success = db.acknowledge_alert(alert_id, acknowledged_by)
            if not success:
                return jsonify({'success': False, 'error': 'Alert not found'}), 404
            
            return jsonify({
                'success': True,
                'message': 'Alert acknowledged successfully'
            }), 200
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== STATISTICS ====================
    
    @app.route('/api/stats/overall', methods=['GET'])
    def get_overall_stats():
        """Get overall system statistics"""
        try:
            stats = db.get_overall_stats()
            
            # Calculate compliance_rate if not present
            total_events = stats.get('total_events') or 0
            compliant_events = stats.get('compliant_events') or 0
            compliance_rate = (compliant_events / total_events * 100) if total_events > 0 else 0
            
            # Ensure all required fields are present
            response_data = {
                'success': True,
                'total_employees': stats.get('total_employees') or 0,
                'total_events': total_events,
                'compliant_events': compliant_events,
                'incomplete_events': total_events - compliant_events,
                'compliance_rate': compliance_rate,
                'avg_duration': stats.get('avg_duration') or 0,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return jsonify(response_data), 200
        except Exception as e:
            logger.error(f"Error fetching overall stats: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/stats/daily', methods=['GET'])
    def get_daily_stats():
        """Get daily statistics"""
        try:
            date = request.args.get('date')
            stats = db.update_daily_stats(date)
            
            return jsonify({
                'success': True,
                'stats': stats,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error fetching daily stats: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/stats/department/<department>', methods=['GET'])
    def get_department_stats(department):
        """Get department compliance statistics"""
        try:
            stats = db.get_department_compliance_stats(department)
            
            if not stats:
                return jsonify({'success': False, 'error': 'Department not found'}), 404
            
            return jsonify({
                'success': True,
                'stats': stats,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error fetching department stats: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== AI MODEL ENDPOINTS ====================
    
    @app.route('/api/ai/model-status', methods=['GET'])
    def ai_model_status():
        """Check AI model status"""
        try:
            model_service = get_model_service()
            status = 'ready' if model_service.model else 'not_loaded'
            
            return jsonify({
                'success': True,
                'status': status,
                'model_loaded': model_service.model is not None,
                'config': model_service.config if model_service.config else None
            }), 200
        except Exception as e:
            logger.error(f"Error checking model status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/predict', methods=['POST'])
    def ai_predict():
        """
        Run AI prediction on image frame
        Expects: base64 encoded image or raw binary
        Returns: prediction result with confidence
        """
        try:
            model_service = get_model_service()
            
            if model_service.model is None:
                return jsonify({'success': False, 'error': 'Model not loaded'}), 503
            
            # Get image from request
            if 'image' not in request.files and 'image_data' not in request.json:
                return jsonify({'success': False, 'error': 'No image provided'}), 400
            
            # Decode image
            if 'image' in request.files:
                file = request.files['image']
                image_data = file.read()
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                # Base64 encoded image
                image_base64 = request.json.get('image_data')
                image_data = base64.b64decode(image_base64)
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return jsonify({'success': False, 'error': 'Invalid image data'}), 400
            
            # Run prediction
            prediction = model_service.predict(frame)
            
            if prediction is None:
                return jsonify({'success': False, 'error': 'Prediction failed'}), 500
            
            return jsonify({
                'success': True,
                'prediction': prediction
            }), 200
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/metrics', methods=['GET'])
    def ai_metrics():
        """Get AI model performance metrics"""
        try:
            model_service = get_model_service()
            metrics = model_service.get_metrics()
            
            return jsonify({
                'success': True,
                'metrics': metrics,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/ai/metrics/reset', methods=['POST'])
    def ai_metrics_reset():
        """Reset AI model metrics"""
        try:
            model_service = get_model_service()
            model_service.reset_metrics()
            
            return jsonify({
                'success': True,
                'message': 'Metrics reset successfully'
            }), 200
        except Exception as e:
            logger.error(f"Error resetting metrics: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # ==================== ERROR HANDLERS ====================
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("🏥 Hand Hygiene Compliance Monitoring System")
    print("=" * 60)
    print("📦 Version: 3.0.0")
    print("💾 Database: SQLite")
    print("🚀 Server: http://localhost:5000")
    print("📊 API Docs: http://localhost:5000/")
    print("=" * 60)
    print("Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
