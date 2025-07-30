from flask import Blueprint, request, jsonify
from app import db
from models import PlayerCharacter, CanvasEntry
import json
import logging
from datetime import datetime

bp = Blueprint('force', __name__)

@bp.route('/update_alignment', methods=['POST'])
def update_alignment():
    """Update Force alignment based on player actions"""
    try:
        data = request.get_json()
        user = data.get('user')
        alignment_shift = data.get('alignment_shift', 0)  # Positive = Light, Negative = Dark
        action_description = data.get('action_description', '')
        
        if not user:
            return jsonify({'error': 'Missing user field'}), 400
        
        # Get or create player character
        character = PlayerCharacter.query.filter_by(user=user).first()
        
        if not character:
            return jsonify({'error': 'Character not found. Create character first.'}), 404
        
        # Parse current alignment or set default
        alignment_data = json.loads(character.faction_reputation) if character.faction_reputation else {}
        current_force_score = alignment_data.get('force_alignment_score', 0)
        
        # Apply alignment shift
        new_force_score = max(-100, min(100, current_force_score + alignment_shift))
        
        # Determine alignment category
        if new_force_score <= -30:
            alignment_category = 'Dark'
        elif new_force_score >= 30:
            alignment_category = 'Light'
        else:
            alignment_category = 'Gray'
        
        # Update character data
        character.force_alignment = alignment_category
        alignment_data['force_alignment_score'] = new_force_score
        alignment_data['last_alignment_change'] = datetime.utcnow().isoformat() + 'Z'
        alignment_data['last_action'] = action_description
        character.faction_reputation = json.dumps(alignment_data)
        character.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Generate Force consequences based on significant shifts
        force_consequences = []
        if abs(alignment_shift) >= 20:
            if alignment_shift > 0:
                force_consequences.append("The Force flows through you with renewed clarity.")
            else:
                force_consequences.append("You feel the dark side's influence growing stronger.")
        
        return jsonify({
            'status': 'success',
            'alignment': {
                'category': alignment_category,
                'score': new_force_score,
                'shift': alignment_shift,
                'consequences': force_consequences
            },
            'character': character.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error updating alignment: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/get_alignment', methods=['GET'])
def get_alignment():
    """Get current Force alignment for a user"""
    try:
        user = request.args.get('user')
        
        if not user:
            return jsonify({'error': 'Missing user parameter'}), 400
        
        character = PlayerCharacter.query.filter_by(user=user).first()
        
        if not character:
            return jsonify({'error': 'Character not found'}), 404
        
        # Parse alignment data
        alignment_data = json.loads(character.faction_reputation) if character.faction_reputation else {}
        force_score = alignment_data.get('force_alignment_score', 0)
        
        # Create alignment meter visualization
        meter_position = int((force_score + 100) / 200 * 20)  # Scale to 0-20 for visual meter
        meter_visual = ['|' if i < meter_position else '-' for i in range(20)]
        
        return jsonify({
            'status': 'success',
            'alignment': {
                'category': character.force_alignment,
                'score': force_score,
                'meter_visual': ''.join(meter_visual),
                'description': get_alignment_description(force_score),
                'last_change': alignment_data.get('last_alignment_change'),
                'last_action': alignment_data.get('last_action')
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error retrieving alignment: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@bp.route('/force_vision', methods=['POST'])
def force_vision():
    """Trigger Force vision based on current alignment and actions"""
    try:
        data = request.get_json()
        user = data.get('user')
        trigger_context = data.get('context', '')
        
        if not user:
            return jsonify({'error': 'Missing user field'}), 400
        
        character = PlayerCharacter.query.filter_by(user=user).first()
        
        if not character or character.force_sensitive != 'Yes':
            return jsonify({'error': 'Character is not Force sensitive'}), 400
        
        # Generate Force vision based on alignment and context
        alignment_data = json.loads(character.faction_reputation) if character.faction_reputation else {}
        force_score = alignment_data.get('force_alignment_score', 0)
        
        vision = generate_force_vision(character.force_alignment, force_score, trigger_context)
        
        # Save vision as a canvas entry for persistence
        vision_canvas = CanvasEntry(
            canvas='Force_Vision',
            user=user,
            data=json.dumps({
                'vision_text': vision['text'],
                'vision_type': vision['type'],
                'alignment_influence': character.force_alignment,
                'trigger_context': trigger_context
            }),
            meta=json.dumps({
                'campaign': 'Galaxy of Consequence',
                'version': '1.0.0',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'source': 'Force_Engine',
                'system_flags': {
                    'auto_save': True,
                    'force_event': True
                }
            })
        )
        
        db.session.add(vision_canvas)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'vision': vision,
            'canvas_id': vision_canvas.id
        }), 200
        
    except Exception as e:
        logging.error(f"Error generating Force vision: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

def get_alignment_description(force_score):
    """Get descriptive text for Force alignment score"""
    if force_score <= -80:
        return "Consumed by the dark side"
    elif force_score <= -60:
        return "Deeply touched by darkness"
    elif force_score <= -30:
        return "Leaning toward the dark side"
    elif force_score <= -10:
        return "Slightly influenced by darkness"
    elif force_score < 10:
        return "Balanced in the Force"
    elif force_score < 30:
        return "Touched by the light"
    elif force_score < 60:
        return "Strong in the light side"
    elif force_score < 80:
        return "A beacon of light"
    else:
        return "One with the light side"

def generate_force_vision(alignment, force_score, context):
    """Generate Force vision content based on alignment and context"""
    visions = {
        'Dark': [
            {
                'type': 'warning',
                'text': 'You see flashes of crimson lightning and hear the whisper of ancient Sith Lords calling your name...'
            },
            {
                'type': 'temptation',
                'text': 'In your vision, you see yourself wielding unlimited power, but the faces of those you care about fade into shadow...'
            },
            {
                'type': 'consequence',
                'text': 'The galaxy burns in your vision, and you realize your choices have led to this moment of darkness...'
            }
        ],
        'Light': [
            {
                'type': 'guidance',
                'text': 'A warm presence surrounds you, and you hear the gentle voice of a Jedi Master: "Trust in the Force, young one..."'
            },
            {
                'type': 'hope',
                'text': 'You see a vision of peace spreading across the galaxy, systems united not by fear, but by understanding...'
            },
            {
                'type': 'wisdom',
                'text': 'Ancient Jedi spirits appear before you, their lightsabers forming a circle of protection and guidance...'
            }
        ],
        'Gray': [
            {
                'type': 'balance',
                'text': 'You see two paths before you - one of light, one of shadow. Both lead to the same destination...'
            },
            {
                'type': 'choice',
                'text': 'In your vision, you stand at the center of a great conflict, neither Jedi nor Sith, but something else entirely...'
            },
            {
                'type': 'mystery',
                'text': 'The Force shows you fragments of possible futures, none clear, all dependent on choices yet to be made...'
            }
        ]
    }
    
    import random
    alignment_visions = visions.get(alignment, visions['Gray'])
    return random.choice(alignment_visions)
