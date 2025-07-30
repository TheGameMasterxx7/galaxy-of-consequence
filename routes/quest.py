from flask import Blueprint, request, jsonify
from app import db
from models import QuestLog, FactionState
from services.galaxy_service import generate_procedural_quest
import json
import logging
from datetime import datetime

bp = Blueprint('quest', __name__)

@bp.route('/generate_quest', methods=['POST'])
def generate_quest():
    """Procedural quest logic based on state + morality"""
    try:
        data = request.get_json()
        user = data.get('user')
        
        if not user:
            return jsonify({'error': 'Missing user field'}), 400
        
        # Get current faction states to influence quest generation
        faction_states = FactionState.query.filter(
            (FactionState.user == user) | (FactionState.user == 'system')
        ).all()
        
        # Generate quest based on current game state
        quest_data = generate_procedural_quest(user, faction_states, data)
        
        # Create quest log entry
        quest = QuestLog(
            user=user,
            quest_title=quest_data['title'],
            quest_type=quest_data['type'],
            description=quest_data['description'],
            objectives=json.dumps(quest_data['objectives']),
            rewards=json.dumps(quest_data['rewards']),
            difficulty=quest_data['difficulty'],
            faction_involvement=json.dumps(quest_data['faction_involvement'])
        )
        
        db.session.add(quest)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'quest': quest.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error generating quest: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/get_active_quests', methods=['GET'])
def get_active_quests():
    """Get all active quests for a user"""
    try:
        user = request.args.get('user')
        
        if not user:
            return jsonify({'error': 'Missing user parameter'}), 400
        
        quests = QuestLog.query.filter_by(
            user=user,
            status='active'
        ).order_by(QuestLog.created_at.desc()).all()
        
        return jsonify({
            'status': 'success',
            'quests': [quest.to_dict() for quest in quests]
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving active quests: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/update_quest_status', methods=['POST'])
def update_quest_status():
    """Update quest progress or completion status"""
    try:
        data = request.get_json()
        quest_id = data.get('quest_id')
        new_status = data.get('status')
        
        if not quest_id or not new_status:
            return jsonify({'error': 'Missing quest_id or status'}), 400
        
        quest = QuestLog.query.get(quest_id)
        if not quest:
            return jsonify({'error': 'Quest not found'}), 404
        
        quest.status = new_status
        
        if new_status == 'completed':
            from datetime import datetime
            quest.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'quest': quest.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error updating quest status: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/get_quest_history', methods=['GET'])
def get_quest_history():
    """Get quest completion history"""
    try:
        user = request.args.get('user')
        
        if not user:
            return jsonify({'error': 'Missing user parameter'}), 400
        
        quests = QuestLog.query.filter_by(user=user)\
            .order_by(QuestLog.created_at.desc()).all()
        
        # Organize by status
        quest_history = {
            'active': [],
            'completed': [],
            'failed': [],
            'abandoned': []
        }
        
        for quest in quests:
            if quest.status in quest_history:
                quest_history[quest.status].append(quest.to_dict())
        
        return jsonify({
            'status': 'success',
            'history': quest_history
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving quest history: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/add_quest_objective', methods=['POST'])
def add_quest_objective():
    """Add a new objective to an existing quest"""
    try:
        data = request.get_json()
        quest_id = data.get('quest_id')
        objective = data.get('objective')
        
        if not quest_id or not objective:
            return jsonify({'error': 'Missing quest_id or objective'}), 400
        
        quest = QuestLog.query.get(quest_id)
        if not quest:
            return jsonify({'error': 'Quest not found'}), 404
        
        objectives = json.loads(quest.objectives) if quest.objectives else []
        from datetime import datetime
        objectives.append({
            'description': objective,
            'completed': False,
            'added_at': datetime.utcnow().isoformat() + 'Z'
        })
        
        quest.objectives = json.dumps(objectives)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'quest': quest.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error adding quest objective: {str(e)}")
        return jsonify({'error': 'Server error'}), 500
