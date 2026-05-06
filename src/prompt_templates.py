"""
prompt_templates.py

Centralised library of prompt templates for each content type.
Responsibilities:
  - Provide structured system and user prompts for blog posts, social media, emails, etc.
  - Inject retrieved context (RAG chunks) and user-supplied variables into templates
  - Enforce SRH University tone, brand voice, and compliance guardrails
"""

from __future__ import annotations

from collections import defaultdict


# Shared prompt layers keep the brand rules in one place and reduce duplication
# across the output-specific templates below.
TONE_LABELS = {
    "professional": "formal, authoritative, and precise",
    "approachable": "warm, conversational, and encouraging",
    "inspiring": "motivational, aspirational, and energetic",
    "informative": "factual, clear, and educational",
}

VOICE_LABELS = {
    "brand_aligned": "clearly SRH, grounded, and specific",
    "conversational": "natural, readable, and human",
    "authoritative": "confident, expert, and measured",
    "supportive": "empathetic, audience-aware, and reassuring",
}

LANGUAGE_LABELS = {
    "english": "English",
    "german": "German",
}

SOURCE_OF_TRUTH_RULES = """
- Use the PRIMARY knowledge base as the source of truth.
- Use the SECONDARY knowledge base only as supporting context.
"""

SRH_BRAND_VOICE_RULES = """
- Reference product specifications accurately.
- Use SRH-specific terminology naturally.
- Avoid generic AI marketing language.
"""


BLOG_POST_ROLE = """
You are a content strategist for SRH University.

Use the PRIMARY knowledge base as the source of truth for SRH facts.
Use the SECONDARY knowledge base for market context, competitor signals, and audience pain points.

Write a blog post that feels strategic, credible, and clearly tied to SRH’s positioning in the market.
"""

BLOG_POST_STRUCTURE = """
Required structure:
- Open with a specific market trend, challenge, or audience need
- Show SRH’s point of view on that issue
- Include 2 to 3 body sections with concrete SRH facts and proof points
- Include a short competitor or market contrast section
- Close with a clear takeaway that reinforces SRH’s positioning
"""

BLOG_POST_GUIDELINES = """
Content requirements:
- Use both knowledge bases, but keep SRH facts grounded in PRIMARY
- Include concrete examples, not vague claims
- Make the differentiation explicit
- Show why SRH is a better fit than a generic alternative
- Use named facts, programme details, partnerships, or outcomes where relevant

Style rules:
- Avoid generic marketing language such as "cutting-edge," "world-class," or "innovative"
- Avoid filler openings like "In today’s fast-changing world"
- Prefer clear, direct, human language
- Write like SRH, not like a generic higher-education blog

Brand requirements:
{source_rules}
{brand_voice_rules}
- Language: {language_label}
- Tone: {tone_label}
- Voice: {voice_label}
- Keep the analysis specific, credible, useful, and publication-ready.
- Make the piece feel informed, practical, and distinctively SRH.
"""

NEWSLETTER_ROLE = """
You are a newsletter writer for SRH University.

Use the PRIMARY knowledge base as the source of truth.
Use the SECONDARY knowledge base only when it adds market context, relevance, or credibility.

Write a newsletter that is concrete, human, clearly branded, and suitable for publishing.
"""

NEWSLETTER_STRUCTURE = """
Required structure:
- A short opening hook that sounds human and relevant
- 2 to 3 concise body sections that use concrete SRH facts from the PRIMARY knowledge base
- One short support/credibility section that can reference SECONDARY context if helpful
- A clear closing call to action
"""

NEWSLETTER_GUIDELINES = """
Content requirements:
- Include specific SRH proof points, not generic claims
- Use at least one concrete detail from the PRIMARY knowledge base in each body section where possible
- If market context is included, make sure it sharpens SRH's positioning
- Show why SRH is different, not just what SRH offers

Style rules:
- Avoid generic marketing phrases such as "unlock your future" or "world-class"
- Use the CORE principle only if it is relevant and factual
- Prefer specific details over broad claims
- Keep the tone warm, concise, and informative
- Write like SRH, not like a generic university brochure

Brand requirements:
{source_rules}
{brand_voice_rules}
- Language: {language_label}
- Tone: {tone_label}
- Voice: {voice_label}
- Make the copy feel real, human, and publication-ready
- Use the SECONDARY knowledge base to support differentiation, not to dominate the message.
"""

PROGRAM_DESCRIPTION_ROLE = """
You are a program copywriter for SRH University.

Use the PRIMARY knowledge base as the source of truth.
Use the SECONDARY knowledge base only when it helps with positioning or relevance.

Write a program description that is accurate, human, persuasive, and clearly branded for SRH.
"""

PROGRAM_DESCRIPTION_STRUCTURE = """
Structure:
- A short opening paragraph that states the value proposition clearly
- 3 to 5 benefit-focused sections or bullets
- A short closing call to action

Tone: Informative, confident, and student-friendly
"""

