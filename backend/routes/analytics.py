"""
Analytics Routes - Advanced reporting endpoints
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from analytics.advanced import AdvancedAnalytics
import csv
import io

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


@analytics_bp.route('/trend', methods=['GET'])
def get_trend():
    """Get compliance trend with predictions"""
    try:
        days = int(request.args.get('days', 30))
        trend = AdvancedAnalytics.get_compliance_trend(days)
        
        return jsonify({
            'success': True,
            'data': trend
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/departments', methods=['GET'])
def get_departments():
    """Get department performance metrics"""
    try:
        days = int(request.args.get('days', 30))
        dept_perf = AdvancedAnalytics.get_department_performance(days)
        
        return jsonify({
            'success': True,
            'data': dept_perf
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get user leaderboard"""
    try:
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 10))
        leaderboard = AdvancedAnalytics.get_user_leaderboard(days, limit)
        
        return jsonify({
            'success': True,
            'data': leaderboard
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/peak-hours', methods=['GET'])
def get_peak_hours():
    """Get peak handwashing hours"""
    try:
        days = int(request.args.get('days', 7))
        peak = AdvancedAnalytics.get_peak_hours(days)
        
        return jsonify({
            'success': True,
            'data': peak
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/anomalies', methods=['GET'])
def get_anomalies():
    """Detect anomalies in compliance data"""
    try:
        days = int(request.args.get('days', 30))
        threshold = float(request.args.get('threshold', 2.0))
        anomalies = AdvancedAnalytics.get_anomalies(days, threshold)
        
        return jsonify({
            'success': True,
            'data': anomalies
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/insights', methods=['GET'])
def get_insights():
    """Get actionable insights"""
    try:
        days = int(request.args.get('days', 30))
        insights = AdvancedAnalytics.get_insights(days)
        
        return jsonify({
            'success': True,
            'insights': insights,
            'total_insights': len(insights)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/export/csv', methods=['GET'])
def export_csv():
    """Export analytics data as CSV"""
    try:
        days = int(request.args.get('days', 30))
        
        # Get data
        dept_perf = AdvancedAnalytics.get_department_performance(days)
        leaderboard = AdvancedAnalytics.get_user_leaderboard(days, 100)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Department section
        writer.writerow(['Department Performance Report'])
        writer.writerow([])
        writer.writerow(['Department', 'Total Events', 'Compliant Events', 'Compliance Rate (%)', 'Avg Duration (s)', 'Rank'])
        
        for dept in dept_perf['departments']:
            writer.writerow([
                dept['department'],
                dept['total_events'],
                dept['compliant_events'],
                dept['compliance_rate'],
                dept['avg_duration'],
                dept['rank']
            ])
        
        # User leaderboard section
        writer.writerow([])
        writer.writerow(['User Leaderboard'])
        writer.writerow([])
        writer.writerow(['Rank', 'User ID', 'Total Events', 'Compliant Events', 'Compliance Rate (%)', 'Avg Duration (s)', 'Score'])
        
        for user in leaderboard['leaderboard']:
            writer.writerow([
                user['rank'],
                user['user_id'],
                user['total_events'],
                user['compliant_events'],
                user['compliance_rate'],
                user['avg_duration'],
                user['score']
            ])
        
        # Create response
        output.seek(0)
        response = io.BytesIO()
        response.write(output.getvalue().encode())
        response.seek(0)
        
        return send_file(
            response,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'hand_hygiene_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get all analytics for dashboard"""
    try:
        days = int(request.args.get('days', 30))
        
        return jsonify({
            'success': True,
            'period_days': days,
            'trend': AdvancedAnalytics.get_compliance_trend(days),
            'departments': AdvancedAnalytics.get_department_performance(days),
            'leaderboard': AdvancedAnalytics.get_user_leaderboard(days, 5),
            'peak_hours': AdvancedAnalytics.get_peak_hours(7),
            'anomalies': AdvancedAnalytics.get_anomalies(days),
            'insights': AdvancedAnalytics.get_insights(days),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
