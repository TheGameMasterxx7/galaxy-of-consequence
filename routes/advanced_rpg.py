"""
Advanced RPG Mechanics Routes
Real-time faction AI, procedural quests, multiplayer sessions, and Force morality
"""
from flask import Blueprint, request, jsonify
from app import db
import json
import logging
from datetime import datetime

# Import our advanced RPG services
from services.faction_ai_service import faction_ai
from services.quest_engine import quest_engine
from services.session_manager import session_manager
from services.force_morality_engine import force_engine

bp = Blueprint('advanced_rpg', __name__)

@bp.route('/faction_ai_turn', methods=['POST'])
def process_faction_ai_turn():
    """Process real-time faction AI turn with intelligent responses"""
    try:
        data = request.get_json()
        if not data or 'faction' not in data:
            return jsonify({'error': 'Missing faction parameter'}), 400
        
        faction_name = data['faction']
        galaxy_events = data.get('galaxy_events', [])
        
        # Get current faction state from database
        from models import FactionState
        faction_state = FactionState.query.filter_by(faction_name=faction_name).first()
        if not faction_state:
            return jsonify({'error': f'Faction {faction_name} not found'}), 404
        
        current_state = faction_state.to_dict()
        
        # Process AI turn
        turn_result = faction_ai.process_faction_turn(faction_name, current_state, galaxy_events)
        
        # Update faction state in database
        faction_state.reputation += turn_result.get('resource_changes', {}).get('reputation', 0)
        faction_state.resources += turn_result.get('resource_changes', {}).get('resources', 0)
        faction_state.awareness = min(100, faction_state.awareness + turn_result.get('resource_changes', {}).get('awareness', 0))
        faction_state.last_interaction = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'faction_turn': turn_result,
            'updated_state': faction_state.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error in faction AI turn: {str(e)}")
        return jsonify({'error': 'Server error processing faction turn'}), 500

@bp.route('/generate_adaptive_quest', methods=['POST'])
def generate_adaptive_quest():
    """Generate procedural quest that adapts to current galaxy state"""
    try:
        data = request.get_json()
        if not data or 'user' not in data:
            return jsonify({'error': 'Missing user parameter'}), 400
        
        user = data['user']
        
        # Get current faction states
        from models import FactionState, QuestLog
        faction_states = {}
        factions = FactionState.query.all()
        for faction in factions:
            faction_states[faction.faction_name] = faction.to_dict()
        
        # Get player quest history
        player_history = QuestLog.query.filter_by(user=user).order_by(QuestLog.created_at.desc()).limit(20).all()
        quest_history = [quest.to_dict() for quest in player_history]
        
        # Get Force alignment if available
        force_alignment = data.get('force_alignment', {'light': 0, 'dark': 0, 'balance': 100})
        
        # Generate adaptive quest
        quest_data = quest_engine.generate_adaptive_quest(user, faction_states, quest_history, force_alignment)
        
        # Save quest to database
        new_quest = QuestLog(
            user=user,
            quest_title=quest_data['quest_title'],
            quest_type=quest_data['quest_type'],
            description=quest_data['description'],
            objectives=json.dumps(quest_data['objectives']),
            rewards=json.dumps(quest_data['rewards']),
            status='active',
            difficulty=quest_data['difficulty'],
            faction_involvement=json.dumps(quest_data['faction_involvement'])
        )
        
        db.session.add(new_quest)
        db.session.commit()
        
        # Add quest ID to response
        quest_data['id'] = new_quest.id
        
        return jsonify({
            'status': 'success',
            'quest': quest_data
        }), 200
        
    except Exception as e:
        logging.error(f"Error generating adaptive quest: {str(e)}")
        return jsonify({'error': 'Server error generating quest'}), 500

@bp.route('/create_multiplayer_session', methods=['POST'])
def create_multiplayer_session():
    """Create new multiplayer session with persistent world state"""
    try:
        data = request.get_json()
        if not data or 'session_id' not in data or 'session_master' not in data:
            return jsonify({'error': 'Missing session_id or session_master'}), 400
        
        session_id = data['session_id']
        session_master = data['session_master']
        initial_config = data.get('config', {})
        
        # Create session world state
        world_state = session_manager.create_session(session_id, session_master, initial_config)
        
        # Save session to database
        from models import SessionState
        session_record = SessionState(
            session_id=session_id,
            users=json.dumps([session_master]),
            current_location=initial_config.get('starting_location', 'Coruscant'),
            active_scene=initial_config.get('starting_scene', 'Campaign Beginning'),
            session_data=json.dumps(world_state.__dict__),
            galaxy_momentum=0
        )
        
        db.session.add(session_record)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'session_state': world_state.__dict__,
            'message': f'Multiplayer session {session_id} created successfully'
        }), 200
        
    except Exception as e:
        logging.error(f"Error creating multiplayer session: {str(e)}")
        return jsonify({'error': 'Server error creating session'}), 500

