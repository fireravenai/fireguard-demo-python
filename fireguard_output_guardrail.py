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
            f"https://api.fireraven.ai/public/safeguard/output?conversationId={conversation_id}",
            headers={
                'X-Api-Key': os.getenv("FIRERAVEN_GUARDRAILS_API_KEY"),
                'Content-Type': 'application/json'
            },
            json={
                'inputId': input_id,
                'output': output
            }
        )
        
        # Check if request was successful
        if not response.ok:
            raise Exception(f"API error: {response.status_code} {response.text}")

        # Parse response data
        output_guardrails_data = response.json()
        
        return output_guardrails_data
        
        # Response data format:
        # {
        #   id: '00000000-0000-0000-0000-000000000000,
        #   inputMessage: {
        #     id: '00000000-0000-0000-0000-000000000000',
        #     direction: 'Outgoing',
        #     status: 'Saved',
        #     content: {
        #       text: 'original user message text',
        #       processed: 'message with context from previous messages'
        #     }
        #   },
        #   outputMessage: {
        #     id: '00000000-0000-0000-0000-000000000000',
        #     direction: 'Incoming',
        #     status: 'Saved',
        #     content: {
        #       text: 'original assistant message text',
        #       processed: null
        #     }
        #   },
        #   metricResults: [
        #     {
        #       metric: {
        #         id: '00000000-0000-0000-0000-000000000000',
        #         name: 'Policy 1',
        #         description: 'Policy description',
        #         criticality: 'CRITICAL',
        #         detectionThreshold: 0.1,
        #         detectionIsAboveThreshold: true,
        #         isDefault: false,
        #         isArchived: false,
        #         createdAt: '0000-00-00T00:00:00.000Z',
        #         updatedAt: '0000-00-00T00:00:00.000Z',
        #         archivedAt: null
        #       },
        #       status: 'SUCCESS',
        #       value: 0.9546173468312323,
        #       isIssue: true
        #     },
        #     ...
        #   ],
        #   createdAt: '0000-00-00T00:00:00.000Z'
        # }
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to check output guardrail: {str(e)}")