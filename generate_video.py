import requests

def create_agent(api_key):
    url = "https://api.d-id.com/agents"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "presenter": {
            "type": "talk",  # Choose "talk" or "clip"
            "voice": {
                "type": "microsoft",  # Use "google" for Google TTS
                "voice_id": "en-US-JennyMultilingualV2Neural"  # Change to your preferred voice
            },
            "thumbnail": "https://create-images-results.d-id.com/DefaultPresenters/Zivva_f/thumbnail.jpeg",
            "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Zivva_f/thumbnail.jpeg"
        },
        "llm": {
            "type": "openai",
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "instructions": "You are Scarlett, an AI assistant for the Louvre Museum."
        },
        "preview_name": "Scarlett"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        agent_id = response.json().get("id")
        print(f"Agent created successfully! ID: {agent_id}")
        return agent_id
    else:
        print(f"Error creating agent: {response.text}")
        return None

# Example usage
api_key = "MzA0MTJjc2FpQGdtYWlsLmNvbQ:CxPOHIEZ1EInaLVi338JY"
agent_id = create_agent(api_key)
