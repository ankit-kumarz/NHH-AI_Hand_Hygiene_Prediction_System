"""
Hygiene Routes - REST API endpoints for hand hygiene events
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func
from models.db import db, HygieneEvent, DailyStats, User
from realtime.events import (
    broadcast_completion_alert,
    broadcast_failure_alert,
    broadcast_status_update,
    broadcast_system_alert
)

hygiene_bp = Blueprint('hygiene', __name__, url_prefix='/api')


# ========== LOG ENDPOINTS ==========

@hygiene_bp.route('/log', methods=['POST'])
def log_event():
    """
    Log a new hand hygiene event
    
    Expected JSON:
    {
        "user_id": "USER123",
        "duration": 22.5,
        "status": "completed",
        "location": "ICU",
        "department": "Critical Care"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'duration' not in data or 'status' not in data:
            return jsonify({'error': 'Missing required fields: duration, status'}), 400
        
        user_id = data.get('user_id', 'system')
        duration = float(data.get('duration', 0))
        status = data.get('status', 'incomplete')
        location = data.get('location', None)
        department = data.get('department', None)
        
        # Check compliance (WHO 20-second rule)
        compliance = duration >= 20
        
        # Create event
        event = HygieneEvent(
            user_id=user_id,
            duration=duration,
            status=status,
            compliance=compliance,
            location=location,
            department=department,
            end_time=datetime.utcnow()
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Broadcast real-time alert
        if compliance:
            broadcast_completion_alert({
                'user_id': user_id,
                'duration': round(duration, 1),
                'location': location,
                'message': f'✅ Proper handwashing completed ({duration:.1f}s)'
            })
        else:
            broadcast_failure_alert({
                'user_id': user_id,
                'duration': round(duration, 1),
                'location': location,
                'message': f'⚠️ Insufficient handwash time ({duration:.1f}s < 20s)'
            })
        
        # Update status
        broadcast_status_update({
            'event_id': event.id,
            'user_id': user_id,
            'status': status,
            'compliance': compliance
        })
        
        return jsonify({
            'success': True,
            'message': 'Event logged successfully',
            'event': event.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@hygiene_bp.route('/logs', methods=['GET'])
def get_logs():
    """
    Fetch all hygiene events with optional filtering
    
    Query params:
    - user_id: Filter by user
    - status: Filter by status (completed/incomplete)
    - days: Last N days (default: 7)
    - limit: Max results (default: 100)
    """
    try:
        user_id = request.args.get('user_id', None)
        status = request.args.get('status', None)
        days = int(request.args.get('days', 7))
        limit = int(request.args.get('limit', 100))
        
        # Base query
        query = HygieneEvent.query
        
        # Apply filters
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Filter by date range
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(HygieneEvent.created_at >= start_date)
        
        # Order by newest first and limit
        events = query.order_by(HygieneEvent.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(events),
            'events': [event.to_dict() for event in events]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hygiene_bp.route('/logs/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get specific event by ID"""
    try:
        event = HygieneEvent.query.get(event_id)
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        return jsonify({
            'success': True,
            'event': event.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== STATISTICS ENDPOINTS ==========

@hygiene_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get overall statistics
    
    Query params:
    - days: Last N days (default: 7)
    - user_id: Specific user stats
    """
    try:
        days = int(request.args.get('days', 7))
        user_id = request.args.get('user_id', None)
        
        # Base query
        query = HygieneEvent.query
        
        # Filter by date
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(HygieneEvent.created_at >= start_date)
        
        # Filter by user if provided
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        events = query.all()
        
        # Calculate stats
        total = len(events)
        completed = sum(1 for e in events if e.status == 'completed')
        incomplete = sum(1 for e in events if e.status == 'incomplete')
        compliant = sum(1 for e in events if e.compliance)
        
        avg_duration = sum(e.duration for e in events) / total if total > 0 else 0
        compliance_rate = (compliant / total * 100) if total > 0 else 0
        
        return jsonify({
            'success': True,
            'period_days': days,
            'total_events': total,
            'completed_events': completed,
            'incomplete_events': incomplete,
            'compliant_events': compliant,
            'compliance_rate': round(compliance_rate, 2),
            'avg_duration': round(avg_duration, 1),
            'user_id': user_id if user_id else 'all'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hygiene_bp.route('/stats/daily', methods=['GET'])
def get_daily_stats():
    """
    Get daily statistics trend
    
    Query params:
    - days: Last N days (default: 30)
    """
    try:
        days = int(request.args.get('days', 30))
        
        # Get daily stats
        daily_stats = DailyStats.query.filter(
            DailyStats.date >= datetime.utcnow().date() - timedelta(days=days)
        ).order_by(DailyStats.date.asc()).all()
        
        return jsonify({
            'success': True,
            'period_days': days,
            'daily_stats': [stat.to_dict() for stat in daily_stats]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@hygiene_bp.route('/stats/user/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Get statistics for specific user"""
    try:
        days = int(request.args.get('days', 30))
        
        start_date = datetime.utcnow() - timedelta(days=days)
        events = HygieneEvent.query.filter(
            HygieneEvent.user_id == user_id,
            HygieneEvent.created_at >= start_date
        ).all()
        
        if not events:
            return jsonify({
                'success': True,
                'user_id': user_id,
                'total_events': 0,
                'compliance_rate': 0
            }), 200
        
        total = len(events)
        compliant = sum(1 for e in events if e.compliance)
        avg_duration = sum(e.duration for e in events) / total
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'period_days': days,
            'total_events': total,
            'compliant_events': compliant,
            'compliance_rate': round((compliant / total * 100), 2),
            'avg_duration': round(avg_duration, 1)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== USER ENDPOINTS ==========

@hygiene_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create new user
    
    Expected JSON:
    {
        "user_id": "USER123",
        "name": "Dr. John Doe",
        "department": "ICU",
        "role": "Doctor"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'name' not in data:
            return jsonify({'error': 'Missing required fields: user_id, name'}), 400
        
        # Check if user already exists
        if User.query.filter_by(user_id=data['user_id']).first():
            return jsonify({'error': 'User already exists'}), 400
        
        user = User(
            user_id=data['user_id'],
            name=data['name'],
            department=data.get('department'),
            role=data.get('role')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@hygiene_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details"""
    try:
        user = User.query.filter_by(user_id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== HEALTH CHECK ==========

@hygiene_bp.route('/health', methods=['GET'])
def health_check():
    """API health check"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500
