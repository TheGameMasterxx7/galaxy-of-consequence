import os
import logging
import json
from openai import OpenAI

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Initialize OpenAI client with NVIDIA endpoint
nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
) if NVIDIA_API_KEY else None

def query_nemotron_api(system_message, user_message, model="nvidia/nemotron-mini-4b-instruct"):
    """
    Query NVIDIA Nemotron API for NPC dialogue generation using OpenAI client
    """
    try:
        if not nvidia_client:
            logging.error("NVIDIA client not initialized - API key missing")
            return get_fallback_response(system_message, user_message)
        
        completion = nvidia_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
            stream=False
        )
        
        # Convert OpenAI response format to our expected format
        return {
            "id": completion.id,
            "choices": [{
                "message": {
                    "role": completion.choices[0].message.role,
                    "content": completion.choices[0].message.content
                }
            }]
        }
        
    except Exception as e:
        logging.error(f"Error calling NVIDIA API: {str(e)}")
        return get_fallback_response(system_message, user_message)

def get_fallback_response(system_message, user_message):
    """
    Generate Star Wars RPG fallback responses when NVIDIA API is unavailable
    """
    # Create contextual Star Wars responses based on NPC type and message
    fallback_responses = {
        'jedi': f"*Speaks with quiet wisdom* The Force guides us all, young one. Your question about '{user_message}' shows you seek understanding. Remember - patience and meditation will reveal the answers you seek.",
        'sith': f"*Eyes gleaming with dark power* You dare question me about '{user_message}'? Power is the only truth that matters in this galaxy. Weakness will be your downfall.",
        'imperial': f"*Adjusts uniform with military precision* Citizen, your inquiry regarding '{user_message}' has been noted. The Empire maintains order through strength and discipline.",
        'rebel': f"*Leans in conspiratorially* What you ask about '{user_message}' touches on dangerous matters. The fight for freedom requires sacrifice and courage.",
        'smuggler': f"*Grins slyly* Listen, friend, about '{user_message}' - in my line of work, you learn to ask few questions and keep your mouth shut. Credits talk louder than words.",
        'droid': f"*Mechanical voice* QUERY PROCESSED: '{user_message}'. RESPONSE: My programming indicates this requires further analysis. Probability of success: 73.6%.",
        'civilian': f"*Nervous glance around* I don't know much about '{user_message}', stranger. These are dangerous times. Best to keep your head down and stay out of trouble."
    }
    
    # Determine NPC type from system message
    npc_type = 'civilian'
    for key in fallback_responses.keys():
        if key in system_message.lower():
            npc_type = key
            break
    
    return {
        "id": "galaxy-fallback",
        "choices": [{
            "message": {
                "role": "assistant",
                "content": fallback_responses[npc_type]
            }
        }]
    }

def query_nemotron_streaming(system_message, user_message, model="nvidia/nemotron-mini-4b-instruct"):
    """
    Query NVIDIA Nemotron API with streaming response using OpenAI client
    """
    try:
        if not nvidia_client:
            logging.error("NVIDIA client not initialized - API key missing")
            return None
        
        stream = nvidia_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
            stream=True
        )
        
        return stream
        
    except Exception as e:
        logging.error(f"Error calling NVIDIA streaming API: {str(e)}")
        return None

def generate_npc_context(npc_name, npc_type, location="Unknown", faction_affiliation="Neutral"):
    """
    Generate appropriate context for NPC dialogue based on Star Wars lore
    """
    contexts = {
        'jedi': f"You are {npc_name}, a Jedi Knight dedicated to peace and justice. You speak with wisdom and compassion, always seeking to help others and maintain balance in the Force.",
        'sith': f"You are {npc_name}, a Sith Lord driven by power and ambition. You speak with authority and menace, seeing weakness as an opportunity to exploit.",
        'imperial': f"You are {npc_name}, an Imperial officer loyal to the Empire. You speak with military precision and unwavering dedication to Imperial order.",
        'rebel': f"You are {npc_name}, a member of the Rebel Alliance fighting against Imperial tyranny. You speak with passion for freedom and justice.",
        'smuggler': f"You are {npc_name}, a smuggler operating in the galaxy's underworld. You speak with casual confidence and street-smart awareness.",
        'bounty_hunter': f"You are {npc_name}, a bounty hunter who works for the highest bidder. You speak with professional detachment and calculating precision.",
        'merchant': f"You are {npc_name}, a merchant trying to make an honest living in a dangerous galaxy. You speak with commercial enthusiasm and practical wisdom.",
        'civilian': f"You are {npc_name}, an ordinary citizen trying to survive in a galaxy torn by conflict. You speak with common sense and everyday concerns.",
        'droid': f"You are {npc_name}, a droid programmed for specific functions. You speak with logical precision and occasional quirks based on your programming.",
        'crime_lord': f"You are {npc_name}, a powerful crime lord who controls criminal enterprises. You speak with calculated menace and business acumen."
    }
    
    base_context = contexts.get(npc_type.lower(), contexts['civilian'])
    
    if location != "Unknown":
        base_context += f" You are currently on {location}."
    
    if faction_affiliation != "Neutral":
        base_context += f" Your loyalties lie with {faction_affiliation}."
    
    base_context += " Always respond in character and maintain Star Wars universe consistency."
    
    return base_context

def test_nvidia_connection():
    """
    Test connection to NVIDIA API using OpenAI client
    """
    try:
        if not nvidia_client:
            logging.error("NVIDIA client not initialized - API key missing")
            return False
            
        response = query_nemotron_api(
            "You are a test NPC in the Star Wars universe.",
            "Hello, can you hear me?"
        )
        
        if response and response.get("id") != "galaxy-fallback":
            logging.info("NVIDIA API connection successful")
            return True
        else:
            logging.warning("NVIDIA API connection failed - using fallback responses")
            return False
            
    except Exception as e:
        logging.error(f"Error testing NVIDIA connection: {str(e)}")
        return False