@bp.route('/join_session', methods=['POST'])
def join_session():
    """Join existing multiplayer session"""
    try:
        data = request.get_json()
        if not data or 'session_id' not in data or 'player_id' not in data:
            return jsonify({'error': 'Missing session_id or player_id'}), 400
        
        session_id = data['session_id']
        player_id = data['player_id']
        character_data = data.get('character_data', {})
        
        # Join session through session manager
        player_state = session_manager.join_session(session_id, player_id, character_data)
        
        # Update database session record
        from models import SessionState
        session_record = SessionState.query.filter_by(session_id=session_id).first()
        if session_record:
            current_users = json.loads(session_record.users) if session_record.users else []
            if player_id not in current_users:
                current_users.append(player_id)
                session_record.users = json.dumps(current_users)
                session_record.last_active = datetime.utcnow()
                db.session.commit()
        
        return jsonify({
            'status': 'success',
            'player_state': player_state.__dict__,
            'session_info': session_manager.sync_session_state(session_id)
        }), 200
        
    except Exception as e:
        logging.error(f"Error joining session: {str(e)}")
        return jsonify({'error': str(e)}), 400

@bp.route('/process_moral_choice', methods=['POST'])
def process_moral_choice():
    """Process Force morality choice with narrative consequences"""
    try:
        data = request.get_json()
        if not data or 'user' not in data or 'choice' not in data:
            return jsonify({'error': 'Missing user or choice parameters'}), 400
        
        user_id = data['user']
        selected_choice = data['choice']  # 'light', 'dark', or 'balance'
        choice_context = data.get('context', {})
        
        # Process moral choice through Force engine
        moral_result = force_engine.process_moral_choice(user_id, choice_context, selected_choice)
        
        # Update player character Force alignment if exists
        from models import PlayerCharacter
        character = PlayerCharacter.query.filter_by(user=user_id).first()
        if character:
            character.force_alignment = moral_result['new_alignment']
            character.updated_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'moral_result': moral_result,
            'message': 'Force alignment and destiny threads updated'
        }), 200
        
    except Exception as e:
        logging.error(f"Error processing moral choice: {str(e)}")
        return jsonify({'error': 'Server error processing moral choice'}), 500

@bp.route('/generate_force_vision', methods=['POST'])
def generate_force_vision():
    """Generate AI-powered Force vision based on moral trajectory"""
    try:
        data = request.get_json()
        if not data or 'user' not in data:
            return jsonify({'error': 'Missing user parameter'}), 400
        
        user_id = data['user']
        vision_context = data.get('context', {})
        
        # Generate Force vision
        vision_result = force_engine.generate_force_vision(user_id, vision_context)
        
        if 'error' in vision_result:
            return jsonify(vision_result), 400
        
        return jsonify({
            'status': 'success',
            'force_vision': vision_result
        }), 200
        
    except Exception as e:
        logging.error(f"Error generating Force vision: {str(e)}")
        return jsonify({'error': 'Server error generating vision'}), 500

@bp.route('/sync_session_state', methods=['GET'])
def sync_session_state():
    """Get complete session state for all connected players"""
    try:
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({'error': 'Missing session_id parameter'}), 400
        
        # Get synchronized session state
        session_state = session_manager.sync_session_state(session_id)
        
        return jsonify({
            'status': 'success',
            'session_sync': session_state
        }), 200
        
    except Exception as e:
        logging.error(f"Error syncing session state: {str(e)}")
        return jsonify({'error': str(e)}), 400

@bp.route('/advance_session_time', methods=['POST'])
def advance_session_time():
    """Advance session time and process background world changes"""
    try:
        data = request.get_json()
        if not data or 'session_id' not in data:
            return jsonify({'error': 'Missing session_id parameter'}), 400
        
        session_id = data['session_id']
        time_increment = data.get('time_increment', '1 day')
        
        # Advance session time
        time_result = session_manager.advance_session_time(session_id, time_increment)
        
        return jsonify({
            'status': 'success',
            'time_advancement': time_result
        }), 200
        
    except Exception as e:
        logging.error(f"Error advancing session time: {str(e)}")
        return jsonify({'error': str(e)}), 400

@bp.route('/calculate_force_corruption', methods=['POST'])
def calculate_force_corruption():
    """Calculate and track Force corruption effects"""
    try:
        data = request.get_json()
        if not data or 'user' not in data:
            return jsonify({'error': 'Missing user parameter'}), 400
        
        user_id = data['user']
        
        # Calculate corruption effects
        corruption_result = force_engine.calculate_force_corruption(user_id)
        
        if 'error' in corruption_result:
            return jsonify(corruption_result), 400
        
        return jsonify({
            'status': 'success',
            'corruption_analysis': corruption_result
        }), 200
        
    except Exception as e:
        logging.error(f"Error calculating Force corruption: {str(e)}")
        return jsonify({'error': 'Server error calculating corruption'}), 500