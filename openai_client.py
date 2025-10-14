import openai
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from fireguard_create_conversation import create_conversation
from fireguard_input_guardrail import check_input_guardrail
from fireguard_output_guardrail import check_output_guardrail

# Load environment variables from .env file
load_dotenv()


class OpenAIClient:
    """
    A simple OpenAI client connected to FireGuard and keeping the conversation history during execution.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the OpenAI client and FireGuard conversation.
        
        Args:
            api_key: OpenAI API key.
        """

        self.client = openai.OpenAI(api_key=api_key)
        self.messages: List[Dict[str, str]] = []
        self.model = "gpt-5-nano"

        # FireGuard - Create conversation
        self.conversation_id = create_conversation(
            name="OpenAI Chat Session",
            description="Chat session with OpenAI assistant"
        )
        
        # Set default system prompt
        self.add_message("system", "You are a helpful assistant.")
    

    def add_message(self, role: str, content: str):
        """
        Add a message to the conversation history.
        
        Args:
            role: "user", "assistant", or "system"
            content: The message content
        """
        self.messages.append({"role": role, "content": content})
    

    def get_response(self, user_input: str) -> str:
        """
        Get a response from OpenAI API based on user input.
        Maintains conversation history.
        Inputs and outputs are checked against FireGuard guardrails.
        
        Args:
            user_input: The user's input message
            
        Returns:
            The assistant's response
        """

        # Input Guardrail
        input_guardrails_data = check_input_guardrail(
            self.conversation_id,
            self.messages + [{"role": "user", "content": user_input}]
        )

        # If input is blocked by guardrails, return a message
        if not input_guardrails_data.get("allowed", True):
            return "Input blocked by input guardrail."

        try:
            # Add user message to history
            self.add_message("user", user_input)

            # Make API call
            response = self.client.responses.create(
                model=self.model,
                input=self.messages,
            )
            
            # Extract assistant's response
            assistant_response = response.output_text

            # Output Guardrail
            apology_message = "Sorry, I can't answer your request as it goes against my policies."
            # Configure criticality levels to block
            criticality_levels_to_block = ['CRITICAL', 'HIGH']

            output_guardrails_data = check_output_guardrail(
                self.conversation_id,
                input_guardrails_data.get('input_id'),
                assistant_response
            )

            # Check if any metric results indicate blocking
            # If any metric result has criticality in the block list and isIssue is true, block the response
            should_block = False
            for metric_result in output_guardrails_data.get('metricResults', []):
                metric = metric_result.get('metric', {}) or {}
                criticality = metric.get('criticality')
                is_issue = metric_result.get('isIssue') is True
                if criticality in criticality_levels_to_block and is_issue:
                    should_block = True
                    break

            if should_block:
                self.add_message("assistant", apology_message)
                return apology_message

            # Add assistant's response to history (not blocked)
            self.add_message("assistant", assistant_response)
            return assistant_response
            
        except Exception as e:
            error_msg = f"Error calling OpenAI API: {str(e)}"
            print(f"Error: {error_msg}")
            return error_msg
    
