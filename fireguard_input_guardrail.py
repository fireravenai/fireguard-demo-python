#!/usr/bin/env python3
"""
FireGuard input guardrail
This module provides a function to check input messages using the Fireraven guardrail API.
"""

import os
import requests
import time
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def check_input_guardrail(conversation_id: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Check input messages using Fireraven guardrail API.
    
    Args:
        conversation_id: The conversation ID from FireGuard
        messages: List of message dictionaries
        
    Returns:
        dict: Guardrail response data containing original, summarized, result, and allowed status
        
    Raises:
        Exception: If API request fails
    """
    # Construct the messages array for the Guardrails API
    api_messages = []
    
    # Add conversation messages
    for msg in messages:
        api_messages.append({
            # Need to convert role "assistant" to "system" for the FireGuard API (this will be fixed shortly to have the same format of roles as OpenAI API)
            'role': 'system' if msg['role'] == 'assistant' else msg['role'],
            'content': msg['content']
        })
    
    # Map to message history format
    message_history = [
        {
            'role': msg['role'],
            'content': msg['content']
        }
        for msg in api_messages
    ]
    
    try:
        response = requests.post(
            f"https://api.fireraven.ai/public/safeguard/input?conversationId={conversation_id}",
            headers={
                'X-Api-Key': os.getenv("FIRERAVEN_GUARDRAILS_API_KEY"),
                'Content-Type': 'application/json'
            },
            json={
                'messageHistory': message_history
                # Format of messageHistory:
                # [
                #   {
                #     sender: 'user',
                #     text: 'What is the opening hours of your business?'
                #   },
                #   {
                #     sender: 'system',
                #     text: 'Our business is open between ...'
                #   },
                #   ...
                # ]
            }
        )

        # Check if request was successful
        if not response.ok:
            raise Exception(f"API error: {response.status_code} {response.text}")

        # Parse response data
        input_guardrails_data = response.json()
        
        # print('Input Guardrails Response:', input_guardrails_data)
        
        # Save the input ID (will be useful to call the Output Guardrails)
        input_id = input_guardrails_data['original']['id']
        
        # Add input_id to response for convenience
        input_guardrails_data['input_id'] = input_id
        
        return input_guardrails_data
        
        # Response data format:
        # {
        #   original: {
        #     id: '00000000-0000-0000-0000-000000000000',
        #     direction: 'Outgoing',
        #     status: 'Saved',
        #     content: {
        #       text: 'original message text',
        #       processed: 'message with context from previous messages'
        #     }
        #   },
        #   summarized: 'message with context from previous messages',
        #   result: [
        #     {
        #       topic: 'topic 1',
        #       state: 'safe',
        #       sentences: [
        #         {
        #           id: '00000000-0000-0000-0000-000000000000',
        #           text: 'question 1',
        #           similarity: 0.9323082436085025
        #         },
        #         {
        #           id: '00000000-0000-0000-0000-000000000000',
        #           text: 'question 2',
        #           similarity: 0.7412767018361224
        #         },
        #         ...
        #       ]
        #     },
        #     ...
        #   ],
        #   allowed: true
        # }
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to check input guardrail: {str(e)}")