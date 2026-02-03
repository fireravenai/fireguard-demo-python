#!/usr/bin/env python3
"""
FireGuard input guardrail
This module provides a function to check input messages using the Fireraven guardrail API.
"""

import os
import requests
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
    
    try:
        response = requests.post(
            f"https://api.fireraven.ai/public/fireguard/v1.1/input_guardrails?conversation_id={conversation_id}",
            headers={
                'X-Api-Key': os.getenv("FIRERAVEN_GUARDRAILS_API_KEY"),
                'Content-Type': 'application/json'
            },
            json={
                'messages_history': messages,
                'guardrails': [
                    {
                        "type": "policies_guardrail"
                    },
                    {
                        "type": "security_guardrail"
                    }
                ]
            }
            # Request format
            # {
            #     "messages_history": [
            #         {
            #             "role": "system",
            #             "content": "You are a helpful agent"
            #         },
            #         {
            #             "role": "user",
            #             "content": "What is the weather today?"
            #         },
            #         {
            #             "role": "assistant",
            #             "content": "The weather is 30"
            #         },
            #         {
            #             "role": "user",
            #             "content": "And what about tomorrow?"
            #         }
            #     ],
            #     "guardrails": [
            #         {
            #             "type": "security_guardrail"
            #         },
            #         {
            #             "type": "policies_guardrail"
            #         }
            #     ]
            # } 
        )

        # Check if request was successful
        if not response.ok:
            raise Exception(f"API error: {response.status_code} {response.text}")

        # Parse response data
        input_guardrails_data = response.json()
        
        print('Input Guardrails Response:', input_guardrails_data, "\n\n--\n\n")

        # Response format:
        # {
        #     "input_request": {
        #         "id": "string",
        #         "role": "user",
        #         "content": {
        #             "text": "string",
        #             "processed": "string"
        #         }
        #     },
        #     "security_guardrail_results": {
        #         "value": 0,
        #         "is_safe": true,
        #         "timestamp": "string"
        #     },
        #     "policies_guardrail_results": {
        #         "policies": [
        #             {
        #                 "id": "string",
        #                 "name": "string",
        #                 "description": "string",
        #                 "criticality": "LOW",
        #                 "detection_threshold": 0,
        #                 "detection_is_above_threshold": true,
        #                 "is_default": true,
        #                 "is_archived": true,
        #                 "created_at": "string",
        #                 "updated_at": "string",
        #                 "archived_at": "string",
        #                 "status": "success",
        #                 "value": 0,
        #                 "is_safe": true
        #             }
        #         ],
        #         "is_safe": true,
        #         "timestamp": "string"
        #     }
        # }

        # Check if any policy results indicate blocking (in this case, only for criticality HIGH or CRITICAL)
        criticality_levels_to_block = ['CRITICAL', 'HIGH']
        policies_guardrail_is_safe = True
        security_guardrail_is_safe = True
        # Check if policies_guardrail_results exist
        if input_guardrails_data['policies_guardrail_results']:
            # If any policy result has criticality in the block list and is_safe is false, then the request is blocked
            for policy_result in input_guardrails_data['policies_guardrail_results']['policies']:
                criticality = policy_result['criticality']
                is_safe = policy_result['is_safe']
                if not is_safe and criticality in criticality_levels_to_block:
                    policies_guardrail_is_safe = False
                    break
        # Check if security_guardrail_results exist
        if input_guardrails_data['security_guardrail_results']:
            security_guardrail_is_safe = input_guardrails_data['security_guardrail_results']['is_safe']
        
        # Create a reponse object for convenience (could contain more fields if needed)
        input_guardrails_response = {
            # Save the input ID (will be useful to call the Output Guardrails)
            "input_id": input_guardrails_data['input_request']['id'],
            # Check if the security guardrail and policies guardrail both marked the input as safe
            "is_safe": security_guardrail_is_safe and policies_guardrail_is_safe
        }
        
        return input_guardrails_response
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to check input guardrail: {str(e)}")
