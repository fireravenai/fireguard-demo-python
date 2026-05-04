#!/usr/bin/env python3
"""
FireGuard input guardrail with image support.
This module checks input messages and optional image(s) via the Fireraven API.
"""

import os
import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

from config import API_FIRERAVEN_URL

# Load environment variables from .env file
load_dotenv()


def _build_image_payload(image_path: str) -> Dict[str, str]:
    """
    Build a FireGuard-compatible image object from a local file.

    Args:
        image_path: Path to the image file.

    Returns:
        dict: {"base64": "...", "mimeType": "image/...", "name": "..."}
    """
    path = Path(image_path)
    if not path.exists() or not path.is_file():
        raise ValueError(f"Image not found: {image_path}")

    mime_type, _ = mimetypes.guess_type(path.name)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError(f"Unsupported or unknown image MIME type: {path.name}")

    with path.open("rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")

    return {
        "base64": encoded,
        "mimeType": mime_type,
        "name": path.name,
    }


def check_input_guardrail_with_images(
    conversation_id: str,
    messages: List[Dict[str, str]],
    image_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Check input guardrails with optional image support.

    This follows FireGuard v1 docs for multimodal input:
    - messages_history contains text messages only
    - images is a top-level array with base64 + mimeType + optional name

    Args:
        conversation_id: FireGuard conversation ID.
        messages: Conversation history where the last message is the evaluated turn.
        image_path: Optional image file path attached to the current user turn.

    Returns:
        dict: includes high-level safety flags + raw API response.
    """
    payload: Dict[str, Any] = {
        "messages_history": messages,
        "guardrails": [
            {"type": "policies_guardrail"},
            {"type": "security_guardrail"},
        ],
    }

    if image_path:
        payload["images"] = [_build_image_payload(image_path)]

    try:
        response = requests.post(
            f"{API_FIRERAVEN_URL}/public/fireguard/v1/input_guardrails?conversation_id={conversation_id}",
            headers={
                "X-Api-Key": os.getenv("FIRERAVEN_GUARDRAILS_API_KEY"),
                "Content-Type": "application/json",
            },
            json=payload,
        )

        if not response.ok:
            raise Exception(f"API error: {response.status_code} {response.text}")

        input_guardrails_data = response.json()
        print("Input Guardrails Response:", input_guardrails_data, "\n\n--\n")

        policies_guardrail_is_safe = True
        security_guardrail_is_safe = True

        policies_results = input_guardrails_data.get("policies_guardrail_results")
        if policies_results:
            policies_guardrail_is_safe = policies_results.get("is_safe", True)

        security_results = input_guardrails_data.get("security_guardrail_results")
        if security_results:
            security_guardrail_is_safe = security_results.get("is_safe", True)

        return {
            "input_id": input_guardrails_data.get("input_request", {}).get("id"),
            "is_safe": policies_guardrail_is_safe and security_guardrail_is_safe,
            "policies_guardrail_is_safe": policies_guardrail_is_safe,
            "security_guardrail_is_safe": security_guardrail_is_safe,
            "raw": input_guardrails_data,
        }

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to check input guardrail with images: {str(e)}")
