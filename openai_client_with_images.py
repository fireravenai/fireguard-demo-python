#!/usr/bin/env python3
"""
OpenAI client with FireGuard (input images + text support).
"""

import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional

import openai
from dotenv import load_dotenv

from fireguard_create_conversation import create_conversation
from fireguard_input_guardrail_with_images import check_input_guardrail_with_images
from fireguard_output_guardrail import check_output_guardrail

# Load environment variables from .env file
load_dotenv()


class OpenAIClientWithImages:
    """
    OpenAI client connected to FireGuard.
    Supports user input as text + optional image.
    """

    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.messages: List[Dict[str, str]] = []
        self.model = "gpt-5-nano"
        self.last_run: Dict[str, Any] = {}

        self.conversation_id = create_conversation(
            name="OpenAI Image Chat Session",
            description="Chat session with text and images",
        )
        self.add_message("system", "You are a helpful assistant.")

    def add_message(self, role: str, content: str):
        """Add a text message to history used by FireGuard messages_history."""
        self.messages.append({"role": role, "content": content})

    @staticmethod
    def _image_to_data_url(image_path: str) -> str:
        """Convert a local image to a data URL for OpenAI input_image."""
        path = Path(image_path)
        if not path.exists() or not path.is_file():
            raise ValueError(f"Image not found: {image_path}")

        mime_type, _ = mimetypes.guess_type(path.name)
        if not mime_type or not mime_type.startswith("image/"):
            raise ValueError(f"Unsupported or unknown image MIME type: {path.name}")

        with path.open("rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"

    def get_response(
        self,
        user_input: str,
        image_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get an assistant response from text + optional image.
        Runs FireGuard input/output guardrails.
        """
        pending_messages = self.messages + [{"role": "user", "content": user_input}]

        input_guardrails = check_input_guardrail_with_images(
            conversation_id=self.conversation_id,
            messages=pending_messages,
            image_path=image_path,
        )

        if not input_guardrails.get("is_safe", True):
            if not input_guardrails.get("security_guardrail_is_safe", True):
                blocked_message = "Input blocked by security guardrail."
            else:
                blocked_message = "Input blocked by policies guardrail."

            self.last_run = {
                "conversation_id": self.conversation_id,
                "input_guardrails": input_guardrails,
                "assistant_output": blocked_message,
                "output_guardrails": None,
            }
            return self.last_run

        self.add_message("user", user_input)

        user_content: List[Dict[str, str]] = [{"type": "input_text", "text": user_input}]
        if image_path:
            user_content.append(
                {
                    "type": "input_image",
                    "image_url": self._image_to_data_url(image_path),
                }
            )

        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_content},
            ],
        )
        assistant_response = response.output_text

        output_guardrails = check_output_guardrail(
            conversation_id=self.conversation_id,
            input_id=input_guardrails.get("input_id"),
            output=assistant_response,
        )

        if not output_guardrails.get("is_safe", True):
            if not output_guardrails.get("security_guardrail_is_safe", True):
                assistant_response = "Sorry, I can't answer your request (security guardrail)."
            else:
                assistant_response = "Sorry, I can't answer your request as it goes against my policies."

        self.add_message("assistant", assistant_response)
        self.last_run = {
            "conversation_id": self.conversation_id,
            "input_guardrails": input_guardrails,
            "assistant_output": assistant_response,
            "output_guardrails": output_guardrails,
        }
        return self.last_run
