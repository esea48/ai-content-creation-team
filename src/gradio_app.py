"""
gradio_app.py

Gradio UI for the SRH University AI Content Creator.
Three tabs:
  - New: generate and edit content
  - Drafts: manage saved drafts
  - Publish: browse published content
"""

from __future__ import annotations

from base64 import b64encode
import re
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
import gradio as gr
from gradio.themes.utils.colors import Color

from src.content_pipeline import run, save_output, validate_output
from src.main import AUDIENCE_CHOICES, LANGUAGE_CHOICES, TONE_CHOICES, VOICE_CHOICES


CONTENT_TYPES = ("blog_post", "newsletter", "program_description")
PROGRAM_NAME_CHOICES = (
    "MSc Applied Data Science and Artificial Intelligence",
    "MSc Big Data and Business Analytics",
    "MA International Business and Leadership",
    "M.Eng. International Business and Engineering",
    "MSc Computer Science — Big Data and Artificial Intelligence",
    "Classical Music",
)
OUTPUT_ROOT = Path("output")
DRAFTS_DIR = OUTPUT_ROOT / "drafts"
PUBLISHED_DIR = OUTPUT_ROOT / "published"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
LOGO_PATH = Path(__file__).resolve().parent.parent / "knowledge_base" / "primary" / "SRH_Heidelberg_logo.png"
load_dotenv(dotenv_path=ENV_PATH, override=True)

SRH_RED = Color(
    c50="#fbeaea",
    c100="#f6caca",
    c200="#ed9d9d",
    c300="#e66f6f",
    c400="#dc4040",
    c500="#cc0000",
    c600="#b30000",
    c700="#8f0000",
    c800="#6b0000",
    c900="#470000",
    c950="#2c0000",
    name="srh_red",
)

SRH_ORANGE = Color(
    c50="#fff2e8",
    c100="#ffd9bd",
    c200="#ffc38f",
    c300="#ffad61",
    c400="#f99634",
    c500="#e87722",
    c600="#c96417",
    c700="#a55012",
    c800="#7f3d0e",
    c900="#5c2d0a",
    c950="#381b06",
    name="srh_orange",
)

SRH_NEUTRAL = Color(
    c50="#fcfcfc",
    c100="#f5f5f5",
    c200="#ececec",
    c300="#d6d6d6",
    c400="#b6b6b6",
    c500="#8b8b8b",
    c600="#666666",
    c700="#454545",
    c800="#2d2d2d",
    c900="#1a1a1a",
    c950="#101010",
    name="srh_neutral",
)

SRH_THEME = gr.themes.Soft(
    primary_hue=SRH_RED,
    secondary_hue=SRH_ORANGE,
    neutral_hue=SRH_NEUTRAL,
    radius_size="lg",
    spacing_size="md",
)

