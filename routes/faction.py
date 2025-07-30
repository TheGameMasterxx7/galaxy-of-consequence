from flask import Blueprint, request, jsonify
from app import db
from models import FactionState
from services.galaxy_service import update_faction_ai, calculate_faction_response
import json
import logging

bp = Blueprint('faction', __name__)

@bp.route('/faction_tick', methods=['POST'])
def faction_tick():
    """Real-time, persistent faction simulation"""
    try:
        data = request.get_json()
        user = data.get('user', 'anonymous')
        action = data.get('action', 'passive_tick')
        target_faction = data.get('faction')
        
        # Get all factions for this user (or system factions)
        factions = FactionState.query.filter(
            (FactionState.user == user) | (FactionState.user == 'system')
        ).all()
        
        faction_updates = []
        
        for faction in factions:
            # Calculate faction AI response based on player actions
            old_state = faction.to_dict()
            
            # Update faction based on action and current state
            updated_faction = update_faction_ai(faction, action, target_faction)
            
            if updated_faction:
                db.session.commit()
                faction_updates.append({
                    'faction': updated_faction.faction_name,
                    'old_state': old_state,
                    'new_state': updated_faction.to_dict(),
                    'changes': calculate_faction_response(old_state, updated_faction.to_dict())
                })
        
        return jsonify({
            'status': 'success',
            'faction_updates': faction_updates,
            'galaxy_momentum': sum(f['new_state']['awareness'] for f in faction_updates)
        }), 200
        
    except Exception as e:
        logging.error(f"Error in faction tick: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/get_faction_state', methods=['GET'])
def get_faction_state():
    """Get current state of all factions"""
    try:
        user = request.args.get('user', 'anonymous')
        faction_name = request.args.get('faction')
        
        query = FactionState.query.filter(
            (FactionState.user == user) | (FactionState.user == 'system')
        )
        
        if faction_name:
            query = query.filter(FactionState.faction_name == faction_name)
        
        factions = query.all()
        
        return jsonify({
            'status': 'success',
            'factions': [faction.to_dict() for faction in factions]
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving faction state: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/update_faction_reputation', methods=['POST'])
def update_faction_reputation():
    """Update reputation with a specific faction"""
    try:
        data = request.get_json()
        user = data.get('user')
        faction_name = data.get('faction_name')
        reputation_change = data.get('reputation_change', 0)
        awareness_change = data.get('awareness_change', 0)
        
        if not user or not faction_name:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find or create faction state for user
        faction = FactionState.query.filter_by(
            faction_name=faction_name,
            user=user
        ).first()
        
        if not faction:
            # Create new faction state based on system defaults
            system_faction = FactionState.query.filter_by(
                faction_name=faction_name,
                user='system'
            ).first()
            
            if system_faction:
                faction = FactionState(
                    faction_name=faction_name,
                    user=user,
                    reputation=reputation_change,
                    awareness=awareness_change,
                    resources=system_faction.resources,
                    goals=system_faction.goals,
                    active_operations=system_faction.active_operations
                )
                db.session.add(faction)
            else:
                return jsonify({'error': 'Unknown faction'}), 404
        else:
            faction.reputation += reputation_change
            faction.awareness += awareness_change
        
        # Clamp values to reasonable ranges
        faction.reputation = max(-100, min(100, faction.reputation))
        faction.awareness = max(0, min(100, faction.awareness))
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'faction': faction.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error updating faction reputation: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/get_faction_relationships', methods=['GET'])
def get_faction_relationships():
    """Get relationship matrix between factions"""
    try:
        user = request.args.get('user', 'anonymous')
        
        factions = FactionState.query.filter(
            (FactionState.user == user) | (FactionState.user == 'system')
        ).all()
        
        # Create relationship matrix
        relationships = {}
        for faction in factions:
            relationships[faction.faction_name] = {
                'reputation': faction.reputation,
                'awareness': faction.awareness,
                'threat_level': 'Low' if faction.awareness < 30 else 'Medium' if faction.awareness < 70 else 'High',
                'relationship_status': 'Hostile' if faction.reputation < -50 else 
                                    'Unfriendly' if faction.reputation < -10 else
                                    'Neutral' if faction.reputation < 10 else
                                    'Friendly' if faction.reputation < 50 else 'Allied'
            }
        
        return jsonify({
            'status': 'success',
            'relationships': relationships
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving faction relationships: {str(e)}")
        return jsonify({'error': 'Server error'}), 500