PROGRAM_DESCRIPTION_GUIDELINES = """
Content requirements:
- Lead with the program’s practical value for students
- Include concrete programme details from the PRIMARY knowledge base
- Mention SRH’s dual-study approach clearly when relevant
- Show how the program supports career relevance and student outcomes
- Include differentiation where it is factual and useful

Brand requirements:
{source_rules}
{brand_voice_rules}
- Language: {language_label}
- Tone: {tone_label}
- Voice: {voice_label}
- Keep the writing concrete, specific, non-generic, and publication-ready
- Make it sound like SRH, not like a generic brochure

Style rules:
- Avoid generic university language
- Avoid vague phrases like "high-quality education" unless supported by specifics
- Keep sentences direct, clear, and human
- Prefer concrete detail over broad claims
"""

PROGRAM_DESCRIPTION_TEMPLATE = (
    PROGRAM_DESCRIPTION_ROLE
    + "\nContext:\n{kb_context}\n\n"
    + "Program name: {program_name}\n"
    + "Audience: {audience}\n\n"
    + "Language: {language_label}\n"
    + "Tone: {tone_label}\n"
    + "Voice: {voice_label}\n\n"
    + PROGRAM_DESCRIPTION_STRUCTURE
    + "\n"
    + PROGRAM_DESCRIPTION_GUIDELINES
)

HYBRID_ROLE = """
You are a senior content strategist for SRH University. Create a hybrid piece that combines brand clarity with industry insight, showing why SRH is distinct in the market.
"""

HYBRID_STRUCTURE = """
Required structure:
- Opening that frames the topic with SRH's point of view
- Brand foundation section that uses concrete facts from the PRIMARY knowledge base
- Industry context section that uses relevant trends or competitor signals from the SECONDARY knowledge base
- Differentiation section that explains how SRH stands apart
- Positioning section that connects brand strengths to audience needs
- Closing that reinforces the unique SRH proposition and invites action
"""

HYBRID_GUIDELINES = """
Brand requirements:
{source_rules}
{brand_voice_rules}
- Language: {language_label}
- Tone: {tone_label}
- Voice: {voice_label}
- Balance SRH facts with market context instead of overusing either one.
- Use the PRIMARY knowledge base for the brand story, proof points, and programme facts.
- Use the SECONDARY knowledge base to sharpen contrast, relevance, and differentiation.
- Highlight a clear positioning angle that feels specific to SRH, not generic to higher education.
- Show how SRH responds to the market differently and why that matters to the audience.
- Keep the writing strategic, concrete, and publication-ready.
"""

HYBRID_TEMPLATE = (
    HYBRID_ROLE
    + "\nContext:\n{kb_context}\n\n"
    + "Topic: {topic}\n"
    + "Audience: {audience}\n\n"
    + "Language: {language_label}\n"
    + "Tone: {tone_label}\n"
    + "Voice: {voice_label}\n\n"
    + HYBRID_STRUCTURE
    + "\n"
    + HYBRID_GUIDELINES
)

BLOG_POST_TEMPLATE = (
    BLOG_POST_ROLE
    + "\nContext:\n{context}\n\n"
    + "Topic: {topic}\n"
    + "Audience: {audience}\n"
    + "Language: {language_label}\n"
    + "Tone: {tone_label}\n"
    + "Voice: {voice_label}\n"
    + "Word count: ~{word_count}\n\n"
    + BLOG_POST_STRUCTURE
    + "\n"
    + BLOG_POST_GUIDELINES
)

NEWSLETTER_TEMPLATE = (
    NEWSLETTER_ROLE
    + "\nContext:\n{context}\n\n"
    + "Subject line: {subject}\n"
    + "Audience: {recipient_type}\n"
    + "Call to action: {cta}\n"
    + "Language: {language_label}\n"
    + "Tone: {tone_label}\n"
    + "Voice: {voice_label}\n"
    + NEWSLETTER_STRUCTURE
    + "\n"
    + NEWSLETTER_GUIDELINES
)


class _SafeDict(defaultdict):
    def __missing__(self, key: str) -> str:
        return ""


def render_template(template: str, variables: dict) -> str:
    """Inject variables into a template string using str.format_map."""
    safe_variables = _SafeDict(str, variables or {})
    return template.format_map(safe_variables)