SRH_CSS = """
.srh-shell {
    background: #ffffff;
    border: 1px solid rgba(26, 26, 26, 0.12);
    border-radius: 20px;
    padding: 0.95rem 1rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 10px 24px rgba(26, 26, 26, 0.06);
}

.srh-shell-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}

.srh-shell-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 0;
}

.srh-logo-mark {
    flex: 0 0 auto;
    width: 2.6rem;
    height: 2.6rem;
    border-radius: 0.5rem;
    background: transparent;
    display: grid;
    place-items: center;
}

.srh-logo-mark img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
    filter: none;
}

.srh-shell-title {
    display: flex;
    flex-direction: column;
    gap: 0.05rem;
    min-width: 0;
}

.srh-shell-kicker {
    color: #cc0000;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.srh-shell-name {
    color: #1a1a1a;
    font-size: 1.05rem;
    font-weight: 800;
    line-height: 1.15;
}

.srh-shell-subtitle {
    color: #5c5c5c;
    font-size: 0.86rem;
    line-height: 1.3;
}

.srh-shell-pills {
    display: flex;
    gap: 0.45rem;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.srh-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    border: 1px solid rgba(26, 26, 26, 0.14);
    border-radius: 999px;
    padding: 0.45rem 0.75rem;
    font-size: 0.84rem;
    font-weight: 600;
    background: #fafafa;
    color: #202020;
}

.srh-pill--active {
    border-color: rgba(204, 0, 0, 0.48);
    box-shadow: 0 0 0 2px rgba(204, 0, 0, 0.08) inset;
}

.srh-pill-badge {
    display: inline-grid;
    place-items: center;
    min-width: 1.2rem;
    height: 1.2rem;
    border-radius: 999px;
    padding: 0 0.35rem;
    background: #cc0000;
    color: #ffffff;
    font-size: 0.72rem;
    font-weight: 800;
}

.srh-page-note {
    margin-top: 0.25rem;
    margin-bottom: 0.65rem;
    color: #5a5a5a;
    font-size: 0.9rem;
}

.srh-success-popup {
    position: fixed !important;
    inset: 0;
    background: rgba(26, 26, 26, 0.52);
    z-index: 9999;
    padding: 1rem;
}

.srh-success-popup > div {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.srh-success-card {
    width: min(460px, calc(100vw - 2rem));
    background: #ffffff;
    border: 1px solid rgba(26, 26, 26, 0.12);
    border-radius: 22px;
    padding: 1.25rem 1.25rem 1rem 1.25rem;
    box-shadow: 0 24px 60px rgba(26, 26, 26, 0.22);
}

.srh-success-card .srh-panel-title {
    margin-top: 0;
}

.srh-panel-title {
    color: #1a1a1a;
    font-size: 1rem;
    font-weight: 800;
    margin: 0.25rem 0 0.35rem 0;
}

.srh-panel-subtitle {
    color: #5f5f5f;
    font-size: 0.88rem;
    margin-bottom: 0.75rem;
}

.srh-draft-toolbar {
    display: flex;
    gap: 0.55rem;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.srh-compacted .wrap {
    gap: 0.6rem !important;
}
"""


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return value or "content"


def _artifact_path(folder: Path, content_type: str, topic: str, language: str) -> Path:
    prefix = f"{content_type}_{_slug(topic)}_{language}_{_timestamp()}"
    return folder / f"{prefix}.md"


def _infer_content_type(path: str | None) -> str:
    if not path:
        return "newsletter"
    stem = Path(path).stem
    for content_type in CONTENT_TYPES:
        if stem.startswith(f"{content_type}_"):
            return content_type
    return "newsletter"


