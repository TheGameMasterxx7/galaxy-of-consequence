import json
import random
import logging
from datetime import datetime, timedelta
from models import FactionState

def update_faction_ai(faction, action, target_faction=None):
    """
    Update faction AI based on player actions
    """
    try:
        # Define faction response logic
        if action == 'help_empire':
            if faction.faction_name == 'Galactic Empire':
                faction.reputation += 10
                faction.awareness += 5
            elif faction.faction_name == 'Rebel Alliance':
                faction.reputation -= 15
                faction.awareness += 10
        
        elif action == 'help_rebels':
            if faction.faction_name == 'Rebel Alliance':
                faction.reputation += 10
                faction.awareness += 5
            elif faction.faction_name == 'Galactic Empire':
                faction.reputation -= 15
                faction.awareness += 10
        
        elif action == 'smuggling':
            if faction.faction_name == 'Corporate Sector Authority':
                faction.reputation -= 5
                faction.awareness += 8
            elif faction.faction_name == 'Galactic Empire':
                faction.reputation -= 3
                faction.awareness += 5
        
        elif action == 'bounty_hunting':
            if faction.faction_name == 'Galactic Empire':
                faction.reputation += 5
                faction.awareness += 3
        
        elif action == 'piracy':
            # All legitimate factions dislike piracy
            if faction.faction_name in ['Galactic Empire', 'Rebel Alliance', 'Corporate Sector Authority']:
                faction.reputation -= 10
                faction.awareness += 15
        
        # Passive faction evolution
        elif action == 'passive_tick':
            # Factions gradually lose awareness if player is inactive
            if faction.awareness > 0:
                faction.awareness = max(0, faction.awareness - 1)
        
        # Update resources based on reputation and time
        if faction.reputation > 50:
            faction.resources = min(1000, faction.resources + 5)
        elif faction.reputation < -50:
            faction.resources = max(100, faction.resources - 3)
        
        # Update active operations based on awareness
        operations = json.loads(faction.active_operations) if faction.active_operations else []
        
        if faction.awareness > 70:
            if 'Hunt player' not in operations:
                operations.append('Hunt player')
        elif faction.awareness < 30:
            operations = [op for op in operations if op != 'Hunt player']
        
        faction.active_operations = json.dumps(operations)
        faction.last_interaction = datetime.utcnow()
        
        return faction
        
    except Exception as e:
        logging.error(f"Error updating faction AI: {str(e)}")
        return None

def calculate_faction_response(old_state, new_state):
    """
    Calculate specific faction responses based on state changes
    """
    responses = []
    
    reputation_change = new_state['reputation'] - old_state['reputation']
    awareness_change = new_state['awareness'] - old_state['awareness']
    
    if reputation_change > 10:
        responses.append(f"{new_state['faction_name']} regards you more favorably")
    elif reputation_change < -10:
        responses.append(f"{new_state['faction_name']} is displeased with your actions")
    
    if awareness_change > 15:
        responses.append(f"{new_state['faction_name']} is now actively tracking you")
    elif awareness_change > 5:
        responses.append(f"{new_state['faction_name']} has taken notice of your activities")
    
    # Special faction-specific responses
    faction_name = new_state['faction_name']
    if faction_name == 'Galactic Empire' and new_state['awareness'] > 80:
        responses.append("Imperial Intelligence has issued a priority alert on your activities")
    elif faction_name == 'Rebel Alliance' and new_state['reputation'] > 70:
        responses.append("The Rebellion considers you a valuable ally")
    elif faction_name == 'Corporate Sector Authority' and new_state['reputation'] < -60:
        responses.append("CSA has initiated asset seizure protocols")
    
    return responses