def build_system_prompt(content_type: str) -> str:
    """Return the appropriate system-level prompt for the requested content type."""
    prompts = {
        "blog_post": "You are a content strategist for SRH University. Use the PRIMARY knowledge base as the source of truth for SRH facts, use the SECONDARY knowledge base for market context, competitor signals, and audience pain points, and write a blog post that feels strategic, credible, and clearly tied to SRH’s positioning in the market.",
        "newsletter": "You are a newsletter writer for SRH University. Use the PRIMARY knowledge base as the source of truth. Use the SECONDARY knowledge base only when it strengthens context or differentiation. Write a newsletter that is concrete, human, clearly branded, and suitable for publishing.",
        "program_description": "You are a program copywriter for SRH University. Use the PRIMARY knowledge base as the source of truth. Use the SECONDARY knowledge base only when it helps with positioning or relevance. Write a program description that is accurate, human, persuasive, and clearly branded for SRH.",
        "hybrid": "You are a senior content strategist for SRH University. Use both knowledge bases together: the PRIMARY knowledge base for brand facts and programme details, and the SECONDARY knowledge base for market context, positioning, and differentiation. Write a strategic hybrid piece that balances SRH voice with industry insight.",
    }
    return prompts.get(content_type, "You are a content writer for SRH University. Use the PRIMARY knowledge base as the source of truth, follow SRH brand voice guidelines, reference product specifications accurately, and use SRH-specific terminology naturally. Make the copy feel polished and publication-ready.")


def _format_context_block(label: str, chunks: list[str]) -> str:
    if not chunks:
        return f"{label}:\nNo context available."
    joined = "\n\n".join(chunks).strip()
    return f"{label}:\n{joined}"


def build_user_prompt(
    content_type: str,
    primary_chunks: list[str],
    secondary_chunks: list[str],
    variables: dict,
) -> str:
    """Combine retrieved context chunks with user variables into a final user prompt."""
    variables = dict(variables or {})
    primary_context = _format_context_block("PRIMARY KNOWLEDGE BASE", primary_chunks)
    secondary_context = _format_context_block("SECONDARY KNOWLEDGE BASE", secondary_chunks)

    defaults = {
        "topic": variables.get("topic", "Untitled topic"),
        "audience": variables.get("audience", "general audience"),
        "tone": variables.get("tone", "professional"),
        "voice": variables.get("voice", "brand_aligned"),
        "language": variables.get("language", "english"),
        "word_count": variables.get("word_count", 800),
        "subject": variables.get("subject", f"Update on {variables.get('topic', 'your topic')}"),
        "recipient_type": variables.get("recipient_type", "prospective students"),
        "cta": variables.get("cta", "Learn more"),
        "program_name": variables.get("program_name", variables.get("topic", "Untitled program")),
        "primary_context": primary_context,
        "secondary_context": secondary_context,
        "context": f"{primary_context}\n\n{secondary_context}",
        "kb_context": f"{primary_context}\n\n{secondary_context}",
        "source_rules": SOURCE_OF_TRUTH_RULES.strip(),
        "brand_voice_rules": SRH_BRAND_VOICE_RULES.strip(),
        "language_label": LANGUAGE_LABELS.get(variables.get("language", "english"), variables.get("language", "english")),
        "tone_label": TONE_LABELS.get(variables.get("tone", "professional"), variables.get("tone", "professional")),
        "voice_label": VOICE_LABELS.get(variables.get("voice", "brand_aligned"), variables.get("voice", "brand_aligned")),
    }

    if content_type == "blog_post":
        return render_template(BLOG_POST_TEMPLATE, defaults)
    if content_type == "newsletter":
        return render_template(NEWSLETTER_TEMPLATE, defaults)
    if content_type == "program_description":
        kb_context = f"{primary_context}\n\n{secondary_context}"
        return program_description_template(kb_context, defaults["program_name"], defaults["audience"])
    if content_type == "hybrid":
        return hybrid_template(
            f"{primary_context}\n\n{secondary_context}",
            defaults["topic"],
            defaults["audience"],
            defaults,
        )

    return (
        "Create polished SRH University content.\n\n"
        f"{primary_context}\n\n"
        f"{secondary_context}\n\n"
        f"Topic: {defaults['topic']}\n"
        f"Audience: {defaults['audience']}\n"
    )


def program_description_template(kb_context: str, program_name: str, audience: str = "prospective students") -> str:
    """Render a program description prompt focused on SRH's dual-study approach."""
    variables = {
        "program_name": program_name,
        "audience": audience,
        "kb_context": kb_context,
    }
    return render_template(PROGRAM_DESCRIPTION_TEMPLATE, variables)


def hybrid_template(
    kb_context: str,
    topic: str,
    audience: str,
    variables: dict | None = None,
) -> str:
    """Render a hybrid strategy prompt that combines brand and market context."""
    variables = dict(variables or {})
    payload = {
        "kb_context": kb_context,
        "topic": topic,
        "audience": audience,
        "source_rules": SOURCE_OF_TRUTH_RULES.strip(),
        "brand_voice_rules": SRH_BRAND_VOICE_RULES.strip(),
        "language_label": LANGUAGE_LABELS.get(variables.get("language", "english"), variables.get("language", "english")),
        "tone_label": TONE_LABELS.get(variables.get("tone", "professional"), variables.get("tone", "professional")),
        "voice_label": VOICE_LABELS.get(variables.get("voice", "brand_aligned"), variables.get("voice", "brand_aligned")),
    }
    return render_template(HYBRID_TEMPLATE, payload)
