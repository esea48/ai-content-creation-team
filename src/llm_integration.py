"""
llm_integration.py

Thin abstraction layer over LLM provider APIs (Anthropic Claude, OpenAI GPT).
Responsibilities:
  - Initialise API clients from environment variables
  - Send chat completion requests with configurable parameters
  - Handle retries, rate limiting, and error responses
  - Support model switching without changing calling code
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter


DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-opus-4-7",
}


def get_client(provider: str = "anthropic"):
    """
    Return an initialised API client for the specified provider.

    Args:
        provider: 'anthropic' or 'openai'
    """
    provider = provider.lower().strip()

    if provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key.startswith("your_"):
            return None
        from anthropic import Anthropic

        return Anthropic(api_key=api_key)

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("your_"):
            return None
        from openai import OpenAI

        return OpenAI(api_key=api_key)

    raise ValueError("provider must be 'anthropic' or 'openai'")


def _fallback_provider(provider: str) -> str:
    if provider.lower().strip() == "openai":
        return "anthropic"
    if provider.lower().strip() == "anthropic":
        return "openai"
    return "anthropic"


def resolve_model(provider: str, model: str | None = None) -> str:
    """
    Resolve the model to use for a provider.

    If a model is explicitly supplied, use it.
    Otherwise prefer a provider-specific env var and then a built-in default.
    """
    if model:
        return model

    provider = provider.lower().strip()
    if provider == "openai":
        return os.getenv("OPENAI_MODEL") or DEFAULT_MODELS["openai"]
    if provider == "anthropic":
        return os.getenv("ANTHROPIC_MODEL") or DEFAULT_MODELS["anthropic"]
    return DEFAULT_MODELS["anthropic"]


def _curl_post_json(url: str, headers: dict[str, str], payload: dict) -> dict:
    """Send a JSON POST request via curl and parse the JSON response."""
    if shutil.which("curl") is None:
        raise RuntimeError("curl is not available on this system")

    command = [
        "curl",
        "--silent",
        "--show-error",
        "--fail",
        "--location",
        "--request",
        "POST",
        url,
    ]
    for name, value in headers.items():
        command.extend(["-H", f"{name}: {value}"])
    command.extend(["--data", json.dumps(payload)])

    result = subprocess.run(command, capture_output=True, text=True, timeout=90)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "curl request failed"
        raise RuntimeError(message)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        preview = result.stdout[:500]
        raise RuntimeError(f"Invalid JSON response: {preview}") from exc


def _generate_via_curl(
    provider: str,
    system_prompt: str,
    user_prompt: str,
    model: str,
    max_tokens: int,
    temperature: float,
) -> str:
    provider = provider.lower().strip()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("your_"):
            raise RuntimeError("OPENAI_API_KEY is missing or placeholder")

        response = _curl_post_json(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            payload={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        return (response["choices"][0]["message"]["content"] or "").strip()

    if provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or api_key.startswith("your_"):
            raise RuntimeError("ANTHROPIC_API_KEY is missing or placeholder")

        response = _curl_post_json(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            payload={
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
        )
        parts = []
        for block in response.get("content", []):
            if isinstance(block, dict):
                text = block.get("text")
                if text:
                    parts.append(text)
        return "".join(parts).strip()

    raise ValueError("provider must be 'anthropic' or 'openai'")


def _fallback_generate(system_prompt: str, user_prompt: str, model: str, provider: str, reason: str = "no API key was configured") -> str:
    _ = system_prompt
    lines = [line.strip() for line in user_prompt.splitlines() if line.strip()]
    topic = "the topic"
    audience = "the audience"
    subject = "Update from SRH University"
    cta = "Learn more"
    language = "english"
    context_lines: list[str] = []
    in_context = False
    newsletter_mode = "newsletter" in user_prompt.lower() or "newsletter" in system_prompt.lower()
    for line in lines:
        lower = line.lower()
        if lower.startswith("topic:"):
            topic = line.split(":", 1)[1].strip() or topic
        elif lower.startswith("audience:"):
            audience = line.split(":", 1)[1].strip() or audience
        elif lower.startswith("subject line:"):
            subject = line.split(":", 1)[1].strip() or subject
        elif lower.startswith("call to action:"):
            cta = line.split(":", 1)[1].strip() or cta
        elif lower.startswith("language:"):
            language = line.split(":", 1)[1].strip().lower() or language
        elif lower.startswith("context:"):
            in_context = True
        elif in_context and ":" in line and line.split(":", 1)[0].lower() in {"topic", "audience", "tone", "word count", "character limit", "include hashtags", "subject line", "recipient", "call to action", "primary cta", "desired length", "angle"}:
            in_context = False
        elif in_context:
            context_lines.append(line)

    context_excerpt = " ".join(context_lines[:2]).strip()
    if not context_excerpt:
        context_excerpt = "Relevant brand and program information from the knowledge base."
    else:
        words = context_excerpt.split()
        context_excerpt = " ".join(words[:30])

    hybrid_mode = "hybrid" in user_prompt.lower() or "hybrid" in system_prompt.lower()
    if newsletter_mode:
        if language == "german":
            return (
                f"## {subject}\n\n"
                f"Liebe {audience},\n\n"
                f"Hier ist ein kurzes Update von SRH University zu {topic}. Wir konzentrieren uns auf das, was wirklich zählt: praxisnahes Lernen, starke Unterstützung und klare Wege in Studium und Karriere.\n\n"
                f"**Was gerade besonders wichtig ist**\n"
                f"- Der Newsletter stützt sich auf die PRIMARY knowledge base und bleibt dadurch faktenbasiert und markenkonform.\n"
                f"- Der SECONDARY Kontext hilft dabei, das Thema im Markt einzuordnen.\n"
                f"- Die Formulierung bleibt konkret und vermeidet generische Marketing-Sprache.\n\n"
                f"**Warum das wichtig ist**\n"
                f"{context_excerpt}\n\n"
                f"{cta}\n\n"
                f"Viele Grüße\n"
                f"Das SRH University Team\n\n"
                f"Draft generiert lokal, weil {reason} für {provider} ({model})."
            )
        return (
            f"## {subject}\n\n"
            f"Dear {audience},\n\n"
            f"Here’s a quick update from SRH University about {topic}. We’re keeping this focused on what matters most: practical learning, strong student support, and clearly defined pathways into study and career outcomes.\n\n"
            f"**What stands out right now**\n"
            f"- The newsletter is grounded in SRH’s PRIMARY knowledge base, so the details stay factual and brand-specific.\n"
            f"- The supporting context helps frame the message with market relevance and audience fit.\n"
            f"- The draft avoids generic marketing language and stays close to the actual SRH story.\n\n"
            f"**Why it matters**\n"
            f"{context_excerpt}\n\n"
            f"{cta}\n\n"
            f"Warm regards,\n"
            f"The SRH University Team\n\n"
            f"Draft generated locally because {reason} for {provider} ({model})."
        )

    if hybrid_mode:
        if language == "german":
            return (
                f"{topic}\n\n"
                f"Für {audience}.\n\n"
                f"**SRH-Perspektive**\n"
                f"SRH verbindet konkrete Programm- und Markenstärken mit einem klaren Blick auf den Markt.\n\n"
                f"**Marktkontext**\n"
                f"{context_excerpt}\n\n"
                f"**Differenzierung**\n"
                f"Die Positionierung bleibt bewusst spezifisch: praxisnah, markenklar und auf relevante Studierendenbedürfnisse ausgerichtet.\n\n"
                f"**Nächster Schritt**\n"
                f"{cta}\n\n"
                f"Draft generiert lokal, weil {reason} für {provider} ({model})."
            )
        return (
            f"{topic}\n\n"
            f"Built for {audience}.\n\n"
            f"**SRH perspective**\n"
            f"SRH combines concrete brand strengths with a clear read on the market.\n\n"
            f"**Industry context**\n"
            f"{context_excerpt}\n\n"
            f"**Differentiation**\n"
            f"The positioning stays specific: practical, brand-led, and aligned with what the audience actually needs.\n\n"
            f"**Next step**\n"
            f"{cta}\n\n"
            f"Draft generated locally because {reason} for {provider} ({model})."
        )

    if language == "german":
        return (
            f"{topic}\n\n"
            f"Für {audience}.\n\n"
            f"Wichtiger Kontext: {context_excerpt}\n\n"
            f"Draft generiert lokal, weil {reason} für {provider} ({model})."
        )

    return (
        f"{topic}\n\n"
        f"Aimed at {audience}.\n\n"
        f"Key context used: {context_excerpt}\n\n"
        f"Draft generated locally because {reason} for {provider} ({model})."
    )


def generate(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    max_tokens: int = 2048,
    temperature: float = 0.7,
    provider: str = "anthropic",
) -> str:
    """
    Send a prompt to the LLM and return the text response.

    Args:
        system_prompt: Instructions that define the assistant's role and constraints.
        user_prompt: The specific request, including injected context.
        model: Model identifier string.
        max_tokens: Maximum tokens in the completion.
        temperature: Sampling temperature (0 = deterministic, 1 = creative).
        provider: 'anthropic' or 'openai'.

    Returns:
        The model's text response.
    """
    providers_to_try = [provider, _fallback_provider(provider)]
    last_error: Exception | None = None
    last_reason = "no API key was configured"

    for current_provider in providers_to_try:
        try:
            current_model = model if current_provider == provider and model else resolve_model(current_provider)
            return _generate_via_curl(
                current_provider,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=current_model,
                max_tokens=max_tokens,
                temperature=temperature,
            )

        except Exception as exc:  # pragma: no cover - provider/network failures
            last_error = exc
            last_reason = f"the API request failed with {exc.__class__.__name__}"
            print(f"LLM provider error ({current_provider}): {exc.__class__.__name__}: {exc}", file=sys.stderr)
            continue

    if last_error is not None:
        return _fallback_generate(system_prompt, user_prompt, resolve_model(provider, model), provider, reason=last_reason)

    return _fallback_generate(system_prompt, user_prompt, resolve_model(provider, model), provider, reason=last_reason)


def count_tokens(text: str, model: str = "claude-opus-4-7") -> int:
    """Estimate token count for a string (useful for chunking and cost tracking)."""
    _ = model
    words = re.findall(r"\w+|[^\w\s]", text)
    return max(1, int(len(words) * 1.2))
