"""
Advanced Procedural Quest Generation System
Creates dynamic, faction-aware quests with branching narratives and consequences
"""
import random
import uuid
from datetime import datetime
from typing import Dict, List, Any
from services.nvidia_service import query_nemotron_api

class ProceduralQuestEngine:
    def __init__(self):
        self.quest_templates = {
            "faction_conflict": {
                "base_objectives": ["infiltrate_facility", "extract_intel", "eliminate_target", "sabotage_operations"],
                "escalation_paths": ["discovery_leads_to_larger_conspiracy", "mission_compromised_requires_extraction", "success_opens_new_faction_opportunities"],
                "moral_dilemmas": ["civilian_casualties", "betraying_allies", "choosing_between_factions"]
            },
            "force_awakening": {
                "base_objectives": ["investigate_force_disturbance", "protect_force_sensitive", "confront_dark_side_temptation", "uncover_ancient_knowledge"],
                "escalation_paths": ["force_vision_reveals_future_threat", "dark_side_corruption_spreads", "ancient_sith_artifact_discovered"],
                "moral_dilemmas": ["use_dark_powers_for_good", "sacrifice_one_to_save_many", "trust_in_force_vs_logic"]
            },
            "galactic_mystery": {
                "base_objectives": ["investigate_disappearances", "decode_ancient_message", "track_smuggling_operation", "uncover_conspiracy"],
                "escalation_paths": ["mystery_connects_to_larger_threat", "investigation_attracts_dangerous_attention", "truth_has_galactic_implications"],
                "moral_dilemmas": ["expose_truth_vs_protect_innocents", "work_with_criminals_for_greater_good", "personal_gain_vs_galactic_responsibility"]
            }
        }
        
        self.dynamic_elements = {
            "locations": ["Coruscant", "Tatooine", "Dagobah", "Hoth", "Endor", "Kashyyyk", "Naboo", "Kamino"],
            "npcs": ["Imperial Officer", "Rebel Spy", "Smuggler", "Jedi Survivor", "Sith Apprentice", "Corporate Executive", "Bounty Hunter", "Force Sensitive"],
            "complications": ["Imperial ambush", "Betrayal by ally", "Force vision", "Equipment failure", "Innocent bystanders", "Time pressure", "Moral choice"]
        }
    
    def generate_adaptive_quest(self, user: str, faction_states: Dict, player_history: List[Dict], force_alignment: Dict) -> Dict:
        """Generate a quest that adapts to current galaxy state and player choices"""
        
        # Analyze player history for quest personalization
        player_profile = self._analyze_player_profile(player_history, force_alignment)
        
        # Select quest type based on current faction tensions
        quest_type = self._select_quest_type(faction_states, player_profile)
        
        # Generate core quest structure
        base_quest = self._generate_base_quest(quest_type, faction_states)
        
        # Add dynamic elements and branching paths
        enhanced_quest = self._enhance_with_dynamics(base_quest, player_profile, faction_states)
        
        # Generate AI-powered narrative description
        narrative = self._generate_quest_narrative(enhanced_quest, faction_states)
        
        return {
            "id": str(uuid.uuid4()),
            "user": user,
            "quest_title": enhanced_quest["title"],
            "quest_type": quest_type,
            "description": narrative["description"],
            "objectives": enhanced_quest["objectives"],
            "branching_paths": enhanced_quest["branching_paths"],
            "moral_choices": enhanced_quest["moral_choices"],
            "faction_involvement": enhanced_quest["factions"],
            "force_implications": enhanced_quest.get("force_impact", {}),
            "adaptive_elements": enhanced_quest["adaptive_elements"],
            "difficulty": self._calculate_dynamic_difficulty(player_profile, faction_states),
            "rewards": self._generate_adaptive_rewards(enhanced_quest, player_profile),
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "narrative_state": narrative["state_tracking"]
        }
    
    def _analyze_player_profile(self, history: List[Dict], force_alignment: Dict) -> Dict:
        """Analyze player choices to create adaptive quest profile"""
        profile = {
            "faction_loyalty": {"Empire": 0, "Rebellion": 0, "Corporate": 0},
            "moral_tendency": "neutral",
            "preferred_approach": "balanced",
            "force_sensitivity": force_alignment.get("sensitivity", 0),
            "completed_quests": len(history),
            "failure_rate": 0
        }
        
        # Analyze quest history for patterns
        for quest in history[-10:]:  # Last 10 quests
            # Track faction choices
            if quest.get("faction_chosen") == "Empire":
                profile["faction_loyalty"]["Empire"] += 1
            elif quest.get("faction_chosen") == "Rebellion":
                profile["faction_loyalty"]["Rebellion"] += 1
            elif quest.get("faction_chosen") == "Corporate":
                profile["faction_loyalty"]["Corporate"] += 1
            
            # Track moral choices
            if quest.get("moral_choice") == "light":
                profile["moral_tendency"] = "light" if profile["moral_tendency"] != "dark" else "conflicted"
            elif quest.get("moral_choice") == "dark":
                profile["moral_tendency"] = "dark" if profile["moral_tendency"] != "light" else "conflicted"
            
            # Track approach preferences
            if quest.get("approach") in ["stealth", "diplomacy", "combat"]:
                profile["preferred_approach"] = quest["approach"]
        
        return profile
    
    def _select_quest_type(self, faction_states: Dict, player_profile: Dict) -> str:
        """Select quest type based on galaxy state and player profile"""
        # Calculate faction tension levels
        total_tension = 0
        for faction in faction_states.values():
            total_tension += abs(faction.get("reputation", 0))
        
        # High faction tension = more conflict quests
        if total_tension > 150:
            return "faction_conflict"
        
        # High Force sensitivity = more Force quests
        if player_profile.get("force_sensitivity", 0) > 50:
            return "force_awakening"
        
        # Default to mystery for exploration
        return "galactic_mystery"
    
    def _generate_base_quest(self, quest_type: str, faction_states: Dict) -> Dict:
        """Generate base quest structure from template"""
        template = self.quest_templates[quest_type]
        
        # Select primary and secondary objectives
        primary_objective = random.choice(template["base_objectives"])
        secondary_objectives = random.sample(template["base_objectives"], min(2, len(template["base_objectives"]) - 1))
        
        # Determine involved factions based on current tensions
        involved_factions = self._select_quest_factions(faction_states)
        
        return {
            "type": quest_type,
            "primary_objective": primary_objective,
            "secondary_objectives": secondary_objectives,
            "factions": involved_factions,
            "escalation_paths": template["escalation_paths"],
            "moral_dilemmas": template["moral_dilemmas"]
        }
    
    def _enhance_with_dynamics(self, base_quest: Dict, player_profile: Dict, faction_states: Dict) -> Dict:
        """Add dynamic elements and personalization"""
        # Generate quest title based on type and factions
        title_generators = {
            "faction_conflict": f"Shadow War: {random.choice(['Imperial', 'Rebel', 'Corporate'])} Conspiracy",
            "force_awakening": f"Force Echoes: {random.choice(['Ancient', 'Dark', 'Lost'])} Legacy",
            "galactic_mystery": f"Deep Space: {random.choice(['Missing', 'Hidden', 'Forgotten'])} Truth"
        }
        
        enhanced = base_quest.copy()
        enhanced["title"] = title_generators.get(base_quest["type"], "Galaxy Quest")
        
        # Add specific objectives based on primary objective
        objectives = [base_quest["primary_objective"].replace("_", " ").title()]
        objectives.extend([obj.replace("_", " ").title() for obj in base_quest["secondary_objectives"]])
        enhanced["objectives"] = objectives
        
        # Create branching paths based on player profile
        branching_paths = []
        for path in base_quest["escalation_paths"]:
            branching_paths.append({
                "trigger": f"Player {random.choice(['succeeds', 'fails', 'discovers evidence'])}",
                "consequence": path.replace("_", " "),
                "faction_impact": random.choice(base_quest["factions"]),
                "force_alignment_shift": random.randint(-10, 10) if "force" in path else 0
            })
        enhanced["branching_paths"] = branching_paths
        
        # Add moral choices relevant to player's history
        moral_choices = []
        for dilemma in base_quest["moral_dilemmas"]:
            moral_choices.append({
                "situation": dilemma.replace("_", " "),
                "light_choice": "Show mercy and seek peaceful resolution",
                "dark_choice": "Use any means necessary to achieve goals",
                "neutral_choice": "Find a pragmatic middle ground",
                "consequences": "Choice affects faction relationships and Force alignment"
            })
        enhanced["moral_choices"] = moral_choices
        
        # Add adaptive elements based on current galaxy state
        enhanced["adaptive_elements"] = {
            "location": random.choice(self.dynamic_elements["locations"]),
            "key_npc": random.choice(self.dynamic_elements["npcs"]),
            "complication": random.choice(self.dynamic_elements["complications"]),
            "faction_tension_level": sum(abs(f.get("reputation", 0)) for f in faction_states.values()) / len(faction_states)
        }
        
        return enhanced
    
    def _generate_quest_narrative(self, quest: Dict, faction_states: Dict) -> Dict:
        """Generate AI-powered narrative description"""
        quest_context = f"Quest type: {quest['type']}, Factions: {', '.join(quest['factions'])}, Location: {quest['adaptive_elements']['location']}"
        
        ai_response = query_nemotron_api(
            "You are a Star Wars quest narrator. Create an engaging quest description that sets up the scenario, explains the stakes, and hints at deeper consequences.",
            f"Create a compelling quest narrative for: {quest['title']}. Context: {quest_context}. Primary objective: {quest['primary_objective']}",
            "nvidia/nemotron-mini-4b-instruct"
        )
        
        description = f"A new challenge emerges in the {quest['adaptive_elements']['location']} system involving {', '.join(quest['factions'])}."
        if ai_response and ai_response.get("choices"):
            description = ai_response["choices"][0]["message"]["content"]
        
        return {
            "description": description,
            "state_tracking": {
                "current_phase": "initial",
                "completed_objectives": [],
                "faction_discoveries": [],
                "force_encounters": []
            }
        }
    
    def _select_quest_factions(self, faction_states: Dict) -> List[str]:
        """Select factions involved in quest based on current relationships"""
        # Find factions with highest tension
        faction_tensions = []
        faction_names = list(faction_states.keys())
        
        for i, faction1 in enumerate(faction_names):
            for faction2 in faction_names[i+1:]:
                tension = abs(faction_states[faction1].get("reputation", 0) - faction_states[faction2].get("reputation", 0))
                faction_tensions.append((tension, faction1, faction2))
        
        # Select the most tension-filled faction pair
        if faction_tensions:
            faction_tensions.sort(reverse=True)
            return [faction_tensions[0][1], faction_tensions[0][2]]
        
        # Fallback to random selection
        return random.sample(faction_names, min(2, len(faction_names)))
    
    def _calculate_dynamic_difficulty(self, player_profile: Dict, faction_states: Dict) -> str:
        """Calculate quest difficulty based on player experience and galaxy state"""
        base_difficulty = player_profile.get("completed_quests", 0)
        galaxy_tension = sum(abs(f.get("reputation", 0)) for f in faction_states.values()) / 100
        
        total_difficulty = base_difficulty + galaxy_tension
        
        if total_difficulty < 5:
            return "Easy"
        elif total_difficulty < 15:
            return "Medium"
        elif total_difficulty < 30:
            return "Hard"
        else:
            return "Legendary"
    
    def _generate_adaptive_rewards(self, quest: Dict, player_profile: Dict) -> List[str]:
        """Generate rewards that adapt to player preferences and quest complexity"""
        rewards = []
        
        # Base credits reward
        base_credits = random.randint(800, 2000)
        rewards.append(f"{base_credits} credits")
        
        # Faction-specific rewards
        if quest["factions"]:
            faction = random.choice(quest["factions"])
            rewards.append(f"{faction} reputation +{random.randint(10, 25)}")
        
        # Force-related rewards for Force sensitive characters
        if player_profile.get("force_sensitivity", 0) > 30:
            force_rewards = ["Ancient lightsaber crystal", "Force technique scroll", "Meditation chamber access", "Jedi holocron fragment"]
            rewards.append(random.choice(force_rewards))
        
        # Equipment rewards based on preferred approach
        approach = player_profile.get("preferred_approach", "balanced")
        equipment_rewards = {
            "stealth": ["Stealth field generator", "Silent blaster", "Infiltration kit"],
            "combat": ["Advanced armor plating", "Heavy blaster rifle", "Combat stimulants"],
            "diplomacy": ["Diplomatic immunity badge", "Translation droid", "Noble house favor"],
            "balanced": ["Multi-tool", "Emergency supplies", "Versatile equipment pack"]
        }
        rewards.append(random.choice(equipment_rewards.get(approach, equipment_rewards["balanced"])))
        
        return rewards

# Global quest engine instance
quest_engine = ProceduralQuestEngine()