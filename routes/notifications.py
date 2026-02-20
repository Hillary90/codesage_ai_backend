from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.notification import Notification
from database import db

notification_bp = Blueprint('notifications', __name__)

@notification_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    current_user_id = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=current_user_id).order_by(Notification.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notifications]), 200

@notification_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    current_user_id = get_jwt_identity()
    count = Notification.query.filter_by(user_id=current_user_id, read=False).count()
    return jsonify({'count': count}), 200

@notification_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(notification_id):
    current_user_id = get_jwt_identity()
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user_id).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    notification.read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'}), 200

@notification_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    current_user_id = get_jwt_identity()
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user_id).first()
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    db.session.delete(notification)
    db.session.commit()
    return jsonify({'message': 'Notification deleted'}), 200

@notification_bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_read():
    current_user_id = get_jwt_identity()
    Notification.query.filter_by(user_id=current_user_id, read=False).update({'read': True})
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'}), 200
