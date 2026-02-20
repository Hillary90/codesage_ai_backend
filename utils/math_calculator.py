from datetime import datetime, timedelta
from models.review import CodeReview
from models.portfolio import Portfolio

class MetricsCalculator:
    """
    Calculate various metrics for code reviews and portfolio
    """
    
    @staticmethod
    def calculate_user_metrics(user_id):
        """
        Calculate comprehensive user metrics
        """
        reviews = CodeReview.query.filter_by(user_id=user_id).all()
        portfolio_projects = Portfolio.query.filter_by(user_id=user_id).all()
        
        if not reviews:
            return {
                'total_reviews': 0,
                'avg_quality_score': 0,
                'total_issues': 0,
                'languages': {},
                'portfolio_projects': len(portfolio_projects),
                'improvement_trend': 'N/A'
            }
        
        # Basic stats
        total_reviews = len(reviews)
        avg_score = sum(r.quality_score for r in reviews) / total_reviews
        total_issues = sum(r.issues_found for r in reviews)
        
        # Language distribution
        languages = {}
        for review in reviews:
            languages[review.language] = languages.get(review.language, 0) + 1
        
        # Improvement trend (last 5 vs previous 5)
        sorted_reviews = sorted(reviews, key=lambda x: x.created_at)
        if len(sorted_reviews) >= 10:
            recent_avg = sum(r.quality_score for r in sorted_reviews[-5:]) / 5
            previous_avg = sum(r.quality_score for r in sorted_reviews[-10:-5]) / 5
            improvement = recent_avg - previous_avg
            trend = 'improving' if improvement > 5 else 'stable' if improvement > -5 else 'declining'
        else:
            trend = 'insufficient_data'
        
        return {
            'total_reviews': total_reviews,
            'avg_quality_score': round(avg_score, 2),
            'total_issues': total_issues,
            'languages': languages,
            'portfolio_projects': len(portfolio_projects),
            'improvement_trend': trend,
            'most_used_language': max(languages, key=languages.get) if languages else 'None'
        }
    
    @staticmethod
    def calculate_time_series(user_id, days=30):
        """
        Calculate time series data for charts
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        reviews = CodeReview.query.filter(
            CodeReview.user_id == user_id,
            CodeReview.created_at >= start_date
        ).order_by(CodeReview.created_at).all()
        
        # Group by date
        data_by_date = {}
        for review in reviews:
            date_key = review.created_at.strftime('%Y-%m-%d')
            if date_key not in data_by_date:
                data_by_date[date_key] = {
                    'count': 0,
                    'total_score': 0,
                    'issues': 0
                }
            
            data_by_date[date_key]['count'] += 1
            data_by_date[date_key]['total_score'] += review.quality_score
            data_by_date[date_key]['issues'] += review.issues_found
        
        # Format for charts
        dates = []
        scores = []
        review_counts = []
        
        for date_key in sorted(data_by_date.keys()):
            dates.append(date_key)
            data = data_by_date[date_key]
            scores.append(round(data['total_score'] / data['count'], 2))
            review_counts.append(data['count'])
        
        return {
            'dates': dates,
            'scores': scores,
            'review_counts': review_counts
        }
    
    @staticmethod
    def calculate_complexity_distribution(user_id):
        """
        Calculate distribution of code complexity
        """
        reviews = CodeReview.query.filter_by(user_id=user_id).all()
        
        distribution = {
            'low': 0,      # complexity < 5
            'medium': 0,   # complexity 5-10
            'high': 0,     # complexity 10-15
            'very_high': 0 # complexity > 15
        }
        
        for review in reviews:
            complexity = review.complexity_score
            if complexity < 5:
                distribution['low'] += 1
            elif complexity < 10:
                distribution['medium'] += 1
            elif complexity < 15:
                distribution['high'] += 1
            else:
                distribution['very_high'] += 1
        
        return distribution