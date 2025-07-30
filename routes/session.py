from flask import Blueprint, request, jsonify
from app import db
from models import SessionState
import json
import logging
from datetime import datetime

bp = Blueprint('session', __name__)

@bp.route('/get_session_state', methods=['GET'])
def get_session_state():
    """Get current session state"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Missing session_id parameter'}), 400
        
        session = SessionState.query.filter_by(session_id=session_id).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Update last active timestamp
        session.last_active = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving session state: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/update_session_state', methods=['POST'])
def update_session_state():
    """Update session state data"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Missing session_id'}), 400
        
        session = SessionState.query.filter_by(session_id=session_id).first()
        
        if not session:
            # Create new session
            session = SessionState(
                session_id=session_id,
                users=json.dumps(data.get('users', [])),
                current_location=data.get('current_location'),
                active_scene=data.get('active_scene'),
                session_data=json.dumps(data.get('session_data', {})),
                galaxy_momentum=data.get('galaxy_momentum', 0),
                force_events=json.dumps(data.get('force_events', []))
            )
            db.session.add(session)
        else:
            # Update existing session
            if 'users' in data:
                session.users = json.dumps(data['users'])
            if 'current_location' in data:
                session.current_location = data['current_location']
            if 'active_scene' in data:
                session.active_scene = data['active_scene']
            if 'session_data' in data:
                # Merge session data
                existing_data = json.loads(session.session_data) if session.session_data else {}
                existing_data.update(data['session_data'])
                session.session_data = json.dumps(existing_data)
            if 'galaxy_momentum' in data:
                session.galaxy_momentum = data['galaxy_momentum']
            if 'force_events' in data:
                existing_events = json.loads(session.force_events) if session.force_events else []
                existing_events.extend(data['force_events'])
                session.force_events = json.dumps(existing_events)
        
        session.last_active = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error updating session state: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/create_session', methods=['POST'])
def create_session():
    """Create a new multiplayer session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Missing session_id'}), 400
        
        # Check if session already exists
        existing_session = SessionState.query.filter_by(session_id=session_id).first()
        if existing_session:
            return jsonify({'error': 'Session already exists'}), 400
        
        session = SessionState(
            session_id=session_id,
            users=json.dumps(data.get('users', [])),
            current_location=data.get('current_location', 'Unknown'),
            active_scene=data.get('active_scene', 'Starting Scene'),
            session_data=json.dumps(data.get('session_data', {})),
            galaxy_momentum=0,
            force_events=json.dumps([])
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'session': session.to_dict()
        }), 201
        
    except Exception as e:
        logging.error(f"Error creating session: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/join_session', methods=['POST'])
def join_session():
    """Add a user to an existing session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user = data.get('user')
        
        if not session_id or not user:
            return jsonify({'error': 'Missing session_id or user'}), 400
        
        session = SessionState.query.filter_by(session_id=session_id).first()
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        users = json.loads(session.users) if session.users else []
        if user not in users:
            users.append(user)
            session.users = json.dumps(users)
            session.last_active = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error joining session: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/leave_session', methods=['POST'])
def leave_session():
    """Remove a user from a session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user = data.get('user')
        
        if not session_id or not user:
            return jsonify({'error': 'Missing session_id or user'}), 400
        
        session = SessionState.query.filter_by(session_id=session_id).first()
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        users = json.loads(session.users) if session.users else []
        if user in users:
            users.remove(user)
            session.users = json.dumps(users)
            session.last_active = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error leaving session: {str(e)}")
        return jsonify({'error': 'Server error'}), 500
