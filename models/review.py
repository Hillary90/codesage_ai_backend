from app import db
from datetime import datetime

class CodeReview(db.Model):
    __tablename__ = 'code_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), nullable=False)
    quality_score = db.Column(db.Float, default=0)
    complexity_score = db.Column(db.Float, default=0)
    maintainability_index = db.Column(db.Float, default=0)
    issues_found = db.Column(db.Integer, default=0)
    review_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'language': self.language,
            'quality_score': self.quality_score,
            'complexity_score': self.complexity_score,
            'maintainability_index': self.maintainability_index,
            'issues_found': self.issues_found,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
