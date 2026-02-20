from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.review import CodeReview
from models.notification import Notification
from services.ai_service import AIService
from utils.code_analyzer import CodeAnalyzer
from database import db
from datetime import datetime

review_bp = Blueprint('review', __name__)
ai_service = AIService()
code_analyzer = CodeAnalyzer()

@review_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    """Submit code for AI review"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        if not data.get('code'):
            return jsonify({'error': 'Code is required'}), 400
        
        code = data['code']
        language = data.get('language', 'python')
        title = data.get('title', f'Code Review - {datetime.utcnow().strftime("%Y-%m-%d %H:%M")}')
        
        # Basic code analysis
        analysis = code_analyzer.analyze(code, language)
        
        # AI-powered review
        ai_feedback = ai_service.review_code(code, language)
        
        # Create review record
        review = CodeReview(
            user_id=current_user_id,
            title=title,
            code=code,
            language=language,
            ai_feedback=ai_feedback,
            quality_score=analysis.get('quality_score', 0),
            issues_found=analysis.get('issues_count', 0),
            complexity_score=analysis.get('complexity', 0)
        )
        
        db.session.add(review)
        db.session.commit()
        
        # Create notification
        notification = Notification(
            user_id=current_user_id,
            message=f'Code review for "{title}" completed successfully',
            type='review_complete',
            link='/code-review'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Code review completed',
            'review': review.to_dict(),
            'analysis': analysis,
            'ai_feedback': ai_feedback
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@review_bp.route('', methods=['GET'])
@jwt_required()
def get_reviews():
    """Get all reviews for current user"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        reviews = CodeReview.query.filter_by(user_id=current_user_id)\
            .order_by(CodeReview.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'reviews': [review.to_dict() for review in reviews.items],
            'total': reviews.total,
            'pages': reviews.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/<int:review_id>', methods=['GET'])
@jwt_required()
def get_review(review_id):
    """Get specific review by ID"""
    try:
        current_user_id = get_jwt_identity()
        review = CodeReview.query.filter_by(id=review_id, user_id=current_user_id).first()
        
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        
        return jsonify(review.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Delete a review"""
    try:
        current_user_id = get_jwt_identity()
        review = CodeReview.query.filter_by(id=review_id, user_id=current_user_id).first()
        
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({'message': 'Review deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@review_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get user's code review statistics"""
    try:
        current_user_id = get_jwt_identity()
        
        reviews = CodeReview.query.filter_by(user_id=current_user_id).all()
        
        if not reviews:
            return jsonify({
                'total_reviews': 0,
                'avg_quality_score': 0,
                'total_issues': 0,
                'languages': {}
            }), 200
        
        total_reviews = len(reviews)
        avg_score = sum(r.quality_score for r in reviews) / total_reviews
        total_issues = sum(r.issues_found for r in reviews)
        
        # Language distribution
        languages = {}
        for review in reviews:
            languages[review.language] = languages.get(review.language, 0) + 1
        
        return jsonify({
            'total_reviews': total_reviews,
            'avg_quality_score': round(avg_score, 2),
            'total_issues': total_issues,
            'languages': languages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500