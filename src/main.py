"""
main.py

CLI entry point for the SRH University AI Content Creator.
Usage:
  python -m src.main --type blog_post --topic "Applied AI programs" --audience "prospective students"

Responsibilities:
  - Parse command-line arguments
  - Load environment variables from .env
  - Optionally rebuild the knowledge base index
  - Invoke the content pipeline
  - Print or save the result
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from src.content_pipeline import run
from src.knowledge_base import refresh_index


AUDIENCE_CHOICES = (
    "prospective_students",
    "current_students",
    "parents",
    "employers",
    "alumni",
    "press",
)

TONE_CHOICES = (
    "professional",
    "approachable",
    "inspiring",
    "informative",
)

VOICE_CHOICES = (
    "brand_aligned",
    "conversational",
    "authoritative",
    "supportive",
)

LANGUAGE_CHOICES = (
    "english",
    "german",
)


def parse_args() -> argparse.Namespace:
    """Define and parse CLI arguments."""
    parser = argparse.ArgumentParser(description="SRH University AI Content Creator")
    parser.add_argument(
        "--type",
        required=True,
        choices=("blog_post", "newsletter", "program_description", "hybrid"),
        help="Content type",
    )
    parser.add_argument(
        "--workflow",
        choices=("draft", "review", "publish"),
        default="draft",
        help="Workflow stage to run",
    )
    parser.add_argument("--topic", required=True, help="Topic to write about")
    audience_help = (
        "Target audience (prospective_students, current_students, parents, "
        "employers, alumni, press)"
    )

    parser.add_argument(
        "--audience",
        required=True,
        choices=AUDIENCE_CHOICES,
        help=audience_help,
    )
    parser.add_argument(
        "--tone",
        choices=TONE_CHOICES,
        default="professional",
        help="Tone preference (professional, approachable, inspiring, informative)",
    )
    parser.add_argument(
        "--voice",
        choices=VOICE_CHOICES,
        default="brand_aligned",
        help="Voice preference (brand_aligned, conversational, authoritative, supportive)",
    )
    parser.add_argument(
        "--language",
        choices=LANGUAGE_CHOICES,
        default="english",
        help="Content language (english or german)",
    )
    parser.add_argument("--program-name", help="Program name for program descriptions")
    parser.add_argument("--output", help="Optional path to save the output")
    parser.add_argument("--input", help="Reviewed draft to publish in publish workflow")
    parser.add_argument("--prompt-output", help="Optional path to save the assembled prompt")
    parser.add_argument("--review-notes", help="Optional path to save a review checklist")
    parser.add_argument("--refresh-kb", action="store_true", help="Rebuild the knowledge base index")
    return parser.parse_args()


def main() -> None:
    """Load config, run the pipeline, and output the result."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)
    args = parse_args()

    if os.getenv("LLM_PROVIDER", "openai").lower().strip() == "openai":
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "").startswith("your_"):
            print("Warning: OPENAI_API_KEY is missing or still a placeholder, so the app will use the local fallback.", file=sys.stderr)
    else:
        if not os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY", "").startswith("your_"):
            print("Warning: ANTHROPIC_API_KEY is missing or still a placeholder, so the app will use the local fallback.", file=sys.stderr)

    if getattr(args, "refresh_kb", False):
        refresh_index("knowledge_base")

    audience_label = args.audience.replace("_", " ")

    content = run(
        content_type=args.type,
        topic=args.topic,
        audience=audience_label,
        variables={
            "program_name": args.program_name or args.topic,
            "tone": args.tone,
            "voice": args.voice,
            "language": args.language,
        },
        output_path=getattr(args, "output", None),
        prompt_output_path=getattr(args, "prompt_output", None),
        workflow=getattr(args, "workflow", "draft"),
        input_path=getattr(args, "input", None),
        review_notes_path=getattr(args, "review_notes", None),
    )

    print(content)


if __name__ == "__main__":
    main()
