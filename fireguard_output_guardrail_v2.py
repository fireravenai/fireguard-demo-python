#!/usr/bin/env python3
"""
FireGuard output guardrail
This module provides a function to check output messages using the Fireraven guardrail API.
"""

import os
import requests
import time
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def check_output_guardrail_v2(conversation_id: str, input_id: str, output: str) -> Dict[str, Any]:
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

    print(output)
    
    try:
        response = requests.post(
            f"https://api.dev.fireravenmailbox.com/public/fireguard/v1.1/output_guardrails?conversation_id={conversation_id}",
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
        #             "type": "policies_guardrail"
        #         }
        #     ]
        # }
        
        # Check if request was successful
        if not response.ok:
            raise Exception(f"API error: {response.status_code} {response.text}")

        # Parse response data
        output_guardrails_data = response.json()
        
        print('Output Guardrails Response:', output_guardrails_data['output_request'])
        print('Output Guardrails Response:', output_guardrails_data['policies_guardrail_results'])

        # print('Output Guardrails Response:', output_guardrails_data)
        # Response format:
        # {
        #     "output_request": {
        #         "id": "string",
        #         "role": "user",
        #         "content": {
        #             "text": "string"
        #         }
        #     },
        #     "policies_guardrail_results": {
        #         "policies": [
        #             {
        #                 "id": "string",
        #                 "name": "string",
        #                 "description": "string",
        #                 "criticality": "low",
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
        criticality_levels_to_block = ['critical', 'high']
        # If any policy result has criticality in the block list and is_safe is false, then the response is blocked
        policies_guardrail_is_safe = True
        for policy_result in output_guardrails_data['policies_guardrail_results']['policies']:
            criticality = policy_result['criticality']
            is_safe = policy_result['is_safe']
            if not is_safe and criticality in criticality_levels_to_block:
                policies_guardrail_is_safe = False
                break
        
        # Create a reponse object for convenience (could contain more fields if needed)
        output_guardrails_response = {
            # Check if the policies guardrail marked the input as safe
            "is_safe": policies_guardrail_is_safe
        }
        
        return output_guardrails_response

        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to check output guardrail: {str(e)}")
