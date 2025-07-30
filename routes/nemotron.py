from flask import Blueprint, request, jsonify, Response
from services.nvidia_service import query_nemotron_api
from models import NPCInteraction
from app import db
import json
import logging

bp = Blueprint('nemotron', __name__)

@bp.route('/query_nemotron', methods=['POST'])
def query_nemotron():
    """Generate immersive, lore-accurate NPC dialogue"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message field'}), 400
        
        user_message = data['message']
        
        # Extract context information if provided
        npc_context = data.get('npc_context', 'You are a helpful NPC in the Star Wars universe.')
        npc_name = data.get('npc_name', 'Unknown NPC')
        npc_type = data.get('npc_type', 'civilian')
        
        # Prepare the system message for immersive Star Wars dialogue
        system_message = f"""You are {npc_name}, a {npc_type} in the Star Wars galaxy. 
        Respond in character, maintaining immersive, lore-accurate dialogue. 
        Keep responses concise but engaging. Never break character or mention real-world concepts.
        
        Context: {npc_context}
        
        Guidelines:
        - Use appropriate Star Wars terminology and references
        - Maintain the character's personality and background
        - Respond naturally to the player's input
        - Keep responses between 1-3 sentences unless a longer response is clearly needed"""
        
        # Query NVIDIA Nemotron API
        response_data = query_nemotron_api(system_message, user_message)
        
        if not response_data:
            return jsonify({'error': 'Failed to get response from Nemotron'}), 500
        
        # Extract the NPC response
        npc_response = ""
        if 'choices' in response_data and len(response_data['choices']) > 0:
            npc_response = response_data['choices'][0]['message']['content']
        
        # Log the interaction for persistence
        try:
            interaction = NPCInteraction(
                user=data.get('user', 'anonymous'),
                npc_name=npc_name,
                npc_type=npc_type,
                interaction_context=npc_context,
                player_message=user_message,
                npc_response=npc_response,
                sentiment=data.get('sentiment', 'neutral'),
                memory_tier=data.get('memory_tier', 1)
            )
            db.session.add(interaction)
            db.session.commit()
        except Exception as e:
            logging.warning(f"Failed to log NPC interaction: {str(e)}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logging.error(f"Error in nemotron query: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/get_npc_history', methods=['GET'])
def get_npc_history():
    """Get conversation history with a specific NPC"""
    try:
        user = request.args.get('user')
        npc_name = request.args.get('npc_name')
        
        if not user or not npc_name:
            return jsonify({'error': 'Missing user or npc_name parameter'}), 400
        
        interactions = NPCInteraction.query.filter_by(
            user=user,
            npc_name=npc_name
        ).order_by(NPCInteraction.timestamp.desc()).limit(50).all()
        
        return jsonify({
            'status': 'success',
            'history': [interaction.to_dict() for interaction in interactions]
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving NPC history: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/get_all_npc_interactions', methods=['GET'])
def get_all_npc_interactions():
    """Get all NPC interactions for a user"""
    try:
        user = request.args.get('user')
        
        if not user:
            return jsonify({'error': 'Missing user parameter'}), 400
        
        interactions = NPCInteraction.query.filter_by(user=user)\
            .order_by(NPCInteraction.timestamp.desc()).limit(100).all()
        
        # Group by NPC for better organization
        npc_groups = {}
        for interaction in interactions:
            if interaction.npc_name not in npc_groups:
                npc_groups[interaction.npc_name] = []
            npc_groups[interaction.npc_name].append(interaction.to_dict())
        
        return jsonify({
            'status': 'success',
            'interactions': npc_groups
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving all NPC interactions: {str(e)}")
        return jsonify({'error': 'Server error'}), 500
