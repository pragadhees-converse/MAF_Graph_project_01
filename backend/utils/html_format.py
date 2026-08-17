# backend/utils/html_format.py
import html
import re

_HTML_TAG_PATTERN = re.compile(r"<(p|div|br|ul|ol|li|b|strong|h[1-6])\b", re.IGNORECASE)
_HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")


def ensure_html_body(text: str) -> str:
    """
    Guarantees the body renders correctly as HTML, even if the model
    sends plain markdown instead of real HTML. Converts:
      - **bold** -> <b>bold</b>
      - # / ## / ### headers -> <h1>/<h2>/<h3> (capped at h6)
      - "- item" lines -> proper <ul><li> lists
      - remaining lines -> wrapped in <p> so line breaks are preserved

    If the text already contains real HTML tags, it's passed through
    unchanged — this only activates when the model outputs raw
    markdown/plain text instead.
    """
    if _HTML_TAG_PATTERN.search(text):
        return text

    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)

    lines = escaped.split("\n")
    out: list[str] = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in lines:
        stripped = line.strip()

        header_match = _HEADER_PATTERN.match(stripped)
        if header_match:
            close_list()
            level = min(len(header_match.group(1)), 6)
            out.append(f"<h{level}>{header_match.group(2)}</h{level}>")
            continue

        if stripped.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{stripped[2:]}</li>")
            continue

        close_list()
        if stripped:
            out.append(f"<p>{stripped}</p>")

    close_list()
    return "".join(out)