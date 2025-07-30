"""
Real-time Faction AI Turn System
Manages intelligent faction responses, territorial control, and dynamic political landscape
"""
import logging
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from services.nvidia_service import query_nemotron_api

class FactionAIEngine:
    def __init__(self):
        self.faction_personalities = {
            "Galactic Empire": {
                "aggression": 0.8,
                "intelligence": 0.9,
                "resources": 0.9,
                "ideology": "Order through strength",
                "priorities": ["military_expansion", "rebellion_suppression", "resource_control"],
                "reaction_patterns": {
                    "threatened": "mobilize_fleets",
                    "opportunity": "exploit_weakness", 
                    "diplomatic": "demand_submission"
                }
            },
            "Rebel Alliance": {
                "aggression": 0.6,
                "intelligence": 0.7,
                "resources": 0.4,
                "ideology": "Freedom and democracy",
                "priorities": ["liberation", "recruitment", "sabotage"],
                "reaction_patterns": {
                    "threatened": "guerrilla_tactics",
                    "opportunity": "coordinate_strike",
                    "diplomatic": "seek_allies"
                }
            },
            "Corporate Sector Authority": {
                "aggression": 0.5,
                "intelligence": 0.8,
                "resources": 0.7,
                "ideology": "Profit maximization",
                "priorities": ["trade_expansion", "profit_growth", "market_control"],
                "reaction_patterns": {
                    "threatened": "hire_mercenaries",
                    "opportunity": "monopolize_market",
                    "diplomatic": "negotiate_contracts"
                }
            }
        }
    
    def process_faction_turn(self, faction_name: str, current_state: Dict, galaxy_events: List[Dict]) -> Dict:
        """Process a complete AI turn for a faction"""
        personality = self.faction_personalities.get(faction_name, {})
        
        # Analyze current situation
        threat_assessment = self._assess_threats(current_state, galaxy_events)
        opportunity_analysis = self._identify_opportunities(current_state, galaxy_events)
        
        # Generate AI response based on personality and situation
        ai_actions = self._generate_ai_actions(faction_name, personality, threat_assessment, opportunity_analysis)
        
        # Execute faction turn with narrative consequences
        turn_results = self._execute_faction_turn(faction_name, current_state, ai_actions)
        
        return {
            "faction": faction_name,
            "turn_timestamp": datetime.utcnow().isoformat(),
            "threat_level": threat_assessment["overall_threat"],
            "actions_taken": ai_actions,
            "narrative_consequences": turn_results["consequences"],
            "resource_changes": turn_results["resources"],
            "territory_changes": turn_results["territory"],
            "ai_dialogue": turn_results["ai_response"]
        }
    
    def _assess_threats(self, current_state: Dict, galaxy_events: List[Dict]) -> Dict:
        """Analyze threats from other factions and player actions"""
        threats = {
            "military": 0,
            "economic": 0,
            "political": 0,
            "overall_threat": 0
        }
        
        # Analyze recent hostile actions
        for event in galaxy_events[-10:]:  # Last 10 events
            if event.get("type") == "hostile_action":
                threats["military"] += 0.2
            elif event.get("type") == "economic_sabotage":
                threats["economic"] += 0.3
            elif event.get("type") == "diplomatic_insult":
                threats["political"] += 0.1
        
        # Calculate overall threat level
        threats["overall_threat"] = min(1.0, (threats["military"] + threats["economic"] + threats["political"]) / 3)
        
        return threats
    
    def _identify_opportunities(self, current_state: Dict, galaxy_events: List[Dict]) -> Dict:
        """Identify strategic opportunities for expansion or advantage"""
        opportunities = {
            "territorial_expansion": random.uniform(0.1, 0.7),
            "resource_acquisition": random.uniform(0.2, 0.8),
            "alliance_formation": random.uniform(0.1, 0.5),
            "enemy_weakness": random.uniform(0.0, 0.6)
        }
        
        # Modify based on current resources and reputation
        resource_modifier = current_state.get("resources", 500) / 1000
        reputation_modifier = (current_state.get("reputation", 0) + 100) / 200
        
        for key in opportunities:
            opportunities[key] = min(1.0, opportunities[key] * resource_modifier * reputation_modifier)
        
        return opportunities
    
    def _generate_ai_actions(self, faction_name: str, personality: Dict, threats: Dict, opportunities: Dict) -> List[Dict]:
        """Generate intelligent faction actions based on AI personality and situation"""
        actions = []
        
        # High threat response
        if threats["overall_threat"] > 0.6:
            if personality.get("aggression", 0.5) > 0.7:
                actions.append({
                    "type": "military_mobilization",
                    "description": "Mobilize military forces in response to threats",
                    "resource_cost": 200,
                    "effectiveness": random.uniform(0.6, 0.9)
                })
            else:
                actions.append({
                    "type": "defensive_positioning", 
                    "description": "Strengthen defensive positions and fortifications",
                    "resource_cost": 150,
                    "effectiveness": random.uniform(0.5, 0.8)
                })
        
        # Opportunity exploitation
        best_opportunity = max(opportunities.items(), key=lambda x: x[1])
        if best_opportunity[1] > 0.5:
            actions.append({
                "type": f"exploit_{best_opportunity[0]}",
                "description": f"Capitalize on {best_opportunity[0].replace('_', ' ')} opportunity",
                "resource_cost": 100,
                "effectiveness": best_opportunity[1]
            })
        
        # Routine faction activities based on priorities
        for priority in personality.get("priorities", [])[:2]:
            actions.append({
                "type": f"routine_{priority}",
                "description": f"Continue {priority.replace('_', ' ')} operations",
                "resource_cost": 50,
                "effectiveness": random.uniform(0.4, 0.7)
            })
        
        return actions
    
    def _execute_faction_turn(self, faction_name: str, current_state: Dict, actions: List[Dict]) -> Dict:
        """Execute faction actions and calculate consequences"""
        total_cost = sum(action.get("resource_cost", 0) for action in actions)
        
        # Generate AI dialogue for faction leadership
        action_summary = "; ".join([action["description"] for action in actions])
        ai_prompt = f"You are the leadership of {faction_name} in the Star Wars galaxy. Your faction has taken these actions: {action_summary}. Provide a brief strategic statement explaining your faction's position and next moves."
        
        ai_response = query_nemotron_api(
            f"You are {faction_name} leadership in Star Wars",
            f"Our faction has implemented: {action_summary}. What is our strategic statement?",
            "nvidia/nemotron-mini-4b-instruct"
        )
        
        ai_dialogue = "Strategic operations continue as planned."
        if ai_response and ai_response.get("choices"):
            ai_dialogue = ai_response["choices"][0]["message"]["content"]
        
        # Calculate narrative consequences
        consequences = []
        territory_change = 0
        resource_change = -total_cost
        
        for action in actions:
            effectiveness = action.get("effectiveness", 0.5)
            if action["type"].startswith("military"):
                consequences.append(f"{faction_name} military presence increases across contested systems")
                territory_change += int(effectiveness * 10)
            elif action["type"].startswith("exploit"):
                consequences.append(f"{faction_name} expands influence through strategic opportunities") 
                resource_change += int(effectiveness * 150)
            elif action["type"].startswith("defensive"):
                consequences.append(f"{faction_name} fortifies existing positions")
        
        return {
            "consequences": consequences,
            "resources": resource_change,
            "territory": territory_change,
            "ai_response": ai_dialogue
        }

# Global faction AI engine instance
faction_ai = FactionAIEngine()