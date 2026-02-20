from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.portfolio import Portfolio
from services.ai_service import AIService
from services.github_service import GitHubService
from database import db

portfolio_bp = Blueprint('portfolio', __name__)
ai_service = AIService()
github_service = GitHubService()

@portfolio_bp.route('', methods=['POST'])
@jwt_required()
def create_portfolio_project():
    """Add a new project to portfolio"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Project name is required'}), 400
        
        # Generate AI description if not provided
        description = data.get('description')
        if not description and data.get('tech_stack'):
            description = ai_service.generate_portfolio_description(data)
        
        # Create portfolio project
        project = Portfolio(
            user_id=current_user_id,
            project_name=data['name'],
            description=description,
            tech_stack=data.get('tech_stack', []),
            github_url=data.get('github_url'),
            live_url=data.get('live_url'),
            image_url=data.get('image_url')
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project added to portfolio',
            'project': project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('', methods=['GET'])
@jwt_required()
def get_portfolio_projects():
    """Get all portfolio projects for current user"""
    try:
        current_user_id = get_jwt_identity()
        projects = Portfolio.query.filter_by(user_id=current_user_id)\
            .order_by(Portfolio.created_at.desc()).all()
        
        return jsonify({
            'projects': [project.to_dict() for project in projects]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_portfolio_project(project_id):
    """Get specific portfolio project"""
    try:
        current_user_id = get_jwt_identity()
        project = Portfolio.query.filter_by(id=project_id, user_id=current_user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify(project.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_portfolio_project(project_id):
    """Update portfolio project"""
    try:
        current_user_id = get_jwt_identity()
        project = Portfolio.query.filter_by(id=project_id, user_id=current_user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            project.project_name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'tech_stack' in data:
            project.tech_stack = data['tech_stack']
        if 'github_url' in data:
            project.github_url = data['github_url']
        if 'live_url' in data:
            project.live_url = data['live_url']
        if 'image_url' in data:
            project.image_url = data['image_url']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_portfolio_project(project_id):
    """Delete portfolio project"""
    try:
        current_user_id = get_jwt_identity()
        project = Portfolio.query.filter_by(id=project_id, user_id=current_user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'message': 'Project deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('/import-github', methods=['POST'])
@jwt_required()
def import_from_github():
    """Import projects from GitHub"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        github_username = data.get('github_username')
        if not github_username:
            return jsonify({'error': 'GitHub username is required'}), 400
        
        # Fetch repositories from GitHub
        repos = github_service.get_user_repositories(github_username)
        
        imported_count = 0
        for repo in repos[:10]:  # Limit to 10 repos
            # Check if already exists
            existing = Portfolio.query.filter_by(
                user_id=current_user_id,
                github_url=repo['html_url']
            ).first()
            
            if not existing:
                # Generate description
                project_data = {
                    'name': repo['name'],
                    'tech_stack': repo.get('language', 'Unknown'),
                    'features': repo.get('description', '')
                }
                description = ai_service.generate_portfolio_description(project_data)
                
                project = Portfolio(
                    user_id=current_user_id,
                    project_name=repo['name'],
                    description=description,
                    tech_stack=[repo.get('language')] if repo.get('language') else [],
                    github_url=repo['html_url'],
                    image_url=None
                )
                
                db.session.add(project)
                imported_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully imported {imported_count} projects',
            'imported_count': imported_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('/<int:project_id>/regenerate-description', methods=['POST'])
@jwt_required()
def regenerate_description(project_id):
    """Regenerate AI description for a project"""
    try:
        current_user_id = get_jwt_identity()
        project = Portfolio.query.filter_by(id=project_id, user_id=current_user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Try to fetch fresh data from GitHub if URL exists
        features = ''
        if project.github_url:
            try:
                repo_data = github_service.get_repository_details(project.github_url)
                features = repo_data.get('description', '')
            except:
                pass
        
        # Generate new description
        project_data = {
            'name': project.project_name,
            'tech_stack': project.tech_stack or [],
            'features': features
        }
        new_description = ai_service.generate_portfolio_description(project_data)
        
        project.description = new_description
        db.session.commit()
        
        return jsonify({
            'message': 'Description regenerated successfully',
            'project': project.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500