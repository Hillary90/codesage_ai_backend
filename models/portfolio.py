from database import db
from datetime import datetime

class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tech_stack = db.Column(db.JSON, nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    live_url = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_name': self.project_name,
            'description': self.description,
            'tech_stack': self.tech_stack,
            'github_url': self.github_url,
            'live_url': self.live_url,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
