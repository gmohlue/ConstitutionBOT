"""Message normalization utilities for LLM providers."""

from typing import Literal

MessageRole = Literal["user", "assistant", "system"]


def validate_messages(messages: list[dict]) -> list[dict]:
    """Validate and clean message list.

    Args:
        messages: List of message dicts with 'role' and 'content' keys

    Returns:
        List of validated messages with only 'role' and 'content' keys
    """
    validated = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")
        if role in ("user", "assistant", "system") and content:
            validated.append({
                "role": role,
                "content": str(content),
            })
    return validated


def ensure_alternating_messages(messages: list[dict]) -> list[dict]:
    """Ensure messages alternate between user and assistant.

    Claude API requires alternating user/assistant messages.
    This function merges consecutive same-role messages.

    Args:
        messages: List of validated messages

    Returns:
        List with alternating roles
    """
    if not messages:
        return []

    cleaned = []
    last_role = None

    for msg in messages:
        if msg["role"] == "system":
            continue  # Skip system messages in the message list

        if msg["role"] != last_role:
            cleaned.append(msg.copy())
            last_role = msg["role"]
        else:
            # Merge consecutive same-role messages
            cleaned[-1]["content"] += "\n\n" + msg["content"]

    return cleaned


def ensure_starts_with_user(messages: list[dict]) -> list[dict]:
    """Ensure conversation starts with a user message.

    Claude API requires conversations to start with user message.

    Args:
        messages: List of messages

    Returns:
        List starting with user message
    """
    if not messages:
        return []

    if messages[0]["role"] != "user":
        return [{"role": "user", "content": "Hello"}] + messages

    return messages


def normalize_for_anthropic(messages: list[dict]) -> list[dict]:
    """Normalize messages for Anthropic Claude API.

    - Removes system messages from list (should be passed separately)
    - Ensures alternating user/assistant
    - Ensures starts with user

    Args:
        messages: Raw message list

    Returns:
        Normalized message list for Claude
    """
    validated = validate_messages(messages)
    alternating = ensure_alternating_messages(validated)
    return ensure_starts_with_user(alternating)


def normalize_for_openai(messages: list[dict], system_prompt: str | None = None) -> list[dict]:
    """Normalize messages for OpenAI API.

    OpenAI expects system message as first message in the list.

    Args:
        messages: Raw message list
        system_prompt: Optional system prompt to prepend

    Returns:
        Normalized message list for OpenAI
    """
    validated = validate_messages(messages)
    result = []

    # Add system message first if provided
    if system_prompt:
        result.append({"role": "system", "content": system_prompt})

    # Add remaining messages (filter out any system messages as they should be first)
    for msg in validated:
        if msg["role"] != "system":
            result.append(msg)

    return result


def normalize_for_ollama(messages: list[dict], system_prompt: str | None = None) -> list[dict]:
    """Normalize messages for Ollama API.

    Ollama follows OpenAI-style format with system message first.

    Args:
        messages: Raw message list
        system_prompt: Optional system prompt to prepend

    Returns:
        Normalized message list for Ollama
    """
    return normalize_for_openai(messages, system_prompt)
