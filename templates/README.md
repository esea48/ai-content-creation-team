# Prompt Templates

This folder contains proposed prompt versions for the main SRH content types.

## Files

- `blog_post_proposed_prompt.md` - stronger blog prompt focused on SRH positioning, proof points, and differentiation
- `newsletter_proposed_prompt.md` - cleaner newsletter prompt with tighter structure and more explicit SRH-specific detail
- `program_description_proposed_prompt.md` - revised program description prompt with a stronger value proposition and less generic language

## Purpose

These files are reference versions for prompt design and review. They are not used directly by the runtime app unless copied into the code in `src/prompt_templates.py`.

## How To Use

- Review the prompt text here when comparing current and proposed versions
- Copy the final wording into `src/prompt_templates.py` when you are ready to update the live templates
- Use the files in `analysis/` if you want the score-based comparison and rationale

## Notes

- `PRIMARY knowledge base` should remain the source of truth for SRH facts.
- `SECONDARY knowledge base` should only add market context, contrast, or differentiation.
- The goal is to keep output human, specific, and clearly tied to the SRH brand.
