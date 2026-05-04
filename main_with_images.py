#!/usr/bin/env python3
"""
Demo main file for OpenAI + FireGuard using text and a hardcoded image.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from openai_client_with_images import OpenAIClientWithImages

# Load environment variables from .env file
load_dotenv()


def main():
    """
    Run a single demo call with hardcoded sample text and image path.
    Edit HARDCODED_IMAGE_FILENAME to switch image files.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found.")
        return

    images_folder = Path("images_guardrails")
    hardcoded_image_filename = "image-patient-data-and-jailbreak.png"
    image_path = images_folder / hardcoded_image_filename

    sample_text = "Please analyze this image and summarize what you see."

    print("=== FireGuard + OpenAI image demo ===")
    print(f"Image path: {image_path}")
    print(f"User text: {sample_text}\n")

    try:
        client = OpenAIClientWithImages(api_key=api_key)
        result = client.get_response(
            user_input=sample_text,
            image_path=str(image_path),
        )

        print("Conversation ID:", result.get("conversation_id"))
        print("\nInput guardrails summary:")
        print(
            {
                "is_safe": result.get("input_guardrails", {}).get("is_safe"),
                "policies_guardrail_is_safe": result.get("input_guardrails", {}).get(
                    "policies_guardrail_is_safe"
                ),
                "security_guardrail_is_safe": result.get("input_guardrails", {}).get(
                    "security_guardrail_is_safe"
                ),
                "input_id": result.get("input_guardrails", {}).get("input_id"),
            }
        )

        print("\nAssistant output:")
        print(result.get("assistant_output"))

        if result.get("output_guardrails") is not None:
            print("\nOutput guardrails summary:")
            print(result.get("output_guardrails"))

    except Exception as e:
        print(f"Error during execution: {str(e)}")


if __name__ == "__main__":
    main()