def _read_text(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def _logo_data_uri() -> str:
    data = LOGO_PATH.read_bytes()
    return "data:image/png;base64," + b64encode(data).decode("ascii")


def _list_markdown_files(folder: Path) -> list[str]:
    if not folder.exists():
        return []
    return [str(path) for path in sorted(folder.glob("*.md"), reverse=True)]


def _artifact_choices(folder: Path) -> list[tuple[str, str]]:
    choices = [("select file", "")]
    for path_str in _list_markdown_files(folder):
        path = Path(path_str)
        content = _read_text(path_str)
        choices.append((_friendly_artifact_label(path, content), path_str))
    return choices


def _refresh_dropdown(folder: Path):
    choices = _artifact_choices(folder)
    return gr.update(choices=choices, value="")


def _humanize_content_type(content_type: str) -> str:
    return content_type.replace("_", " ").title()


def _extract_content_title(text: str | None, fallback: str = "") -> str:
    if not text:
        return fallback
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.match(r"^#{1,6}\s+(.+)$", stripped)
        if match:
            return match.group(1).strip()
        break
    return fallback


def _friendly_artifact_label(path: Path | str, content_text: str | None = None) -> str:
    file_path = Path(path)
    stem = file_path.stem
    content_type = stem
    title_slug = ""
    short_id = ""
    date_label = ""

    parts = stem.rsplit("_", 3)
    if len(parts) == 4:
        prefix, language, date_part, time_part = parts
        if "_" in prefix:
            content_type, title_slug = prefix.split("_", 1)
        else:
            content_type = prefix
        short_id = time_part
        try:
            date_label = datetime.strptime(date_part, "%Y%m%d").strftime("%b %-d, %Y")
        except ValueError:
            date_label = date_part

    title = _extract_content_title(content_text, fallback=title_slug.replace("_", " ").title() or _humanize_content_type(content_type))
    if short_id and date_label:
        return f"{_humanize_content_type(content_type)} · {title} · {short_id} · {date_label}"
    if short_id:
        return f"{_humanize_content_type(content_type)} · {title} · {short_id}"
    return f"{_humanize_content_type(content_type)} · {title}"


def _generate_content(
    content_type: str,
    topic: str,
    audience: str,
    language: str,
    tone: str,
    voice: str,
    program_name: str,
    ):
    variables = {
        "program_name": program_name or topic,
        "language": language,
        "tone": tone,
        "voice": voice,
    }
    draft_path = _artifact_path(DRAFTS_DIR, content_type, topic, language)

    content = run(
        content_type=content_type,
        topic=topic,
        audience=audience,
        variables=variables,
        workflow="draft",
        output_path=str(draft_path),
    )
    status = f"Draft created: `{_friendly_artifact_label(draft_path, content)}`."
    return (
        gr.update(value=content),
        status,
        str(draft_path),
        content,
        gr.update(interactive=True),
        gr.update(interactive=True),
    )


def _set_generating_state():
    return (
        gr.update(visible=True, value="### Generating content...\nPlease wait while we build your draft."),
        gr.update(value=""),
        "Generating draft...",
        "",
        "",
        gr.update(interactive=False),
        gr.update(interactive=False),
    )


def _save_draft(
    draft_text: str,
    content_type: str,
    topic: str,
    language: str,
    current_draft_path: str | None = None,
) -> tuple[str, str, object, object]:
    if not draft_text or not draft_text.strip():
        raise gr.Error("Please generate or enter draft content first.")
    path = Path(current_draft_path) if current_draft_path else _artifact_path(DRAFTS_DIR, content_type, topic, language)
    save_output(draft_text.strip(), str(path))
    status = f"Saved draft: `{_friendly_artifact_label(path, draft_text)}`."
    banner, button = _success_state("Draft saved successfully")
    return status, str(path), banner, button


def _publish_draft(
    draft_text: str,
    content_type: str,
    topic: str,
    audience: str,
    language: str,
    tone: str,
    voice: str,
    program_name: str,
    current_draft_path: str | None = None,
) -> tuple[str, str, object, object, object]:
    if not draft_text or not draft_text.strip():
        raise gr.Error("Please generate or enter draft content first.")
    if not validate_output(draft_text, content_type):
        raise gr.Error("The draft is too short or empty to publish.")

    published_path = _artifact_path(PUBLISHED_DIR, content_type, topic, language)
    save_output(draft_text.strip(), str(published_path))

    status = f"Published: `{_friendly_artifact_label(published_path, draft_text)}`."
    banner, button = _success_state("Content published successfully")
    return status, str(published_path), _refresh_dropdown(PUBLISHED_DIR), banner, button


def _load_file(path: str | None) -> tuple[str, str]:
    if not path:
        return "", "Select a file first."
    content = _read_text(path)
    return content, f"Loaded `{path}`."


def _toggle_program_name(content_type: str):
    visible = content_type == "program_description"
    if visible:
        return gr.update(visible=True, choices=PROGRAM_NAME_CHOICES, value=PROGRAM_NAME_CHOICES[0])
    return gr.update(visible=False, value=None)


def _success_state(message: str) -> tuple[object, object]:
    return (
        gr.update(visible=True, value=f"### {message}"),
        gr.update(visible=True),
    )


def _reset_create_state():
    return (
        gr.update(value="newsletter"),  # content_type
        gr.update(value="prospective_students"),  # audience
        gr.update(value="professional"),  # tone
        gr.update(value="english"),  # language
        gr.update(value="brand_aligned"),  # voice
        gr.update(value=""),  # topic
        gr.update(visible=False, value=PROGRAM_NAME_CHOICES[0]),  # program_name
        gr.update(value=""),  # draft_preview
        gr.update(value=""),  # new_status
        gr.update(value=""),  # shared_draft_path
        gr.update(value=""),  # current_draft_content
        gr.update(interactive=False),  # save_btn
        gr.update(interactive=False),  # publish_btn
        gr.update(visible=False, value=""),  # success_message
        gr.update(visible=True, interactive=True),  # start_new_btn
        gr.update(visible=False),  # success_popup
    )


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="SRH AI Content Creator", fill_width=True) as demo:
        logo_src = _logo_data_uri()
        gr.HTML(
            f"""
            <div class="srh-shell">
              <div class="srh-shell-top">
                <div class="srh-shell-brand">
                  <div class="srh-logo-mark" aria-label="SRH logo">
                    <img src="{logo_src}" alt="SRH logo" />
                  </div>
                  <div class="srh-shell-title">
                    <div class="srh-shell-kicker">Design your Future</div>
                    <div class="srh-shell-name">Content Creator</div>
                    <div class="srh-shell-subtitle">Compact content workflow for SRH newsletters, blog posts, and program descriptions.</div>
                  </div>
                </div>
              </div>
            </div>
            """
        )

        shared_draft_path = gr.State("")
        current_draft_content = gr.State("")
        success_popup = gr.Column(visible=False, elem_classes=["srh-success-popup"])
        with success_popup:
            with gr.Column(elem_classes=["srh-success-card"]):
                success_message = gr.Markdown(value="", elem_classes=["srh-panel-title"])
                gr.Markdown(
                    "Your content is saved. You can close this message or start a new piece.",
                    elem_classes=["srh-panel-subtitle"],
                )
                with gr.Row():
                    close_popup_btn = gr.Button("Close")
                    start_new_btn = gr.Button("Start new content", variant="primary")
        published_dropdown = gr.Dropdown(
            choices=_artifact_choices(PUBLISHED_DIR),
            label="Published Files",
            value="",
            render=False,
        )

        with gr.Tabs():
            with gr.Tab("New"):
                gr.Markdown("### New", elem_classes=["srh-panel-title"])
                gr.Markdown("Generate a draft, edit it below, then save or publish.", elem_classes=["srh-panel-subtitle"])

                with gr.Row():
                    content_type = gr.Dropdown(
                        choices=CONTENT_TYPES,
                        value="newsletter",
                        label="Content Type",
                        scale=1,
                    )
                    audience = gr.Dropdown(
                        choices=AUDIENCE_CHOICES,
                        value="prospective_students",
                        label="Audience",
                        scale=1,
                    )
                with gr.Row():
                    tone = gr.Dropdown(
                        choices=TONE_CHOICES,
                        value="professional",
                        label="Tone",
                        scale=1,
                    )
                    language = gr.Dropdown(
                        choices=LANGUAGE_CHOICES,
                        value="english",
                        label="Language",
                        scale=1,
                    )
                with gr.Row():
                    voice = gr.Dropdown(
                        choices=VOICE_CHOICES,
                        value="brand_aligned",
                        label="Voice",
                        scale=1,
                )
                topic = gr.Textbox(label="Topic", value="")
                program_name = gr.Dropdown(
                    label="Program Name",
                    choices=PROGRAM_NAME_CHOICES,
                    value=PROGRAM_NAME_CHOICES[0],
                    visible=False,
                )
                content_type.change(
                    fn=_toggle_program_name,
                    inputs=[content_type],
                    outputs=[program_name],
                    queue=False,
                    show_progress="hidden",
                )

                generate_btn = gr.Button("Generate", variant="primary")

                loading_banner = gr.Markdown(
                    value="### Generating content...\nPlease wait while we build your draft.",
                    visible=False,
                )
                draft_preview = gr.Textbox(label="Draft", lines=14, interactive=True)
                new_status = gr.Markdown(label="Status")

                with gr.Row(elem_classes=["srh-draft-toolbar"]):
                    save_btn = gr.Button("Save draft", interactive=False)
                    publish_btn = gr.Button("Publish", variant="primary", interactive=False)

                generate_btn.click(
                    fn=_set_generating_state,
                    outputs=[loading_banner, draft_preview, new_status, shared_draft_path, current_draft_content, save_btn, publish_btn],
                ).then(
                    fn=_generate_content,
                    inputs=[content_type, topic, audience, language, tone, voice, program_name],
                    outputs=[draft_preview, new_status, shared_draft_path, current_draft_content, save_btn, publish_btn],
                )

                save_btn.click(
                    fn=_save_draft,
                    inputs=[current_draft_content, content_type, topic, language, shared_draft_path],
                    outputs=[new_status, shared_draft_path, success_message, success_popup],
                )

                publish_btn.click(
                    fn=_publish_draft,
                    inputs=[current_draft_content, content_type, topic, audience, language, tone, voice, program_name, shared_draft_path],
                    outputs=[new_status, shared_draft_path, published_dropdown, success_message, success_popup],
                )

            with gr.Tab("Drafts"):
                gr.Markdown("### Drafts", elem_classes=["srh-panel-title"])
                gr.Markdown("Saved drafts ready for editing or publishing.", elem_classes=["srh-panel-subtitle"])
                drafts_dropdown = gr.Dropdown(
                    choices=_artifact_choices(DRAFTS_DIR),
                    label="Saved Drafts",
                    value="",
                )
                with gr.Row():
                    refresh_drafts_btn = gr.Button("Refresh")
                    load_drafts_btn = gr.Button("Load")
                drafts_editor = gr.Textbox(label="Draft Editor", lines=14, interactive=True)
                drafts_status = gr.Markdown(label="Status")
                with gr.Row(elem_classes=["srh-draft-toolbar"]):
                    save_draft_btn = gr.Button("Save changes")
                    publish_draft_btn = gr.Button("Publish", variant="primary")

                refresh_drafts_btn.click(
                    fn=lambda: _refresh_dropdown(DRAFTS_DIR),
                    outputs=[drafts_dropdown],
                )

                load_drafts_btn.click(
                    fn=lambda path: (*_load_file(path), path or ""),
                    inputs=[drafts_dropdown],
                    outputs=[drafts_editor, drafts_status, shared_draft_path],
                )

                save_draft_btn.click(
                    fn=lambda text, selected: _save_draft(
                        text,
                        _infer_content_type(selected),
                        Path(selected).stem if selected else "saved_draft",
                        LANGUAGE_CHOICES[0],
                        selected,
                    ),
                    inputs=[drafts_editor, drafts_dropdown],
                    outputs=[drafts_status, shared_draft_path, success_message, success_popup],
                )

                publish_draft_btn.click(
                    fn=lambda text, selected: _publish_draft(
                        text,
                        _infer_content_type(selected),
                        Path(selected).stem if selected else "saved draft",
                        "prospective students",
                        LANGUAGE_CHOICES[0],
                        "professional",
                        "brand_aligned",
                        "",
                        selected,
                    ),
                    inputs=[drafts_editor, drafts_dropdown],
                    outputs=[drafts_status, shared_draft_path, published_dropdown, success_message, success_popup],
                )

            with gr.Tab("Publish"):
                gr.Markdown("### Published", elem_classes=["srh-panel-title"])
                gr.Markdown("Final approved files.", elem_classes=["srh-panel-subtitle"])
                published_dropdown.render()
                with gr.Row():
                    refresh_published_btn = gr.Button("Refresh")
                    load_published_btn = gr.Button("View")
                published_view = gr.Textbox(label="Published Content", lines=14, interactive=False)
                published_status = gr.Markdown(label="Status")

                refresh_published_btn.click(
                    fn=lambda: _refresh_dropdown(PUBLISHED_DIR),
                    outputs=[published_dropdown],
                )
                load_published_btn.click(
                    fn=_load_file,
                    inputs=[published_dropdown],
                    outputs=[published_view, published_status],
                )

        close_popup_btn.click(
            fn=lambda: (gr.update(visible=False), gr.update(value="")),
            outputs=[success_popup, success_message],
        )

        start_new_btn.click(
            fn=_reset_create_state,
            outputs=[
                content_type,
                audience,
                tone,
                language,
                voice,
                topic,
                program_name,
                draft_preview,
                new_status,
                shared_draft_path,
                current_draft_content,
                save_btn,
                publish_btn,
                success_message,
                start_new_btn,
                success_popup,
            ],
        )

        gr.Markdown(
            "Use **New** to generate and edit content, **Drafts** to manage saved drafts, and **Publish** to browse final content.",
            elem_classes=["srh-page-note"],
        )

    return demo


def launch() -> None:
    demo = build_demo()
    preferred_port = os.getenv("GRADIO_SERVER_PORT")
    candidate_ports = []
    if preferred_port:
        candidate_ports.append(int(preferred_port))
    candidate_ports.extend(range(8360, 8376))
    candidate_ports.extend([8400, 8500, 8600, 8700, 8800, 8900, 9002, 10000, 20000, 30000, 40000, 50000, 62000])

    last_error: Exception | None = None
    for port in dict.fromkeys(candidate_ports):
        try:
            demo.launch(
                server_name="127.0.0.1",
                server_port=port,
                inbrowser=True,
                theme=SRH_THEME,
                css=SRH_CSS,
            )
            return
        except OSError as exc:
            last_error = exc

    if last_error is not None:
        raise last_error


if __name__ == "__main__":
    launch()
