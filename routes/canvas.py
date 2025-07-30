from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from models import CanvasEntry
from services.auth_service import validate_bearer_token
import json
import logging

bp = Blueprint('canvas', __name__)

@bp.route('/save_canvas', methods=['POST'])
@jwt_required(optional=True)
def save_canvas():
    """Save any RPG canvas type (Force HUD, Summary, etc.)"""
    try:
        # Validate bearer token
        if not validate_bearer_token(request):
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['canvas', 'user', 'data', 'meta']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new canvas entry
        canvas_entry = CanvasEntry(
            canvas=data['canvas'],
            user=data['user'],
            data=json.dumps(data['data']),
            meta=json.dumps(data['meta'])
        )
        
        db.session.add(canvas_entry)
        db.session.commit()
        
        logging.info(f"Canvas saved: {canvas_entry.id} for user {canvas_entry.user}")
        
        return jsonify({
            'status': 'success',
            'message': 'Canvas saved successfully',
            'id': canvas_entry.id
        }), 200
        
    except Exception as e:
        logging.error(f"Error saving canvas: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/get_canvas', methods=['GET'])
def get_canvas():
    """Retrieve the latest saved canvas"""
    try:
        # Get the most recent canvas entry
        canvas_entry = CanvasEntry.query.order_by(CanvasEntry.timestamp.desc()).first()
        
        if not canvas_entry:
            return jsonify({'error': 'No canvas found'}), 404
        
        return jsonify({
            'status': 'success',
            'canvas': canvas_entry.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving canvas: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/get_canvas_by_id', methods=['GET'])
def get_canvas_by_id():
    """Get a canvas by ID"""
    try:
        canvas_id = request.args.get('id')
        if not canvas_id:
            return jsonify({'error': 'Missing id parameter'}), 400
        
        canvas_entry = CanvasEntry.query.get(canvas_id)
        if not canvas_entry:
            return jsonify({'error': 'Canvas not found'}), 404
        
        return jsonify({
            'status': 'success',
            'canvas': canvas_entry.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving canvas by ID: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/get_log', methods=['GET'])
def get_log():
    """Get canvas history by type or user"""
    try:
        canvas_type = request.args.get('canvas')
        user = request.args.get('user')
        align = request.args.get('align')
        
        query = CanvasEntry.query
        
        if canvas_type:
            query = query.filter(CanvasEntry.canvas == canvas_type)
        
        if user:
            query = query.filter(CanvasEntry.user == user)
        
        # Apply alignment filter if provided (for Force-related canvases)
        if align:
            # This would filter based on meta data containing alignment info
            query = query.filter(CanvasEntry.meta.contains(f'"force_alignment":"{align}"'))
        
        entries = query.order_by(CanvasEntry.timestamp.desc()).all()
        
        return jsonify({
            'status': 'success',
            'log': [entry.to_dict() for entry in entries]
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving canvas log: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/get_canvas_history', methods=['GET'])
def get_canvas_history():
    """Retrieve full save history with filters"""
    try:
        user = request.args.get('user')
        campaign = request.args.get('campaign')
        canvas_type = request.args.get('canvas')
        
        query = CanvasEntry.query
        
        if user:
            query = query.filter(CanvasEntry.user == user)
        
        if campaign:
            query = query.filter(CanvasEntry.meta.contains(f'"campaign":"{campaign}"'))
        
        if canvas_type:
            query = query.filter(CanvasEntry.canvas == canvas_type)
        
        entries = query.order_by(CanvasEntry.timestamp.desc()).all()
        
        return jsonify({
            'status': 'success',
            'history': [entry.to_dict() for entry in entries]
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving canvas history: {str(e)}")
        return jsonify({'error': 'Server error'}), 500
