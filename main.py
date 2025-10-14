#!/usr/bin/env python3
"""
Main file for FireGuard demo using OpenAI API with a command-line interaction.
"""

import os
import sys
from dotenv import load_dotenv
from openai_client import OpenAIClient

# Load environment variables from .env file
load_dotenv()


def main():
    """Main function to run the chat interface."""
    print("Type your message and press Enter to chat with the AI!")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found.")
        return
    
    try:
        # Initialize OpenAI client
        client = OpenAIClient(api_key=api_key)
        
        # Main chat loop
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                # Handle empty input
                if not user_input:
                    continue
                
                # Handle quit command
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    break
                
                # Get AI response
                print("AI: ", end="", flush=True)
                response = client.get_response(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Please try again.")
    
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {str(e)}")
        return


if __name__ == "__main__":
    main()
