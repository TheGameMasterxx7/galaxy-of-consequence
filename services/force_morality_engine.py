"""
Force Morality Engine with Narrative Consequences
Tracks Force alignment, moral choices, and their cascading effects across the galaxy
"""
import logging
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from services.nvidia_service import query_nemotron_api

class ForceAlignment(Enum):
    LIGHT = "light"
    DARK = "dark"
    BALANCE = "balance"
    GRAY = "gray"
    CONFLICTED = "conflicted"

class MoralConsequence(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    GALACTIC = "galactic"

@dataclass
class MoralChoice:
    choice_id: str
    description: str
    alignment_shift: Dict[str, int]
    narrative_weight: float
    consequence_level: MoralConsequence
    faction_impacts: Dict[str, int]
    force_echo: bool
    timestamp: str

@dataclass
class ForceProfile:
    user_id: str
    light_side_points: int
    dark_side_points: int
    balance_points: int
    current_alignment: ForceAlignment
    force_sensitivity: float
    moral_history: List[MoralChoice]
    destiny_threads: List[str]
    corruption_resistance: float
    redemption_potential: float

class ForceMoralityEngine:
    def __init__(self):
        self.force_profiles: Dict[str, ForceProfile] = {}
        self.galactic_force_events: List[Dict] = []
        self.destiny_nexus_points: List[Dict] = []
        
        # Force sensitivity thresholds and effects
        self.force_thresholds = {
            "untrained": (0, 25),
            "sensitive": (25, 50),
            "adept": (50, 75),
            "master": (75, 90),
            "legendary": (90, 100)
        }
        
        # Moral choice templates with escalating consequences
        self.moral_templates = {
            "sacrifice_dilemma": {
                "description": "Save one to doom many, or sacrifice few for the greater good",
                "light_choice": {"points": 15, "description": "Choose compassion and find another way"},
                "dark_choice": {"points": -20, "description": "Embrace pragmatic ruthlessness"},
                "consequences": ["Ripples through Force connections", "Affects faction relationships", "Changes NPC reactions"]
            },
            "power_temptation": {
                "description": "Use forbidden knowledge or power to achieve righteous goals",
                "light_choice": {"points": 10, "description": "Reject the easy path and maintain principles"},
                "dark_choice": {"points": -25, "description": "Embrace power regardless of source"},
                "consequences": ["Force corruption spreads", "Dark side temptations increase", "Ancient evils stir"]
            },
            "mercy_vs_justice": {
                "description": "Show mercy to an enemy or deliver absolute justice",
                "light_choice": {"points": 12, "description": "Offer redemption and second chances"},
                "dark_choice": {"points": -15, "description": "Ensure justice through decisive action"},
                "consequences": ["Reputation shifts across factions", "Future encounters change", "Moral echoes in the Force"]
            }
        }
    
    def initialize_force_profile(self, user_id: str, initial_alignment: str = "balance") -> ForceProfile:
        """Initialize Force profile for a new player"""
        profile = ForceProfile(
            user_id=user_id,
            light_side_points=0 if initial_alignment != "light" else 50,
            dark_side_points=0 if initial_alignment != "dark" else 50,
            balance_points=100 if initial_alignment == "balance" else 0,
            current_alignment=ForceAlignment(initial_alignment),
            force_sensitivity=random.uniform(0.1, 0.8),
            moral_history=[],
            destiny_threads=[],
            corruption_resistance=random.uniform(0.3, 0.9),
            redemption_potential=random.uniform(0.4, 1.0)
        )
        
        self.force_profiles[user_id] = profile
        logging.info(f"Initialized Force profile for {user_id} with {initial_alignment} alignment")
        return profile
    
    def process_moral_choice(self, user_id: str, choice_context: Dict, selected_choice: str) -> Dict:
        """Process a moral choice and calculate Force/narrative consequences"""
        if user_id not in self.force_profiles:
            self.initialize_force_profile(user_id)
        
        profile = self.force_profiles[user_id]
        
        # Generate moral choice based on context
        moral_choice = self._generate_contextual_choice(choice_context, selected_choice, profile)
        
        # Apply Force alignment shifts
        alignment_changes = self._apply_force_shifts(profile, moral_choice)
        
        # Calculate narrative consequences
        narrative_consequences = self._calculate_narrative_consequences(profile, moral_choice)
        
        # Update Force profile
        profile.moral_history.append(moral_choice)
        self._update_alignment_status(profile)
        
        # Generate Force echoes for significant choices
        force_echoes = self._generate_force_echoes(profile, moral_choice)
        
        # Create galactic ripples for major choices
        galactic_impacts = self._process_galactic_impacts(profile, moral_choice)
        
        return {
            "moral_choice": asdict(moral_choice),
            "alignment_changes": alignment_changes,
            "new_alignment": profile.current_alignment.value,
            "force_sensitivity_change": self._calculate_sensitivity_change(moral_choice),
            "narrative_consequences": narrative_consequences,
            "force_echoes": force_echoes,
            "galactic_impacts": galactic_impacts,
            "destiny_shift": self._calculate_destiny_shift(profile, moral_choice)
        }
    
    def generate_force_vision(self, user_id: str, context: Dict = None) -> Dict:
        """Generate AI-powered Force vision based on player's moral trajectory"""
        if user_id not in self.force_profiles:
            return {"error": "No Force profile found"}
        
        profile = self.force_profiles[user_id]
        
        # Analyze moral trajectory
        trajectory = self._analyze_moral_trajectory(profile)
        
        # Generate vision context
        vision_type = self._determine_vision_type(profile, trajectory)
        
        # Create AI-powered vision narrative
        vision_narrative = self._generate_vision_narrative(profile, vision_type, context)
        
        # Calculate vision significance
        significance = self._calculate_vision_significance(profile, vision_type)
        
        return {
            "vision_type": vision_type,
            "narrative": vision_narrative,
            "significance": significance,
            "force_alignment_insight": trajectory,
            "destiny_revelation": self._generate_destiny_revelation(profile),
            "moral_guidance": self._generate_moral_guidance(profile)
        }
    
    def calculate_force_corruption(self, user_id: str) -> Dict:
        """Calculate and track Force corruption effects"""
        if user_id not in self.force_profiles:
            return {"error": "No Force profile found"}
        
        profile = self.force_profiles[user_id]
        
        # Calculate corruption level
        corruption_level = self._calculate_corruption_level(profile)
        
        # Determine corruption effects
        corruption_effects = self._determine_corruption_effects(profile, corruption_level)
        
        # Generate redemption path if applicable
        redemption_path = self._generate_redemption_path(profile) if corruption_level > 0.5 else None
        
        return {
            "corruption_level": corruption_level,
            "corruption_effects": corruption_effects,
            "redemption_potential": profile.redemption_potential,
            "redemption_path": redemption_path,
            "resistance_breakdown": self._analyze_corruption_resistance(profile)
        }
    
    def track_destiny_threads(self, user_id: str, action_context: Dict) -> Dict:
        """Track and weave destiny threads through player actions"""
        if user_id not in self.force_profiles:
            self.initialize_force_profile(user_id)
        
        profile = self.force_profiles[user_id]
        
        # Analyze action for destiny significance
        destiny_weight = self._calculate_destiny_weight(action_context, profile)
        
        # Update destiny threads
        new_threads = self._generate_destiny_threads(action_context, profile)
        profile.destiny_threads.extend(new_threads)
        
        # Identify destiny convergence points
        convergence_points = self._identify_destiny_convergence(profile)
        
        # Generate prophetic insights
        prophetic_insights = self._generate_prophetic_insights(profile, action_context)
        
        return {
            "destiny_weight": destiny_weight,
            "new_threads": new_threads,
            "active_threads": profile.destiny_threads[-10:],  # Last 10 threads
            "convergence_points": convergence_points,
            "prophetic_insights": prophetic_insights,
            "fate_momentum": self._calculate_fate_momentum(profile)
        }
    
    def _generate_contextual_choice(self, context: Dict, selected_choice: str, profile: ForceProfile) -> MoralChoice:
        """Generate moral choice based on context and player history"""
        choice_type = context.get("type", "general")
        template = self.moral_templates.get(choice_type, self.moral_templates["sacrifice_dilemma"])
        
        # Calculate alignment shift based on choice and current alignment
        base_shift = 10
        if selected_choice == "light":
            alignment_shift = {"light": base_shift, "dark": -base_shift//2, "balance": base_shift//2}
        elif selected_choice == "dark":
            alignment_shift = {"dark": base_shift, "light": -base_shift//2, "balance": -base_shift//2}
        else:  # balance/gray choice
            alignment_shift = {"balance": base_shift, "light": 0, "dark": 0}
        
        # Amplify shifts based on Force sensitivity
        sensitivity_multiplier = 1 + (profile.force_sensitivity * 0.5)
        for key in alignment_shift:
            alignment_shift[key] = int(alignment_shift[key] * sensitivity_multiplier)
        
        return MoralChoice(
            choice_id=f"choice_{len(profile.moral_history)}_{datetime.utcnow().timestamp()}",
            description=context.get("description", template["description"]),
            alignment_shift=alignment_shift,
            narrative_weight=random.uniform(0.3, 1.0),
            consequence_level=MoralConsequence(context.get("consequence_level", "moderate")),
            faction_impacts=context.get("faction_impacts", {}),
            force_echo=profile.force_sensitivity > 0.5,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _apply_force_shifts(self, profile: ForceProfile, choice: MoralChoice) -> Dict:
        """Apply Force alignment shifts from moral choice"""
        before_state = {
            "light": profile.light_side_points,
            "dark": profile.dark_side_points,
            "balance": profile.balance_points
        }
        
        # Apply shifts with corruption resistance
        for alignment, shift in choice.alignment_shift.items():
            if alignment == "light":
                profile.light_side_points = max(0, min(100, profile.light_side_points + shift))
            elif alignment == "dark":
                # Dark side shifts affected by corruption resistance
                effective_shift = shift * (1 - profile.corruption_resistance * 0.3)
                profile.dark_side_points = max(0, min(100, profile.dark_side_points + int(effective_shift)))
            elif alignment == "balance":
                profile.balance_points = max(0, min(100, profile.balance_points + shift))
        
        after_state = {
            "light": profile.light_side_points,
            "dark": profile.dark_side_points,
            "balance": profile.balance_points
        }
        
        return {
            "before": before_state,
            "after": after_state,
            "shifts": choice.alignment_shift
        }
    
    def _calculate_narrative_consequences(self, profile: ForceProfile, choice: MoralChoice) -> List[Dict]:
        """Calculate specific narrative consequences of moral choices"""
        consequences = []
        
        # Base consequence from choice
        consequences.append({
            "type": "immediate",
            "description": f"Your choice echoes through the Force",
            "magnitude": choice.narrative_weight
        })
        
        # Faction-related consequences
        for faction, impact in choice.faction_impacts.items():
            consequences.append({
                "type": "faction_relationship",
                "faction": faction,
                "impact": impact,
                "description": f"Relationship with {faction} {'improves' if impact > 0 else 'deteriorates'}"
            })
        
        # Force-related consequences
        if choice.force_echo:
            consequences.append({
                "type": "force_disturbance",
                "description": "Your actions create ripples in the Force felt by other Force users",
                "range": "galactic" if choice.consequence_level == MoralConsequence.GALACTIC else "local"
            })
        
        # Alignment-specific consequences
        dominant_alignment = max(choice.alignment_shift.items(), key=lambda x: abs(x[1]))
        if abs(dominant_alignment[1]) > 15:  # Significant alignment shift
            consequences.append({
                "type": "character_development",
                "alignment": dominant_alignment[0],
                "description": f"Your character undergoes significant {dominant_alignment[0]} side development"
            })
        
        return consequences
    
    def _generate_vision_narrative(self, profile: ForceProfile, vision_type: str, context: Dict) -> str:
        """Generate AI-powered Force vision narrative"""
        vision_context = f"Force vision type: {vision_type}, Current alignment: {profile.current_alignment.value}, Force sensitivity: {profile.force_sensitivity:.2f}"
        
        ai_prompt = f"Generate a Star Wars Force vision for a character with {vision_context}. The vision should be mystical, prophetic, and relevant to their moral journey."
        
        ai_response = query_nemotron_api(
            "You are the Force itself, speaking through visions. Create mystical, prophetic visions that guide moral choices in the Star Wars universe.",
            ai_prompt,
            "nvidia/nemotron-mini-4b-instruct"
        )
        
        default_vision = f"In the swirling mists of the Force, you see echoes of choices yet to come. The {profile.current_alignment.value} within you pulses with possibility."
        
        if ai_response and ai_response.get("choices"):
            return ai_response["choices"][0]["message"]["content"]
        
        return default_vision
    
    def _update_alignment_status(self, profile: ForceProfile):
        """Update overall alignment based on point distribution"""
        total_points = profile.light_side_points + profile.dark_side_points + profile.balance_points
        
        if total_points == 0:
            profile.current_alignment = ForceAlignment.BALANCE
            return
        
        light_ratio = profile.light_side_points / total_points
        dark_ratio = profile.dark_side_points / total_points
        balance_ratio = profile.balance_points / total_points
        
        # Determine primary alignment
        if light_ratio > 0.6:
            profile.current_alignment = ForceAlignment.LIGHT
        elif dark_ratio > 0.6:
            profile.current_alignment = ForceAlignment.DARK
        elif balance_ratio > 0.4:
            profile.current_alignment = ForceAlignment.BALANCE
        elif abs(light_ratio - dark_ratio) < 0.2:
            profile.current_alignment = ForceAlignment.CONFLICTED
        else:
            profile.current_alignment = ForceAlignment.GRAY
    
    def _analyze_moral_trajectory(self, profile: ForceProfile) -> Dict:
        """Analyze the player's moral trajectory over time"""
        if len(profile.moral_history) < 2:
            return {"trend": "insufficient_data", "stability": 1.0}
        
        # Calculate trend over last 5 choices
        recent_choices = profile.moral_history[-5:]
        light_trend = sum(choice.alignment_shift.get("light", 0) for choice in recent_choices)
        dark_trend = sum(choice.alignment_shift.get("dark", 0) for choice in recent_choices)
        
        trend = "toward_light" if light_trend > dark_trend else "toward_dark" if dark_trend > light_trend else "balanced"
        
        # Calculate moral stability (simplified)
        alignment_variance = sum(abs(choice.alignment_shift.get("light", 0) - choice.alignment_shift.get("dark", 0)) for choice in recent_choices)
        stability = max(0.0, 1.0 - (alignment_variance / 100))
        
        return {
            "trend": trend,
            "stability": stability,
            "light_momentum": light_trend,
            "dark_momentum": dark_trend,
            "trajectory_strength": abs(light_trend - dark_trend)
        }
    
    def _determine_vision_type(self, profile: ForceProfile, trajectory: Dict) -> str:
        """Determine type of Force vision based on profile"""
        if profile.current_alignment == ForceAlignment.DARK:
            return "dark_temptation"
        elif profile.current_alignment == ForceAlignment.LIGHT:
            return "light_guidance"
        elif trajectory["trend"] == "toward_dark":
            return "warning_vision"
        else:
            return "balance_insight"
    
    def _calculate_vision_significance(self, profile: ForceProfile, vision_type: str) -> str:
        """Calculate significance level of vision"""
        base_significance = profile.force_sensitivity
        if len(profile.moral_history) > 10:
            base_significance += 0.2
        
        if base_significance > 0.8:
            return "prophetic"
        elif base_significance > 0.6:
            return "significant"
        elif base_significance > 0.4:
            return "meaningful"
        else:
            return "subtle"
    
    def _generate_destiny_revelation(self, profile: ForceProfile) -> str:
        """Generate destiny revelation content"""
        return f"Your path through the {profile.current_alignment.value} side of the Force shapes galactic destiny"
    
    def _generate_moral_guidance(self, profile: ForceProfile) -> str:
        """Generate moral guidance for player"""
        if profile.current_alignment == ForceAlignment.DARK:
            return "The dark side clouds your judgment, but redemption remains possible"
        elif profile.current_alignment == ForceAlignment.LIGHT:
            return "The light side illuminates the path of compassion and justice"
        else:
            return "Balance in the Force brings wisdom and understanding"
    
    def _calculate_corruption_level(self, profile: ForceProfile) -> float:
        """Calculate current corruption level"""
        total_points = profile.light_side_points + profile.dark_side_points + profile.balance_points
        if total_points == 0:
            return 0.0
        return profile.dark_side_points / total_points
    
    def _determine_corruption_effects(self, profile: ForceProfile, corruption_level: float) -> List[str]:
        """Determine effects of Force corruption"""
        effects = []
        if corruption_level > 0.7:
            effects.extend(["Physical manifestation of dark side", "Aggressive tendencies", "Fear of loss"])
        elif corruption_level > 0.5:
            effects.extend(["Emotional instability", "Quick to anger", "Distrustful"])
        elif corruption_level > 0.3:
            effects.extend(["Occasional dark thoughts", "Tempted by power"])
        return effects
    
    def _generate_redemption_path(self, profile: ForceProfile) -> Dict:
        """Generate potential redemption path"""
        return {
            "difficulty": "challenging" if profile.dark_side_points > 70 else "moderate",
            "steps": ["Acknowledge past mistakes", "Seek forgiveness", "Perform selfless acts"],
            "time_required": "long journey" if profile.dark_side_points > 70 else "focused effort"
        }
    
    def _analyze_corruption_resistance(self, profile: ForceProfile) -> Dict:
        """Analyze corruption resistance factors"""
        return {
            "base_resistance": profile.corruption_resistance,
            "light_side_strength": profile.light_side_points / 100,
            "moral_consistency": len([c for c in profile.moral_history[-5:] if c.alignment_shift.get("light", 0) > 0]) / 5
        }
    
    def _calculate_destiny_weight(self, action_context: Dict, profile: ForceProfile) -> float:
        """Calculate destiny weight of action"""
        base_weight = 0.3
        if action_context.get("type") == "major_decision":
            base_weight += 0.4
        if profile.force_sensitivity > 0.7:
            base_weight += 0.3
        return min(1.0, base_weight)
    
    def _generate_destiny_threads(self, action_context: Dict, profile: ForceProfile) -> List[str]:
        """Generate new destiny threads"""
        threads = []
        action_type = action_context.get("type", "unknown")
        threads.append(f"Thread: {action_type} echoes through time")
        if profile.current_alignment != ForceAlignment.BALANCE:
            threads.append(f"Thread: {profile.current_alignment.value} path strengthens")
        return threads
    
    def _identify_destiny_convergence(self, profile: ForceProfile) -> List[Dict]:
        """Identify destiny convergence points"""
        convergences = []
        if len(profile.destiny_threads) > 5:
            convergences.append({
                "type": "thread_intersection",
                "description": "Multiple destiny threads converge",
                "significance": "major"
            })
        return convergences
    
    def _generate_prophetic_insights(self, profile: ForceProfile, action_context: Dict) -> List[str]:
        """Generate prophetic insights"""
        insights = []
        if profile.force_sensitivity > 0.6:
            insights.append("The Force whispers of choices yet to come")
        if profile.current_alignment == ForceAlignment.CONFLICTED:
            insights.append("Balance teeters on the edge of a blade")
        return insights
    
    def _calculate_fate_momentum(self, profile: ForceProfile) -> float:
        """Calculate fate momentum"""
        return min(1.0, len(profile.destiny_threads) * 0.1 + profile.force_sensitivity * 0.5)
    
    def _calculate_sensitivity_change(self, choice: MoralChoice) -> float:
        """Calculate Force sensitivity change from choice"""
        if choice.force_echo:
            return random.uniform(0.01, 0.05)
        return 0.0

# Global Force morality engine instance
force_engine = ForceMoralityEngine()