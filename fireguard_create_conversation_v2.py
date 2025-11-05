#!/usr/bin/env python3
"""
Fireraven conversation creation utility.
This module provides a function to create a new conversation using the Fireraven API.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def create_conversation_v2(name: str = None, description: str = None) -> str:
    """
    Create a new FireGuard conversation.
    
    Args:
        name: Name of the chatbot conversation (optional)
        description: Description of the chatbot conversation (optional)
        
    Returns:
        str: The conversation ID
        
    Raises:
        Exception: If API request fails
    """
    
    # Construct the URL
    url = f"https://api.dev.fireravenmailbox.com/public/fireguard/v1.1/conversation?project_id={os.getenv("FIRERAVEN_PROJECT_ID")}"
    
    try:
        # Make the API request
        response = requests.post(url,
            headers={
                'Content-Type': 'application/json',
                'X-Api-Key': os.getenv("FIRERAVEN_GUARDRAILS_API_KEY")
            },
            json={
                "name": name,
                "description": description
            }
        )
        
        # Check if request was successful
        if not response.ok:
            raise Exception(f"API error: {response.status_code} {response.text}")
        
        # Parse response data and return conversation ID
        data = response.json()
        conversation_id = data.get('id')
        # Response data format:
        # {
        #     id: '00000000-0000-0000-0000-000000000000',
        #     name: '',
        #     description: '',
        #     created_at: '0000-00-00T00:00:00.000Z',
        #     is_client: true
        # }
        
        if not conversation_id:
            raise Exception("No conversation ID returned from API")
        
        return conversation_id
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to create conversation: {str(e)}")
