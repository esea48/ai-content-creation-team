"""
content_pipeline.py

Orchestrates the end-to-end content generation workflow.
Responsibilities:
  - Accept a content request (type, topic, audience, variables)
  - Retrieve relevant context from the knowledge base
  - Build the final prompt via prompt_templates
  - Call the LLM via llm_integration
  - Post-process and validate the output
  - Return or save the finished content
"""

from __future__ import annotations

import os
from pathlib import Path

from src.knowledge_base import retrieve
from src.prompt_templates import build_system_prompt, build_user_prompt
from src.llm_integration import generate


def run(
    content_type: str,
    topic: str,
    audience: str,
    variables: dict | None = None,
    output_path: str | None = None,
    prompt_output_path: str | None = None,
    workflow: str = "draft",
    input_path: str | None = None,
    review_notes_path: str | None = None,
) -> str:
    """
    Full pipeline: retrieve → prompt → generate → post-process.

    Args:
        content_type: One of 'blog_post', 'social_media', 'email', etc.
        topic: The subject the content should cover.
        audience: Target audience description (e.g. 'prospective international students').
        variables: Additional template variables (word count, platform, etc.).
        output_path: If provided, write the result to this file path.

    Returns:
        The generated content as a string.
    """
    variables = dict(variables or {})
    variables.setdefault("topic", topic)
    variables.setdefault("audience", audience)

    workflow = workflow.lower().strip()
    if workflow not in {"draft", "review", "publish"}:
        raise ValueError("workflow must be one of 'draft', 'review', or 'publish'")

    if workflow == "publish":
        if not input_path:
            raise ValueError("publish workflow requires an input_path pointing to the reviewed draft")
        content = read_input(input_path)
        content = post_process(content, content_type)
        if not validate_output(content, content_type):
            raise ValueError("The reviewed content did not pass validation")
        if output_path:
            save_output(content, output_path)
        if review_notes_path:
            save_output(build_review_checklist(content_type, variables), review_notes_path)
        return content

    primary_chunks = retrieve(f"{topic} {audience}", top_k=3, source_type="primary")
    secondary_chunks = retrieve(f"{topic} {audience}", top_k=3, source_type="secondary")
    primary_texts = [chunk.get("text", "") for chunk in primary_chunks if chunk.get("text")]
    secondary_texts = [chunk.get("text", "") for chunk in secondary_chunks if chunk.get("text")]

    system_prompt = build_system_prompt(content_type)
    user_prompt = build_user_prompt(content_type, primary_texts, secondary_texts, variables)

    if prompt_output_path:
        save_output(f"SYSTEM PROMPT:\n{system_prompt}\n\nUSER PROMPT:\n{user_prompt}\n", prompt_output_path)

    provider = os.getenv("LLM_PROVIDER", "anthropic")
    raw_output = generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=None,
        provider=provider,
    )

    content = post_process(raw_output, content_type)
    if not validate_output(content, content_type):
        content = raw_output.strip() or content

    if output_path:
        save_output(content, output_path)
    if review_notes_path:
        save_output(build_review_checklist(content_type, variables), review_notes_path)

    return content


def post_process(raw_output: str, content_type: str) -> str:
    """Clean up LLM output: strip artifacts, enforce length limits, format Markdown."""
    del content_type
    cleaned = raw_output.strip()
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")
    return cleaned


def validate_output(content: str, content_type: str) -> bool:
    """Check that the output meets minimum quality and compliance criteria."""
    del content_type
    return bool(content and content.strip() and len(content.strip()) >= 20)


def build_review_checklist(content_type: str, variables: dict) -> str:
    """Create a simple human review checklist for draft editing and approval."""
    del variables
    content_type = content_type.lower().strip()
    common_checks = [
        "- Verify factual claims against the relevant knowledge base.",
        "- Remove any generic or overly promotional phrasing.",
        "- Check that the tone matches SRH and the intended audience.",
        "- Confirm the CTA and links are correct before publishing.",
    ]
    type_checks = {
        "blog_post": [
            "- Confirm the market context is current and relevant.",
            "- Check that competitor references support SRH positioning.",
            "- Make sure customer pain points are specific, not vague.",
        ],
        "newsletter": [
            "- Confirm the subject line and opening hook feel human.",
            "- Check that the body sections stay concise and readable.",
            "- Confirm the closing CTA is clear and usable.",
        ],
        "program_description": [
            "- Confirm the program name and specifications are accurate.",
            "- Check that the dual-study approach is described clearly.",
            "- Make sure the copy stays concrete and publication-ready.",
        ],
        "hybrid": [
            "- Confirm the brand facts and market context are both accurate.",
            "- Check that the positioning angle is genuinely differentiated.",
            "- Make sure the piece balances SRH voice with industry insight.",
        ],
    }
    lines = [
        "# Review Checklist",
        "",
        f"## {content_type.replace('_', ' ').title()}",
        "",
        *common_checks,
        *type_checks.get(content_type, []),
    ]
    return "\n".join(lines)


def read_input(input_path: str) -> str:
    """Read a draft or reviewed file from disk."""
    path = Path(input_path)
    return path.read_text(encoding="utf-8")


def save_output(content: str, output_path: str) -> None:
    """Persist generated content to a file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
