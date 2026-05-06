# SRH University - AI Content Creator

A AI-powered content generator for SRH-branded marketing and admissions copy.

The workflow is simple:
- `PRIMARY` knowledge is the source of truth for SRH facts and brand rules.
- `SECONDARY` knowledge adds market context, contrast, and positioning.

## What It Does

- Retrieves relevant context from the knowledge base
- Builds prompts from reusable content templates
- Generates draft copy as Markdown
- Supports review and publish workflows
- Exposes a Gradio UI for non-technical editing

## Supported Content Types

The UI currently supports:
- `blog_post`
- `newsletter`
- `program_description`

The CLI also supports `hybrid` for more strategic brand-plus-market content.

## Workflow

### Draft
Generate a new piece of content from the knowledge base.

### Review
Create a review checklist so a human can check facts, tone, CTA, and compliance before publishing.

### Publish
Take a reviewed draft, validate it, and save the final published Markdown.

## UI

Run the Gradio app to work through the workflow in a browser:

```bash
python -m src.gradio_app
```

UI notes:
- `New` generates, edits, saves, and publishes content
- `Drafts` loads and edits saved drafts
- `Publish` browses final files
- `Topic` starts empty
- `Program Name` becomes a dropdown for program descriptions
- save/publish actions open a centered success popup with a close button and `Start new content`
- the UI shows friendly labels, while the backend keeps full file paths

## Setup

Fast setup:

```bash
./setup.sh
```

Manual setup:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then add your API key in `.env`:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

If no key is available, the app falls back to the local generation path.

Refresh the knowledge base:

```bash
python -m src.main --refresh-kb
```

## CLI

Generate content from the terminal:

```bash
python -m src.main \
  --type newsletter \
  --topic "Applied AI programs" \
  --audience prospective_students
```

Useful flags:
- `--type` accepts `blog_post`, `newsletter`, `program_description`, or `hybrid`
- `--workflow` accepts `draft`, `review`, or `publish`
- `--program-name` is useful for program descriptions
- `--output` saves generated Markdown
- `--prompt-output` saves the assembled prompt
- `--review-notes` saves the review checklist
- `--input` is required for `publish`

Example publish flow:

```bash
python -m src.main \
  --type newsletter \
  --workflow draft \
  --topic "Applied AI programs" \
  --audience prospective_students \
  --output output/drafts/newsletter_applied_ai_programs_english.md

python -m src.main \
  --type newsletter \
  --workflow review \
  --topic "Applied AI programs" \
  --audience prospective_students \
  --output output/drafts/newsletter_applied_ai_programs_english.md \
  --review-notes output/archive/reviews/newsletter_applied_ai_programs_review.md

python -m src.main \
  --type newsletter \
  --workflow publish \
  --topic "Applied AI programs" \
  --audience prospective_students \
  --input output/drafts/newsletter_applied_ai_programs_english.md \
  --output output/published/newsletter_applied_ai_programs_english.md
```

## Prompt Files

Live prompt logic:
- [`src/prompt_templates.py`](src/prompt_templates.py)

Reference prompt versions:
- `templates/blog_post_proposed_prompt.md`
- `templates/newsletter_proposed_prompt.md`
- `templates/program_description_proposed_prompt.md`

These reference files are for comparison and review. They are not used by the runtime unless copied into the code.

The `analysis/` folder contains the prompt comparison documents, including side-by-side current vs proposed prompt reviews and scoring notes.

The `kanban/` folder contains screenshots and exports from the project board, including Trello board screenshots used to track the workflow.

## Output Folders

- `output/drafts/` for work-in-progress drafts
- `output/published/` for final published content
- `output/archive/` for older examples and comparison artifacts

The app may also write:
- prompt bundles as `.txt`
- review checklists as `.md`

## Repo Structure

```text
src/              application code
knowledge_base/   SRH source material and supporting research
templates/        proposed prompt reference files
analysis/         prompt comparison and evaluation notes
kanban/           project board screenshots and exports
output/           generated drafts, published files, and archives
setup.sh          one-step local setup script
requirements.txt  Python dependencies
README.md         project overview and workflow guide
```

## Notes

- Blog posts are strategic and market-aware.
- Newsletters are concise, proof-driven, and brand-safe.
- Program descriptions lead with value proposition and practical relevance.
- The PRIMARY knowledge base should remain the factual source of truth.
