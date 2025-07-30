"""
Multiplayer Session State Management System
Handles persistent game world state across multiple players and sessions
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from services.nvidia_service import query_nemotron_api

@dataclass
class PlayerState:
    user_id: str
    character_name: str
    location: str
    force_alignment: Dict[str, float]
    faction_standings: Dict[str, int]
    active_quests: List[str]
    inventory: List[Dict]
    experience_points: int
    session_join_time: str
    last_action_time: str

@dataclass 
class SessionWorldState:
    session_id: str
    galaxy_timestamp: str
    active_conflicts: List[Dict]
    faction_control_map: Dict[str, List[str]]
    global_events: List[Dict]
    shared_narrative: List[Dict]
    session_master: str
    created_at: str
    last_updated: str

class MultplayerSessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, SessionWorldState] = {}
        self.player_sessions: Dict[str, str] = {}  # player_id -> session_id
        self.session_events: Dict[str, List[Dict]] = {}
        
        # Cross-session galaxy state tracking
        self.global_galaxy_state = {
            "major_events": [],
            "faction_power_balance": {"Empire": 40, "Rebellion": 30, "Corporate": 30},
            "force_nexus_events": [],
            "galactic_threat_level": 0.2
        }
    
    def create_session(self, session_id: str, session_master: str, initial_config: Dict = None) -> SessionWorldState:
        """Create a new multiplayer session with persistent world state"""
        
        # Generate initial galaxy state for this session
        galaxy_timestamp = self._generate_galaxy_timestamp()
        
        world_state = SessionWorldState(
            session_id=session_id,
            galaxy_timestamp=galaxy_timestamp,
            active_conflicts=self._generate_initial_conflicts(),
            faction_control_map=self._generate_faction_territories(),
            global_events=[],
            shared_narrative=[],
            session_master=session_master,
            created_at=datetime.utcnow().isoformat(),
            last_updated=datetime.utcnow().isoformat()
        )
        
        self.active_sessions[session_id] = world_state
        self.session_events[session_id] = []
        
        # Add session creation to global galaxy state
        self.global_galaxy_state["major_events"].append({
            "type": "session_created",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "description": f"New campaign begins in {galaxy_timestamp} era"
        })
        
        logging.info(f"Created multiplayer session {session_id} with master {session_master}")
        return world_state
    
    def join_session(self, session_id: str, player_id: str, character_data: Dict) -> PlayerState:
        """Add player to existing session with state synchronization"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} does not exist")
        
        # Create player state within session context
        player_state = PlayerState(
            user_id=player_id,
            character_name=character_data.get("name", f"Player_{player_id}"),
            location=character_data.get("starting_location", "Coruscant"),
            force_alignment=character_data.get("force_alignment", {"light": 0, "dark": 0, "balance": 100}),
            faction_standings=character_data.get("faction_standings", {"Empire": 0, "Rebellion": 0, "Corporate": 0}),
            active_quests=[],
            inventory=character_data.get("inventory", []),
            experience_points=character_data.get("experience", 0),
            session_join_time=datetime.utcnow().isoformat(),
            last_action_time=datetime.utcnow().isoformat()
        )
        
        # Link player to session
        self.player_sessions[player_id] = session_id
        
        # Broadcast player join to session
        join_event = {
            "type": "player_joined",
            "player_id": player_id,
            "character_name": player_state.character_name,
            "location": player_state.location,
            "timestamp": datetime.utcnow().isoformat(),
            "narrative_impact": f"{player_state.character_name} emerges in the galaxy during troubled times"
        }
        
        self.session_events[session_id].append(join_event)
        self._update_session_timestamp(session_id)
        
        logging.info(f"Player {player_id} joined session {session_id} as {player_state.character_name}")
        return player_state
    
    def process_player_action(self, player_id: str, action: Dict) -> Dict:
        """Process player action with full session state awareness"""
        
        session_id = self.player_sessions.get(player_id)
        if not session_id:
            raise ValueError(f"Player {player_id} not in any active session")
        
        session_state = self.active_sessions[session_id]
        
        # Process action based on type
        action_result = self._execute_player_action(session_id, player_id, action)
        
        # Calculate ripple effects across other players
        ripple_effects = self._calculate_action_ripples(session_id, player_id, action, action_result)
        
        # Update session world state
        self._update_world_state(session_id, action, action_result, ripple_effects)
        
        # Generate narrative consequences
        narrative_update = self._generate_action_narrative(session_id, player_id, action, action_result)
        
        return {
            "action_result": action_result,
            "ripple_effects": ripple_effects,
            "narrative_update": narrative_update,
            "updated_world_state": asdict(session_state),
            "session_events": self.session_events[session_id][-5:]  # Last 5 events
        }
    
    def sync_session_state(self, session_id: str) -> Dict:
        """Provide complete session state for all connected players"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} does not exist")
        
        session_state = self.active_sessions[session_id]
        
        # Get all players in this session
        session_players = [pid for pid, sid in self.player_sessions.items() if sid == session_id]
        
        # Calculate current faction balance
        current_balance = self._calculate_session_faction_balance(session_id)
        
        # Generate session summary with AI assistance
        session_summary = self._generate_session_summary(session_id)
        
        return {
            "session_state": asdict(session_state),
            "active_players": session_players,
            "faction_balance": current_balance,
            "recent_events": self.session_events[session_id][-10:],
            "session_summary": session_summary,
            "global_galaxy_influence": self._calculate_global_influence(session_id)
        }
    
    def advance_session_time(self, session_id: str, time_increment: str = "1 day") -> Dict:
        """Advance session time and process background world changes"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} does not exist")
        
        session_state = self.active_sessions[session_id]
        
        # Process faction AI turns during time advancement
        faction_changes = {}
        for faction in ["Empire", "Rebellion", "Corporate"]:
            faction_changes[faction] = self._process_background_faction_activity(session_id, faction, time_increment)
        
        # Generate random galaxy events
        galaxy_events = self._generate_time_passage_events(session_id, time_increment)
        
        # Update session timestamp
        session_state.galaxy_timestamp = self._advance_galaxy_timestamp(session_state.galaxy_timestamp, time_increment)
        session_state.last_updated = datetime.utcnow().isoformat()
        
        # Add time passage event
        time_event = {
            "type": "time_passage",
            "increment": time_increment,
            "faction_changes": faction_changes,
            "galaxy_events": galaxy_events,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.session_events[session_id].append(time_event)
        
        return {
            "new_timestamp": session_state.galaxy_timestamp,
            "faction_changes": faction_changes,
            "galaxy_events": galaxy_events,
            "narrative_summary": f"Time passes in the galaxy. {time_increment} elapses with significant changes across multiple systems."
        }
    
    def _generate_galaxy_timestamp(self) -> str:
        """Generate appropriate Star Wars timeline timestamp"""
        eras = [
            "25 ABY - New Jedi Order Era",
            "4 ABY - New Republic Era", 
            "0 BBY - Rebellion Era",
            "19 BBY - Dark Times",
            "22 BBY - Clone Wars"
        ]
        return f"Galactic Standard Calendar: {random.choice(eras)}"
    
    def _generate_initial_conflicts(self) -> List[Dict]:
        """Generate initial galactic conflicts for session"""
        conflicts = [
            {
                "name": "Corporate Expansion Crisis",
                "factions": ["Corporate", "Rebellion"],
                "systems": ["Sullust", "Bothawui"],
                "intensity": random.uniform(0.3, 0.7),
                "type": "economic_warfare"
            },
            {
                "name": "Imperial Remnant Operations",
                "factions": ["Empire", "Rebellion"],
                "systems": ["Endor", "Jakku"],
                "intensity": random.uniform(0.4, 0.8),
                "type": "military_conflict"
            }
        ]
        return conflicts
    
    def _generate_faction_territories(self) -> Dict[str, List[str]]:
        """Generate initial faction territorial control"""
        territories = {
            "Empire": ["Coruscant", "Kuat", "Fondor", "Carida"],
            "Rebellion": ["Mon Cala", "Chandrila", "Ryloth", "Onderon"], 
            "Corporate": ["Sullust", "Sluis Van", "Bothawui", "Malastare"],
            "Neutral": ["Tatooine", "Dagobah", "Hoth", "Kashyyyk"]
        }
        return territories
    
    def _execute_player_action(self, session_id: str, player_id: str, action: Dict) -> Dict:
        """Execute individual player action within session context"""
        action_type = action.get("type", "unknown")
        
        results = {
            "success": True,
            "experience_gained": random.randint(10, 50),
            "faction_impact": {},
            "force_impact": {},
            "location_change": None
        }
        
        # Process different action types
        if action_type == "faction_mission":
            faction = action.get("faction", "Neutral")
            results["faction_impact"][faction] = random.randint(5, 15)
            results["experience_gained"] = random.randint(25, 75)
            
        elif action_type == "force_action":
            alignment = action.get("alignment", "neutral")
            force_shift = random.randint(5, 20)
            results["force_impact"][alignment] = force_shift
            
        elif action_type == "exploration":
            new_location = action.get("destination", "Unknown System")
            results["location_change"] = new_location
            results["discovery"] = f"New area discovered: {new_location}"
        
        return results
    
    def _calculate_action_ripples(self, session_id: str, acting_player: str, action: Dict, result: Dict) -> List[Dict]:
        """Calculate how player actions affect other players in session"""
        ripples = []
        
        # Get other players in session
        session_players = [pid for pid, sid in self.player_sessions.items() if sid == session_id and pid != acting_player]
        
        # Generate ripple effects for significant actions
        if result.get("faction_impact"):
            for player in session_players:
                ripples.append({
                    "affected_player": player,
                    "effect_type": "faction_reputation_shift",
                    "magnitude": random.randint(1, 5),
                    "description": f"Political ripples from {acting_player}'s actions affect the galaxy"
                })
        
        if result.get("force_impact"):
            for player in session_players:
                ripples.append({
                    "affected_player": player,
                    "effect_type": "force_disturbance",
                    "magnitude": random.randint(1, 10),
                    "description": f"Force disturbance felt across the galaxy from {acting_player}'s actions"
                })
        
        return ripples
    
    def _update_world_state(self, session_id: str, action: Dict, result: Dict, ripples: List[Dict]):
        """Update session world state based on player actions and consequences"""
        session_state = self.active_sessions[session_id]
        
        # Update faction control based on faction impacts
        if result.get("faction_impact"):
            for faction, impact in result["faction_impact"].items():
                # Adjust faction territories and influence
                if impact > 10:  # Significant positive impact
                    session_state.faction_control_map.setdefault(faction, []).append(f"Influenced System {len(session_state.faction_control_map.get(faction, []))}")
        
        # Add significant actions to global events
        if result.get("experience_gained", 0) > 40:  # Major action
            session_state.global_events.append({
                "type": "significant_player_action",
                "action": action.get("type", "unknown"),
                "impact_level": "major",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        session_state.last_updated = datetime.utcnow().isoformat()
    
    def _generate_action_narrative(self, session_id: str, player_id: str, action: Dict, result: Dict) -> str:
        """Generate AI-powered narrative for player actions"""
        action_context = f"Player {player_id} performed {action.get('type', 'action')} with results: {result}"
        
        ai_response = query_nemotron_api(
            "You are a Star Wars game master narrator. Create engaging narrative descriptions of player actions and their consequences in the galaxy.",
            f"Describe the narrative impact of this action in the Star Wars universe: {action_context}",
            "nvidia/nemotron-mini-4b-instruct"
        )
        
        default_narrative = f"The galaxy shifts subtly as {player_id}'s actions ripple through the Force and galactic politics."
        
        if ai_response and ai_response.get("choices"):
            return ai_response["choices"][0]["message"]["content"]
        
        return default_narrative
    
    def _calculate_session_faction_balance(self, session_id: str) -> Dict[str, float]:
        """Calculate current faction power balance in session"""
        session_state = self.active_sessions[session_id]
        
        balance = {"Empire": 0.33, "Rebellion": 0.33, "Corporate": 0.33}
        
        # Calculate based on territorial control
        for faction, territories in session_state.faction_control_map.items():
            if faction != "Neutral":
                balance[faction] = len(territories) / sum(len(t) for t in session_state.faction_control_map.values() if t)
        
        return balance
    
    def _generate_session_summary(self, session_id: str) -> str:
        """Generate AI-powered session summary"""
        session_state = self.active_sessions[session_id]
        recent_events = self.session_events[session_id][-5:]
        
        summary_context = f"Session in {session_state.galaxy_timestamp} with recent events: {[e.get('type', 'unknown') for e in recent_events]}"
        
        ai_response = query_nemotron_api(
            "You are a Star Wars chronicler. Summarize the current state of a galactic campaign session.",
            f"Provide a brief session summary for: {summary_context}",
            "nvidia/nemotron-mini-4b-instruct"
        )
        
        default_summary = f"The galaxy remains in flux during {session_state.galaxy_timestamp}, with multiple factions vying for control and the Force guiding destiny."
        
        if ai_response and ai_response.get("choices"):
            return ai_response["choices"][0]["message"]["content"]
        
        return default_summary

# Import required modules for complete functionality
import random
from services.faction_ai_service import faction_ai

# Global session manager instance
session_manager = MultplayerSessionManager()