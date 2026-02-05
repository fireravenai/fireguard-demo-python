#!/usr/bin/env python3
"""
FireGuard output guardrail
This module provides a function to check output messages using the Fireraven guardrail API.
"""

import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

from config import API_FIRERAVEN_URL

# Load environment variables from .env file
load_dotenv()


def check_output_guardrail(conversation_id: str, input_id: str, output: str) -> Dict[str, Any]:
    """
    Check output messages using Fireraven guardrail API.
    
    Args:
        conversation_id: The conversation ID from FireGuard
        input_id: The input ID from the FireGuard input guardrail response
        output: The output message text to check
        
    Returns:
        dict: Guardrail response data containing metric results and analysis
        
    Raises:
        Exception: If API request fails
    """
    
    try:
        response = requests.post(
            f"{API_FIRERAVEN_URL}/public/fireguard/v1.1/output_guardrails?conversation_id={conversation_id}",
            headers={
                'X-Api-Key': os.getenv("FIRERAVEN_GUARDRAILS_API_KEY"),
                'Content-Type': 'application/json'
            },
            json={
                'input_id': input_id,
                'output': output,
                "guardrails": [
                    {
                        "type": "policies_guardrail"
                    },
                    {
                        "type": "security_guardrail"
                    }
                ]
            }
        )
        # Request format
        # {
        #     "input_id": "00000000-0000-0000-0000-000000000000",
        #     "output": "The weather forecast is 24C with a mix of sun and cloud for the day.",
        #     "guardrails": [
        #         {
        #             "type": "security_guardrail"
        #         },
        #         {
        #             "type": "policies_guardrail"
        #         }
        #     ]
        # }
        
        # Check if request was successful
        if not response.ok:
            raise Exception(f"API error: {response.status_code} {response.text}")

        # Parse response data
        output_guardrails_data = response.json()

        print('Output Guardrails Response:', output_guardrails_data, "\n\n--\n\n")

        # Response format:
        # {
        #     "output_request": {
        #         "id": "string",
        #         "role": "user",
        #         "content": {
        #             "text": "string"
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
        policies_results = output_guardrails_data.get('policies_guardrail_results')
        if policies_results and policies_results.get('policies'):
            # If any policy result has criticality in the block list and is_safe is false, then the response is blocked
            for policy_result in policies_results['policies']:
                criticality = policy_result['criticality']
                is_safe = policy_result['is_safe']
                if not is_safe and criticality in criticality_levels_to_block:
                    policies_guardrail_is_safe = False
                    break
        # Check if security_guardrail_results exist
        security_results = output_guardrails_data.get('security_guardrail_results')
        if security_results:
            security_guardrail_is_safe = security_results.get('is_safe', True)
        
        # Create a reponse object for convenience (could contain more fields if needed)
        output_guardrails_response = {
            # Check if the security guardrail and policies guardrail both marked the output as safe
            "is_safe": security_guardrail_is_safe and policies_guardrail_is_safe,
            "policies_guardrail_is_safe": policies_guardrail_is_safe,
            "security_guardrail_is_safe": security_guardrail_is_safe
        }
        
        return output_guardrails_response

        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to check output guardrail: {str(e)}")