def generate_procedural_quest(user, faction_states, quest_data=None):
    """
    Generate procedural quests based on current game state and faction relationships
    """
    try:
        # Analyze faction states to determine quest opportunities
        high_reputation_factions = [f for f in faction_states if f.reputation > 30]
        hostile_factions = [f for f in faction_states if f.reputation < -30]
        high_awareness_factions = [f for f in faction_states if f.awareness > 60]
        
        quest_templates = {
            'delivery': {
                'titles': [
                    'Critical Supply Run',
                    'Urgent Package Delivery',
                    'Classified Transport Mission'
                ],
                'descriptions': [
                    'A {faction} contact needs sensitive materials delivered to {location}.',
                    'Transport classified cargo through {threat} territory.',
                    'Rush delivery of medical supplies to {location}.'
                ]
            },
            'rescue': {
                'titles': [
                    'Extraction Operation',
                    'Rescue Mission',
                    'Prisoner Liberation'
                ],
                'descriptions': [
                    'A {faction} agent is trapped behind enemy lines.',
                    'Extract civilians from {location} before {threat} arrives.',
                    'Break out a political prisoner from {enemy_faction} custody.'
                ]
            },
            'sabotage': {
                'titles': [
                    'Covert Operations',
                    'Sabotage Mission',
                    'Disruption Protocol'
                ],
                'descriptions': [
                    'Disable {enemy_faction} communications on {location}.',
                    'Sabotage {enemy_faction} supply lines.',
                    'Plant surveillance devices in {enemy_faction} facilities.'
                ]
            },
            'investigation': {
                'titles': [
                    'Intelligence Gathering',
                    'Mystery Investigation',
                    'Corporate Espionage'
                ],
                'descriptions': [
                    'Investigate suspicious {enemy_faction} activities.',
                    'Uncover the truth behind recent attacks on {faction} assets.',
                    'Gather intelligence on {enemy_faction} fleet movements.'
                ]
            }
        }
        
        # Select quest type based on faction relationships
        if hostile_factions and random.random() < 0.4:
            quest_type = random.choice(['sabotage', 'investigation'])
        elif high_reputation_factions and random.random() < 0.5:
            quest_type = random.choice(['delivery', 'rescue'])
        else:
            quest_type = random.choice(list(quest_templates.keys()))
        
        template = quest_templates[quest_type]
        
        # Select factions for quest
        quest_giver = random.choice(high_reputation_factions) if high_reputation_factions else random.choice(faction_states)
        enemy_faction = random.choice(hostile_factions) if hostile_factions else random.choice([f for f in faction_states if f != quest_giver])
        
        # Generate quest details
        quest_title = random.choice(template['titles'])
        quest_description = random.choice(template['descriptions']).format(
            faction=quest_giver.faction_name,
            enemy_faction=enemy_faction.faction_name,
            location=random.choice(['Tatooine', 'Coruscant', 'Naboo', 'Kashyyyk', 'Ryloth']),
            threat=enemy_faction.faction_name
        )
        
        # Generate objectives
        objectives = generate_quest_objectives(quest_type, quest_giver.faction_name, enemy_faction.faction_name)
        
        # Generate rewards
        rewards = generate_quest_rewards(quest_type, quest_giver.reputation)
        
        # Determine difficulty
        difficulty = 'Easy'
        if enemy_faction.awareness > 60:
            difficulty = 'Hard'
        elif enemy_faction.awareness > 30:
            difficulty = 'Medium'
        
        return {
            'title': quest_title,
            'type': quest_type,
            'description': quest_description,
            'objectives': objectives,
            'rewards': rewards,
            'difficulty': difficulty,
            'faction_involvement': [quest_giver.faction_name, enemy_faction.faction_name]
        }
        
    except Exception as e:
        logging.error(f"Error generating procedural quest: {str(e)}")
        # Return a default quest
        return {
            'title': 'Routine Mission',
            'type': 'delivery',
            'description': 'A simple transport job has become available.',
            'objectives': ['Deliver package to destination', 'Avoid Imperial patrols'],
            'rewards': ['1000 credits', 'Faction reputation +5'],
            'difficulty': 'Easy',
            'faction_involvement': ['Independent']
        }

def generate_quest_objectives(quest_type, faction, enemy_faction):
    """Generate appropriate objectives for quest type"""
    objectives_map = {
        'delivery': [
            f'Obtain package from {faction} contact',
            'Navigate to destination safely',
            'Deliver package without detection',
            'Report back to quest giver'
        ],
        'rescue': [
            f'Locate {faction} agent',
            f'Avoid {enemy_faction} patrols',
            'Extract target safely',
            'Escort to safe house'
        ],
        'sabotage': [
            f'Infiltrate {enemy_faction} facility',
            'Plant surveillance devices',
            'Avoid security detection',
            'Escape without raising alarms'
        ],
        'investigation': [
            'Gather intelligence at location',
            'Interview witnesses',
            'Analyze collected data',
            'Report findings'
        ]
    }
    
    return objectives_map.get(quest_type, ['Complete the mission'])

def generate_quest_rewards(quest_type, faction_reputation):
    """Generate appropriate rewards based on quest type and faction standing"""
    base_credits = random.randint(500, 2000)
    
    # Adjust credits based on faction reputation
    if faction_reputation > 50:
        base_credits = int(base_credits * 1.5)
    elif faction_reputation < -30:
        base_credits = int(base_credits * 0.7)
    
    rewards = [f'{base_credits} credits']
    
    if random.random() < 0.6:
        rewards.append('Faction reputation +10')
    
    if random.random() < 0.3:
        equipment_rewards = [
            'Upgraded blaster',
            'Advanced comlink',
            'Stealth field generator',
            'Medical supplies',
            'Ship upgrade components'
        ]
        rewards.append(random.choice(equipment_rewards))
    
    if quest_type == 'rescue' and random.random() < 0.4:
        rewards.append('New ally contact')
    
    return rewards

def calculate_galaxy_momentum(faction_states):
    """Calculate overall galaxy momentum based on faction activities"""
    total_momentum = 0
    
    for faction in faction_states:
        # High awareness and extreme reputation contribute to momentum
        momentum_contribution = faction.awareness
        if abs(faction.reputation) > 60:
            momentum_contribution += 20
        
        total_momentum += momentum_contribution
    
    return min(100, total_momentum)
