from app import db
from datetime import datetime
import json
import uuid

class CanvasEntry(db.Model):
    __tablename__ = 'canvas_entries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    canvas = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Text, nullable=False)  # JSON string
    meta = db.Column(db.Text, nullable=False)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'canvas': self.canvas,
            'user': self.user,
            'data': json.loads(self.data),
            'meta': json.loads(self.meta),
            'timestamp': self.timestamp.isoformat() + 'Z'
        }

class PlayerCharacter(db.Model):
    __tablename__ = 'player_characters'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50))
    homeworld = db.Column(db.String(50))
    background = db.Column(db.String(100))
    allegiance = db.Column(db.String(50))
    force_sensitive = db.Column(db.String(20))
    force_alignment = db.Column(db.String(20))
    appearance = db.Column(db.Text)
    equipment = db.Column(db.Text)  # JSON string
    skills = db.Column(db.Text)  # JSON string
    personal_goal = db.Column(db.Text)
    contacts = db.Column(db.Text)
    faction_reputation = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'name': self.name,
            'species': self.species,
            'homeworld': self.homeworld,
            'background': self.background,
            'allegiance': self.allegiance,
            'force_sensitive': self.force_sensitive,
            'force_alignment': self.force_alignment,
            'appearance': self.appearance,
            'equipment': json.loads(self.equipment) if self.equipment else {},
            'skills': json.loads(self.skills) if self.skills else [],
            'personal_goal': self.personal_goal,
            'contacts': self.contacts,
            'faction_reputation': json.loads(self.faction_reputation) if self.faction_reputation else {},
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z'
        }

class FactionState(db.Model):
    __tablename__ = 'faction_states'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    faction_name = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    reputation = db.Column(db.Integer, default=0)
    awareness = db.Column(db.Integer, default=0)
    resources = db.Column(db.Integer, default=100)
    goals = db.Column(db.Text)  # JSON string
    active_operations = db.Column(db.Text)  # JSON string
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'faction_name': self.faction_name,
            'user': self.user,
            'reputation': self.reputation,
            'awareness': self.awareness,
            'resources': self.resources,
            'goals': json.loads(self.goals) if self.goals else [],
            'active_operations': json.loads(self.active_operations) if self.active_operations else [],
            'last_interaction': self.last_interaction.isoformat() + 'Z'
        }

class QuestLog(db.Model):
    __tablename__ = 'quest_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = db.Column(db.String(100), nullable=False)
    quest_title = db.Column(db.String(200), nullable=False)
    quest_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    objectives = db.Column(db.Text)  # JSON string
    rewards = db.Column(db.Text)  # JSON string
    status = db.Column(db.String(20), default='active')
    difficulty = db.Column(db.String(20))
    faction_involvement = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'quest_title': self.quest_title,
            'quest_type': self.quest_type,
            'description': self.description,
            'objectives': json.loads(self.objectives) if self.objectives else [],
            'rewards': json.loads(self.rewards) if self.rewards else [],
            'status': self.status,
            'difficulty': self.difficulty,
            'faction_involvement': json.loads(self.faction_involvement) if self.faction_involvement else [],
            'created_at': self.created_at.isoformat() + 'Z',
            'completed_at': self.completed_at.isoformat() + 'Z' if self.completed_at else None
        }

class SessionState(db.Model):
    __tablename__ = 'session_states'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(100), nullable=False, unique=True)
    users = db.Column(db.Text)  # JSON string
    current_location = db.Column(db.String(100))
    active_scene = db.Column(db.String(100))
    session_data = db.Column(db.Text)  # JSON string
    galaxy_momentum = db.Column(db.Integer, default=0)
    force_events = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'users': json.loads(self.users) if self.users else [],
            'current_location': self.current_location,
            'active_scene': self.active_scene,
            'session_data': json.loads(self.session_data) if self.session_data else {},
            'galaxy_momentum': self.galaxy_momentum,
            'force_events': json.loads(self.force_events) if self.force_events else [],
            'created_at': self.created_at.isoformat() + 'Z',
            'last_active': self.last_active.isoformat() + 'Z'
        }

class NPCInteraction(db.Model):
    __tablename__ = 'npc_interactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = db.Column(db.String(100), nullable=False)
    npc_name = db.Column(db.String(100), nullable=False)
    npc_type = db.Column(db.String(50))
    interaction_context = db.Column(db.Text)
    player_message = db.Column(db.Text)
    npc_response = db.Column(db.Text)
    sentiment = db.Column(db.String(20))
    memory_tier = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'npc_name': self.npc_name,
            'npc_type': self.npc_type,
            'interaction_context': self.interaction_context,
            'player_message': self.player_message,
            'npc_response': self.npc_response,
            'sentiment': self.sentiment,
            'memory_tier': self.memory_tier,
            'timestamp': self.timestamp.isoformat() + 'Z'
        }

def init_sample_data():
    """Initialize the database with Star Wars faction data"""
    if FactionState.query.count() == 0:
        factions = [
            {
                'faction_name': 'Galactic Empire',
                'user': 'system',
                'reputation': 0,
                'awareness': 0,
                'resources': 1000,
                'goals': json.dumps(['Maintain order', 'Eliminate Rebellion', 'Enforce Imperial law']),
                'active_operations': json.dumps(['Patrol routes', 'Intelligence gathering'])
            },
            {
                'faction_name': 'Rebel Alliance',
                'user': 'system',
                'reputation': 0,
                'awareness': 0,
                'resources': 500,
                'goals': json.dumps(['Overthrow Empire', 'Restore Republic', 'Protect civilians']),
                'active_operations': json.dumps(['Recruitment', 'Sabotage missions'])
            },
            {
                'faction_name': 'Corporate Sector Authority',
                'user': 'system',
                'reputation': 0,
                'awareness': 0,
                'resources': 800,
                'goals': json.dumps(['Maximize profits', 'Maintain trade routes', 'Expand influence']),
                'active_operations': json.dumps(['Trade negotiations', 'Security enforcement'])
            }
        ]
        
        for faction_data in factions:
            faction = FactionState(**faction_data)
            db.session.add(faction)
        
        db.session.commit()
