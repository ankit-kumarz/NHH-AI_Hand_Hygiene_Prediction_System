"""
Advanced Analytics Module
Machine learning insights, trend analysis, and predictive analytics
"""

import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import func, text
from models.db import db, HygieneEvent, DailyStats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import json


class AdvancedAnalytics:
    """
    Advanced analytics engine for hand hygiene compliance
    Includes trend analysis, predictions, and insights
    """
    
    @staticmethod
    def get_compliance_trend(days=30):
        """
        Get compliance trend over time with linear regression prediction
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with trend data and prediction
        """
        start_date = datetime.utcnow().date() - timedelta(days=days)
        
        daily_stats = DailyStats.query.filter(
            DailyStats.date >= start_date
        ).order_by(DailyStats.date.asc()).all()
        
        if len(daily_stats) < 2:
            return {
                'trend': [],
                'prediction': None,
                'trend_direction': 'insufficient_data'
            }
        
        # Prepare data
        dates = np.arange(len(daily_stats)).reshape(-1, 1)
        rates = np.array([d.compliance_rate for d in daily_stats]).reshape(-1, 1)
        
        # Fit linear regression
        model = LinearRegression()
        model.fit(dates, rates)
        
        # Calculate trend direction
        slope = model.coef_[0][0]
        trend_direction = 'improving' if slope > 0 else 'declining'
        
        # Predict next 7 days
        future_dates = np.arange(len(daily_stats), len(daily_stats) + 7).reshape(-1, 1)
        predictions = model.predict(future_dates)
        
        return {
            'historical': [
                {
                    'date': d.date.isoformat(),
                    'rate': d.compliance_rate
                } for d in daily_stats
            ],
            'predictions': [
                {
                    'date': (datetime.utcnow().date() + timedelta(days=i+1)).isoformat(),
                    'predicted_rate': float(np.clip(predictions[i][0], 0, 100))
                } for i in range(7)
            ],
            'slope': float(slope),
            'trend_direction': trend_direction,
            'r_squared': float(model.score(dates, rates))
        }
    
    @staticmethod
    def get_department_performance(days=30):
        """
        Get performance metrics by department
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with department stats
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query by department
        dept_stats = db.session.query(
            HygieneEvent.department,
            func.count(HygieneEvent.id).label('total'),
            func.sum(func.cast(HygieneEvent.compliance, db.Integer)).label('compliant'),
            func.avg(HygieneEvent.duration).label('avg_duration')
        ).filter(
            HygieneEvent.created_at >= start_date,
            HygieneEvent.department.isnot(None)
        ).group_by(HygieneEvent.department).all()
        
        results = []
        for dept, total, compliant, avg_dur in dept_stats:
            compliance_rate = (compliant / total * 100) if total > 0 else 0
            results.append({
                'department': dept,
                'total_events': total,
                'compliant_events': compliant or 0,
                'compliance_rate': round(compliance_rate, 2),
                'avg_duration': round(avg_dur or 0, 1),
                'rank': 0  # Will be assigned after sorting
            })
        
        # Sort by compliance rate and assign ranks
        results.sort(key=lambda x: x['compliance_rate'], reverse=True)
        for i, result in enumerate(results):
            result['rank'] = i + 1
        
        return {
            'period_days': days,
            'departments': results,
            'best_performer': results[0] if results else None,
            'worst_performer': results[-1] if results else None
        }
    
    @staticmethod
    def get_user_leaderboard(days=30, limit=10):
        """
        Get top performing users (leaderboard)
        
        Args:
            days: Number of days to analyze
            limit: Number of users to return
            
        Returns:
            List of top users with scores
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        user_stats = db.session.query(
            HygieneEvent.user_id,
            func.count(HygieneEvent.id).label('total'),
            func.sum(func.cast(HygieneEvent.compliance, db.Integer)).label('compliant'),
            func.avg(HygieneEvent.duration).label('avg_duration')
        ).filter(
            HygieneEvent.created_at >= start_date,
            HygieneEvent.user_id.isnot(None)
        ).group_by(HygieneEvent.user_id).all()
        
        results = []
        for user_id, total, compliant, avg_dur in user_stats:
            if total > 0:  # Only include users with events
                compliance_rate = (compliant / total * 100) if total > 0 else 0
                
                # Calculate score (weighted)
                score = (compliance_rate * 0.7) + (min(avg_dur / 20, 1.0) * 0.3 * 100)
                
                results.append({
                    'user_id': user_id,
                    'total_events': total,
                    'compliant_events': compliant or 0,
                    'compliance_rate': round(compliance_rate, 2),
                    'avg_duration': round(avg_dur or 0, 1),
                    'score': round(score, 2),
                    'rank': 0
                })
        
        # Sort by score and assign ranks
        results.sort(key=lambda x: x['score'], reverse=True)
        for i, result in enumerate(results):
            result['rank'] = i + 1
        
        return {
            'period_days': days,
            'leaderboard': results[:limit],
            'total_participants': len(results)
        }
    
    @staticmethod
    def get_peak_hours(days=7):
        """
        Identify peak handwashing hours
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with hourly breakdown
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query events by hour
        hourly_data = db.session.query(
            func.extract('hour', HygieneEvent.created_at).label('hour'),
            func.count(HygieneEvent.id).label('count'),
            func.avg(HygieneEvent.duration).label('avg_duration'),
            func.sum(func.cast(HygieneEvent.compliance, db.Integer)).label('compliant')
        ).filter(
            HygieneEvent.created_at >= start_date
        ).group_by(
            func.extract('hour', HygieneEvent.created_at)
        ).all()
        
        hours = []
        for hour, count, avg_dur, compliant in hourly_data:
            if hour is not None:
                compliance_rate = (compliant / count * 100) if count > 0 else 0
                hours.append({
                    'hour': int(hour),
                    'events': count,
                    'compliance_rate': round(compliance_rate, 2),
                    'avg_duration': round(avg_dur or 0, 1)
                })
        
        # Sort by hour
        hours.sort(key=lambda x: x['hour'])
        
        return {
            'period_days': days,
            'hourly_breakdown': hours,
            'peak_hour': max(hours, key=lambda x: x['events']) if hours else None
        }
    
    @staticmethod
    def get_anomalies(days=30, threshold=2.0):
        """
        Detect anomalies in compliance data (unusually low/high values)
        
        Args:
            days: Number of days to analyze
            threshold: Standard deviations from mean (default: 2.0)
            
        Returns:
            List of anomalies
        """
        start_date = datetime.utcnow().date() - timedelta(days=days)
        
        daily_stats = DailyStats.query.filter(
            DailyStats.date >= start_date
        ).all()
        
        if len(daily_stats) < 3:
            return {'anomalies': [], 'status': 'insufficient_data'}
        
        # Calculate statistics
        rates = [d.compliance_rate for d in daily_stats]
        mean = np.mean(rates)
        std = np.std(rates)
        
        anomalies = []
        for stat in daily_stats:
            z_score = abs((stat.compliance_rate - mean) / std) if std > 0 else 0
            
            if z_score > threshold:
                anomalies.append({
                    'date': stat.date.isoformat(),
                    'compliance_rate': stat.compliance_rate,
                    'z_score': round(z_score, 2),
                    'type': 'low' if stat.compliance_rate < mean else 'high'
                })
        
        return {
            'anomalies': sorted(anomalies, key=lambda x: x['z_score'], reverse=True),
            'mean': round(mean, 2),
            'std': round(std, 2),
            'threshold': threshold
        }
    
    @staticmethod
    def get_insights(days=30):
        """
        Generate actionable insights from data
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of insights
        """
        insights = []
        
        # Get trend
        trend = AdvancedAnalytics.get_compliance_trend(days)
        if trend['trend_direction'] == 'improving':
            insights.append({
                'type': 'positive',
                'title': '📈 Compliance Improving',
                'description': f"Compliance rate is trending upward with slope {trend['slope']:.2f}%/day"
            })
        elif trend['trend_direction'] == 'declining':
            insights.append({
                'type': 'warning',
                'title': '📉 Compliance Declining',
                'description': f"Compliance rate is trending downward. Intervention needed!"
            })
        
        # Get department performance
        dept_perf = AdvancedAnalytics.get_department_performance(days)
        if dept_perf['best_performer']:
            best = dept_perf['best_performer']
            insights.append({
                'type': 'info',
                'title': '🏆 Best Department',
                'description': f"{best['department']} leads with {best['compliance_rate']}% compliance"
            })
        
        # Get anomalies
        anomalies = AdvancedAnalytics.get_anomalies(days)
        if anomalies['anomalies']:
            insights.append({
                'type': 'warning',
                'title': '🚨 Anomalies Detected',
                'description': f"Unusual compliance patterns detected on {len(anomalies['anomalies'])} days"
            })
        
        # Peak hours insight
        peak = AdvancedAnalytics.get_peak_hours(days)
        if peak['peak_hour']:
            insights.append({
                'type': 'info',
                'title': '⏰ Peak Activity',
                'description': f"Peak handwashing at {int(peak['peak_hour']['hour'])}:00 with {peak['peak_hour']['events']} events"
            })
        
        return insights


if __name__ == "__main__":
    print("Advanced Analytics module loaded")
