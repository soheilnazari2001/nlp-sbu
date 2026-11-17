#!/usr/bin/env python3
"""Build the NLP @ SBU course site.

Reads content/sessions/*.md, renders styled session pages into sessions/,
and injects the schedule table + note cards into index.html and notes.html.

Usage:
    python3 tools/build.py            # build everything
    python3 tools/build.py --check    # validate only, write nothing

No third-party dependencies.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "sessions"
OUT = ROOT / "sessions"

# ---------------------------------------------------------------------------
# Course data
# ---------------------------------------------------------------------------

COURSE = {
    "title_fa": "پردازش زبان‌های طبیعی",
    "title_en": "Natural Language Processing",
    "instructor": "دکتر مهرنوش شمس‌فرد",
    "instructor_en": "Dr. Mehrnoush Shamsfard",
    "university": "دانشگاه شهید بهشتی",
}

# Course sessions come from content/sessions/*.md. No schedule is invented.

CALLOUT_TYPES = {
    "question": ("سؤال", "Question", "#1d4ed8", '<path d="M9 9a3 3 0 1 1 4.6 2.5c-.9.6-1.6 1.2-1.6 2.3"/><circle cx="12" cy="17.5" r=".8" fill="currentColor" stroke="none"/>'),
    "answer": ("پاسخ", "Answer", "#0b7a66", '<path d="m5 12.5 4.2 4.2L19 7"/>'),
    "tip": ("نکته", "Tip", "#925100", '<path d="M9 18h6"/><path d="M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.4.3.6.7.6 1.2V16h6v-1c0-.5.2-.9.6-1.2A6 6 0 0 0 12 3Z"/>'),
    "important": ("مهم", "Important", "#b42318", '<path d="M12 3 2.8 19.2A1.2 1.2 0 0 0 3.9 21h16.2a1.2 1.2 0 0 0 1.1-1.8L12 3Z"/><path d="M12 9v5"/><circle cx="12" cy="17.4" r=".8" fill="currentColor" stroke="none"/>'),
    "definition": ("تعریف", "Definition", "#5b3fd1", '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v18H6.5A2.5 2.5 0 0 1 4 18.5v-13Z"/><path d="M8 3v18"/>'),
    "example": ("مثال", "Example", "#0e6f86", '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z"/><path d="m19 16 .7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7L19 16Z"/>'),
    "warning": ("هشدار", "Caution", "#b45309", '<path d="M12 3 2.8 19.2A1.2 1.2 0 0 0 3.9 21h16.2a1.2 1.2 0 0 0 1.1-1.8L12 3Z"/><path d="M12 9v5"/><circle cx="12" cy="17.4" r=".8" fill="currentColor" stroke="none"/>'),
    "note": ("یادداشت", "Note", "#475569", '<path d="M4 4h11l5 5v11H4z"/><path d="M15 4v5h5"/><path d="M8 13h8M8 17h5"/>'),
    "persian": ("توضیح فارسی", "Persian note", "#1d4ed8", '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.7 3.8 9S14.5 18.4 12 21c-2.5-2.6-3.8-5.7-3.8-9S9.5 5.6 12 3Z"/>'),
}
CALLOUT_ALIASES = {"fa": "persian", "info": "note", "caution": "warning", "key": "important", "q": "question", "a": "answer"}

PERSIAN_RE = re.compile(r"[؀-ۿ‌]")
LATIN_RE = re.compile(r"[A-Za-z]")
SAFE_SCHEMES = {"http", "https", "mailto"}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def esc(value: str) -> str:
    return html.escape(value, quote=True)


def to_fa_digits(value: str) -> str:
    table = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return value.translate(table)


def slugify(text: str) -> str:
    value = re.sub(r"[^\w]+", "-", text.strip().lower(), flags=re.UNICODE)
    value = value.strip("-_")
    return value or "section"


def direction_attr(text: str) -> str:
    fa = len(PERSIAN_RE.findall(text))
    en = len(LATIN_RE.findall(text))
    if fa > en:
        return ' dir="rtl" lang="fa"'
    if en > 0 and fa == 0:
        return ' dir="ltr" lang="en"'
    return ' dir="auto"'


def is_safe_url(url: str) -> bool:
    candidate = html.unescape(url).strip()
    if not candidate:
        return False
    match = re.match(r"^([A-Za-z][A-Za-z0-9+.\-]*):", candidate)
    if match:
        return match.group(1).lower() in SAFE_SCHEMES
    return True


def _brace_span(s: str, i: int):
    """s[i] == '{'. Return (content, index after '}') or (None, i)."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    return None, i


MATH_CMDS = {
    "\\mid": '<span class="m-mid">|</span>',
    "\\prod": '<span class="m-op">∏</span>',
    "\\sum": '<span class="m-op">∑</span>',
    "\\times": "×",
    "\\cdot": "·",
    "\\cdots": "⋯",
    "\\dots": "…",
    "\\approx": "≈",
    "\\Rightarrow": "⇒",
    "\\rightarrow": "→",
    "\\to": "→",
    "\\le": "≤",
    "\\ge": "≥",
    "\\ne": "≠",
    "\\lambda": "λ",
    "\\infty": "∞",
    "\\quad": '<span class="m-sp"></span>',
    "\\qquad": '<span class="m-sp m-sp2"></span>',
    "\\left": "",
    "\\right": "",
}


def math_inline(s: str) -> str:
    r"""Render a small math subset (\frac, _{}, ^{}, \mid, \prod, …) to HTML."""
    out: List[str] = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if s.startswith("\\frac", i):
            j = i + 5
            while j < n and s[j].isspace():
                j += 1
            if j < n and s[j] == "{":
                num, j = _brace_span(s, j)
                if num is not None and j <= n:
                    while j < n and s[j].isspace():
                        j += 1
                    if j < n and s[j] == "{":
                        den, j = _brace_span(s, j)
                        if den is not None and j <= n:
                            out.append(
                                '<span class="frac"><span class="frac-n">%s</span>'
                                '<span class="frac-d">%s</span></span>'
                                % (math_inline(num), math_inline(den))
                            )
                            i = j
                            continue
            out.append(esc(c))
            i += 1
            continue
        if c in ("^", "_"):
            tag = "sup" if c == "^" else "sub"
            if i + 1 < n and s[i + 1] == "{":
                content, j = _brace_span(s, i + 1)
                if content is not None and j <= n:
                    out.append(f"<{tag}>{math_inline(content)}</{tag}>")
                    i = j
                    continue
            if i + 1 < n:
                out.append(f"<{tag}>{esc(s[i + 1])}</{tag}>")
                i += 2
                continue
            out.append(esc(c))
            i += 1
            continue
        if s.startswith("\\text", i):
            j = i + 5
            if j < n and s[j] == "{":
                content, j = _brace_span(s, j)
                if content is not None and j <= n:
                    out.append(f'<span class="m-text">{esc(content)}</span>')
                    i = j
                    continue
            out.append(esc(c))
            i += 1
            continue
        if s.startswith("\\hat", i):
            if i + 5 < n and s[i + 5] != "{":
                out.append(f'<span class="m-hat">{esc(s[i + 5])}</span>')
                i += 6
                continue
            out.append(esc(c))
            i += 1
            continue
        matched = False
        for cmd in sorted(MATH_CMDS, key=len, reverse=True):
            if s.startswith(cmd, i):
                out.append(MATH_CMDS[cmd])
                i += len(cmd)
                matched = True
                break
        if matched:
            continue
        out.append(esc(c))
        i += 1
    return "".join(out)


def inline_md(text: str) -> str:
    """Render inline Markdown after escaping the source."""
    stash: List[str] = []

    def keep(value: str) -> str:
        stash.append(value)
        return f"\x00{len(stash) - 1}\x00"

    # inline code first
    text = re.sub(r"`([^`\n]+)`", lambda m: keep(f"<code>{esc(m.group(1))}</code>"), text)
    # inline math
    text = re.sub(
        r"\$([^$\n]+)\$",
        lambda m: keep(f'<span class="math">{math_inline(m.group(1))}</span>'),
        text,
    )
    text = esc(text)
    # links
    def link(match: re.Match[str]) -> str:
        label = match.group(1)
        url = html.unescape(match.group(2))
        if not is_safe_url(url):
            return label
        external = url.startswith(("http://", "https://"))
        attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
        return keep(f'<a href="{esc(url)}"{attrs}>{label}</a>')
    text = re.sub(r"\[([^\]]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)
    for index, value in enumerate(stash):
        text = text.replace(f"\x00{index}\x00", value)
    return text


# ---------------------------------------------------------------------------
# Markdown block renderer
# ---------------------------------------------------------------------------

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d{1,9}[.)])\s+(.*)$")
QUOTE_RE = re.compile(r"^\s*>\s?(.*)$")
TABLE_DELIM_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
HR_RE = re.compile(r"^\s{0,3}((?:-[ \t]*){3,}|(?:\*[ \t]*){3,}|(?:_[ \t]*){3,})\s*$")
CALLOUT_RE = re.compile(r"^:::\s*([A-Za-z-]+)(?:\s+(.+?))?\s*$")
QA_RE = re.compile(r"^\s*(?:Q|A|پرسش|پاسخ)\s*[|:]\s*(.+?)\s*$")


class Renderer:
    def __init__(self) -> None:
        self.toc: List[Tuple[int, str, str]] = []
        self.heading_count = 0
        self.sub_count = 0
        self.ids: Dict[str, int] = {}

    def render(self, markdown: str) -> str:
        lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        return self.blocks(lines)

    def unique_id(self, text: str, level: int) -> str:
        base = slugify(text)
        if base in self.ids:
            self.ids[base] += 1
            base = f"{base}-{self.ids[base]}"
        else:
            self.ids[base] = 1
        return base

    def blocks(self, lines: List[str]) -> str:
        out: List[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue

            # fenced code
            if line.strip().startswith("```"):
                lang = line.strip()[3:].strip()
                i += 1
                code_lines = []
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1
                if lang.lower() == "math":
                    rows = []
                    for code_line in code_lines:
                        if code_line.strip():
                            rows.append(
                                f'<div class="math-row"><span class="math">'
                                f"{math_inline(code_line.strip())}</span></div>"
                            )
                    out.append(f'<div class="math-block" dir="ltr">{"".join(rows)}</div>')
                else:
                    cls = f' class="language-{esc(lang)}"' if lang else ""
                    out.append(f"<pre><code{cls}>{esc(chr(10).join(code_lines))}</code></pre>")
                continue

            # qa block (must precede generic callout parsing)
            qa_match = CALLOUT_RE.match(line)
            if qa_match and qa_match.group(1).lower() == "qa":
                i += 1
                qa_lines = []
                while i < len(lines) and not lines[i].strip().startswith(":::"):
                    qa_lines.append(lines[i])
                    i += 1
                i += 1
                out.append(self.qa_block(qa_lines))
                continue

            # callout
            match = CALLOUT_RE.match(line)
            if match:
                kind = CALLOUT_ALIASES.get(match.group(1).lower(), match.group(1).lower())
                title = match.group(2) or ""
                i += 1
                body_lines = []
                while i < len(lines) and not lines[i].strip().startswith(":::"):
                    body_lines.append(lines[i])
                    i += 1
                i += 1
                out.append(self.callout(kind, title, self.blocks(body_lines)))
                continue

            # headings
            match = HEADING_RE.match(line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                heading_id = self.unique_id(text, level)
                if level == 2:
                    self.heading_count += 1
                    self.sub_count = 0
                    self.toc.append((2, text, heading_id))
                elif level == 3:
                    self.sub_count += 1
                    self.toc.append((3, text, heading_id))
                if " | " in text:
                    part_fa, part_en = text.split(" | ", 1)
                    heading_html = (
                        f'{inline_md(part_fa)}'
                        f'<span class="h-en" dir="ltr">{inline_md(part_en)}</span>'
                    )
                else:
                    heading_html = inline_md(text)
                out.append(
                    f'<h{level} id="{heading_id}"{direction_attr(text)}>{heading_html}</h{level}>'
                )
                i += 1
                continue

            # horizontal rule
            if HR_RE.match(line):
                out.append("<hr>")
                i += 1
                continue

            # table
            if "|" in line and i + 1 < len(lines) and TABLE_DELIM_RE.match(lines[i + 1]):
                table_lines = [line]
                i += 2
                while i < len(lines) and "|" in lines[i] and lines[i].strip():
                    table_lines.append(lines[i])
                    i += 1
                out.append(self.table(table_lines))
                continue

            # list
            if LIST_RE.match(line):
                list_lines = []
                while i < len(lines):
                    if LIST_RE.match(lines[i]) or (lines[i].startswith((" ", "\t")) and lines[i].strip()):
                        list_lines.append(lines[i])
                        i += 1
                        continue
                    if not lines[i].strip():
                        lookahead = i
                        while lookahead < len(lines) and not lines[lookahead].strip():
                            lookahead += 1
                        if lookahead < len(lines) and LIST_RE.match(lines[lookahead]):
                            i = lookahead
                            continue
                    break
                out.append(self.list_block(list_lines))
                continue

            # blockquote
            if QUOTE_RE.match(line):
                quote_lines = []
                while i < len(lines) and QUOTE_RE.match(lines[i]):
                    quote_lines.append(QUOTE_RE.match(lines[i]).group(1))
                    i += 1
                inner = self.blocks(quote_lines)
                out.append(f"<blockquote>{inner}</blockquote>")
                continue

            # paragraph
            para = [line]
            i += 1
            while (i < len(lines) and lines[i].strip() and not HEADING_RE.match(lines[i])
                   and not LIST_RE.match(lines[i]) and not QUOTE_RE.match(lines[i])
                   and not CALLOUT_RE.match(lines[i]) and not lines[i].strip().startswith("```")
                   and not HR_RE.match(lines[i])):
                para.append(lines[i])
                i += 1
            text = " ".join(part.strip() for part in para)
            attr = direction_attr(text)
            out.append(f"<p{attr}>{inline_md(text)}</p>")

        return "\n".join(out)

    def callout(self, kind: str, title: str, body: str) -> str:
        if kind not in CALLOUT_TYPES:
            kind = "note"
        label_fa, label_en, color, icon = CALLOUT_TYPES[kind]
        if title:
            label_fa = title
        cls = f"callout callout--{kind}"
        return (
            f'<div class="{cls}">'
            f'<div class="callout-head"><span class="co-icon"><svg viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{icon}</svg></span>'
            f'<span>{esc(label_fa)}</span><span class="co-label">{esc(label_en)}</span></div>'
            f'<div class="callout-body">{body}</div></div>'
        )

    def table(self, rows: List[str]) -> str:
        def cells(row: str) -> List[str]:
            value = row.strip()
            if value.startswith("|"):
                value = value[1:]
            if value.endswith("|"):
                value = value[:-1]
            return [cell.strip() for cell in value.split("|")]

        head = cells(rows[0])
        body_rows = [cells(row) for row in rows[1:]]
        head_html = "".join(
            f'<th{direction_attr(cell)}>{inline_md(cell)}</th>' for cell in head
        )
        body_html = ""
        for row in body_rows:
            body_html += "<tr>" + "".join(
                f'<td{direction_attr(cell)}>{inline_md(cell)}</td>' for cell in row
            ) + "</tr>"
        table_dir = direction_attr(" ".join(rows))
        return (
            f'<div class="table-scroll"><table{table_dir}>'
            f"<thead><tr>{head_html}</tr></thead>"
            f"<tbody>{body_html}</tbody></table></div>"
        )

    def list_block(self, lines: List[str]) -> str:
        items: List[Tuple[int, bool, str]] = []
        for line in lines:
            match = LIST_RE.match(line)
            if not match:
                if items and line.strip():
                    level, ordered, text = items[-1]
                    items[-1] = (level, ordered, text + " " + line.strip())
                continue
            indent = match.group(1).replace("\t", "    ")
            level = len(indent) // 2
            ordered = not match.group(2) in "-*+"
            items.append((level, ordered, match.group(3)))
        if not items:
            return ""

        root: Dict = {"level": -1, "ordered": False, "text": None, "children": []}
        stack = [{"level": -1, "node": root}]
        for level, ordered, text in items:
            while len(stack) > 1 and stack[-1]["level"] >= level:
                stack.pop()
            node = {"level": level, "ordered": ordered, "text": text, "children": []}
            stack[-1]["node"]["children"].append(node)
            stack.append({"level": level, "node": node})

        def render_children(parent: Dict) -> str:
            out = []
            index = 0
            children = parent["children"]
            while index < len(children):
                ordered = children[index]["ordered"]
                group = []
                while index < len(children) and children[index]["ordered"] == ordered:
                    group.append(children[index])
                    index += 1
                tag = "ol" if ordered else "ul"
                out.append(f'<{tag} dir="auto">')
                for node in group:
                    inner = inline_md(node["text"])
                    if node["children"]:
                        inner += render_children(node)
                    out.append(f"<li{direction_attr(node['text'])}>{inner}</li>")
                out.append(f"</{tag}>")
            return "".join(out)

        return render_children(root)

    def qa_block(self, lines: List[str]) -> str:
        pairs: List[Tuple[str, str]] = []
        current_q = None
        current_a: List[str] = []
        for line in lines:
            match = QA_RE.match(line)
            if match:
                value = match.group(1)
                prefix = line.strip()
                if prefix.startswith(("Q", "پرسش")):
                    if current_q is not None:
                        pairs.append((current_q, " ".join(current_a).strip()))
                    current_q = value
                    current_a = []
                else:
                    current_a.append(value)
            elif current_q is not None and line.strip():
                current_a.append(line.strip())
        if current_q is not None:
            pairs.append((current_q, " ".join(current_a).strip()))

        if not pairs:
            return ""
        out = ['<div class="qa-list">']
        for question, answer in pairs:
            out.append(
                f'<details class="qa"><summary><span>{inline_md(question)}</span></summary>'
                f'<div class="qa-a"{direction_attr(answer)}>{inline_md(answer)}</div></details>'
            )
        out.append("</div>")
        return "\n".join(out)


# ---------------------------------------------------------------------------
# Front-matter
# ---------------------------------------------------------------------------

def parse_front_matter(text: str) -> Tuple[Dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not match:
        return {}, text
    meta: Dict[str, str] = {}
    for raw in match.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        meta[key.strip()] = value
    return meta, match.group(2)


def parse_tags(value: str) -> List[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return [item.strip().strip("\"'") for item in value.split(",") if item.strip()]


# ---------------------------------------------------------------------------
# Page templates
# ---------------------------------------------------------------------------

THEME_INIT = """<script>(function(){try{var t=localStorage.getItem("nlp-theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t);}catch(e){}})();</script>"""

ICON_SUN = '''<svg data-icon-sun viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true" style="display:none"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'''
ICON_MOON = '''<svg data-icon-moon viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5 8.5 8.5 0 1 0 20.5 14.2Z"/></svg>'''
ICON_PRINT = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9V3h12v6"/><path d="M6 18H4a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8" rx="1"/></svg>'''
ICON_BACK = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>'''
ICON_CAL = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/></svg>'''
ICON_CLOCK = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'''
ICON_USER = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>'''
ICON_TAG = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.6 13.4 12 22l-9-9V3h10l7.6 7.6a2 2 0 0 1 0 2.8Z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>'''


def session_page(meta: Dict[str, str], body: str, toc: List[Tuple[int, str, str]], prev_meta, next_meta) -> str:
    num = int(meta.get("session", "0"))
    num_fa = to_fa_digits(str(num).zfill(2)) if num else "—"
    title_fa = meta.get("title_fa", "جلسه")
    title_en = meta.get("title_en", "")
    date_fa = meta.get("date_fa", "")
    date_en = meta.get("date_en", meta.get("date", ""))
    summary = meta.get("summary_fa", "")
    lecturer = meta.get("lecturer", COURSE["instructor"])
    slides = meta.get("slides", "")
    reading = meta.get("reading", "")
    tags = parse_tags(meta.get("tags", ""))

    toc_items = []
    for level, text, heading_id in toc:
        cls = ' class="toc-sub"' if level == 3 else ""
        label = re.sub(r"[*`]", "", text.split(" | ")[0]).strip()
        toc_items.append(f'<li{cls}><a href="#{heading_id}">{esc(label)}</a></li>')
    toc_html = "\n".join(toc_items)

    mobile_toc = ""
    if toc_html:
        mobile_toc = (
            '<details class="toc-mobile"><summary>فهرست مطالب</summary>'
            f'<ol>{toc_html}</ol></details>'
        )

    tag_html = "".join(f'<span class="tag">{esc(tag)}</span>' for tag in tags)
    meta_bits = [f"<span>{ICON_USER}<span>{esc(lecturer)}</span></span>"]
    if date_fa:
        meta_bits.append(f"<span>{ICON_CAL}<span>{esc(date_fa)} · {esc(date_en)}</span></span>")
    if reading:
        meta_bits.append(f"<span>{ICON_CLOCK}<span>{esc(reading)}</span></span>")
    if slides:
        meta_bits.append(f"<span>{ICON_TAG}<span>اسلاید {esc(slides)}</span></span>")

    def nav_card(item, direction):
        if not item:
            return ""
        label = "جلسهٔ قبل" if direction == "prev" else "جلسهٔ بعد"
        return (
            f'<a class="{direction}" href="{item["file"]}">'
            f'<span class="sn-label">{label}</span>'
            f'<span class="sn-title">{esc(item["label"])}</span></a>'
        )

    prev_html = nav_card(prev_meta, "prev")
    next_html = nav_card(next_meta, "next")

    return f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title_fa)} — جلسه {num_fa} · {esc(COURSE['title_fa'])}</title>
<meta name="description" content="{esc(summary[:180])}">
<meta name="theme-color" content="#1d4ed8">
{THEME_INIT}
<link rel="icon" href="../assets/img/sbu-logo-favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../assets/css/site.css">
</head>
<body>
<a class="skip-link" href="#main">پرش به محتوای اصلی</a>
<div class="read-progress" data-read-progress aria-hidden="true"><span></span></div>

<header class="session-topbar">
  <div class="container inner">
    <span class="brand-logo brand-logo--sm" aria-hidden="true"><img src="../assets/img/sbu-logo.svg" alt=""></span>
    <a class="back" href="../notes.html">{ICON_BACK}<span>یادداشت‌ها</span></a>
    <div class="bar-title"><span class="mono">S{num_fa}</span>{esc(title_fa)}</div>
    <div class="actions">
      <button class="icon-btn" type="button" data-print aria-label="چاپ صفحه" title="چاپ صفحه">{ICON_PRINT}</button>
      <button class="icon-btn" type="button" data-theme-toggle aria-label="تغییر پوسته" title="تغییر پوسته">{ICON_MOON}{ICON_SUN}</button>
    </div>
  </div>
</header>

<main id="main" class="container">
  <div class="session-layout">
    <article class="session-main">
      <header class="session-hero">
        <nav class="breadcrumb" aria-label="مسیر">
          <a href="../index.html">خانه</a><span class="sep">/</span>
          <a href="../notes.html">یادداشت جلسات</a><span class="sep">/</span>
          <span>جلسه {num_fa}</span>
        </nav>
        <div class="session-kicker">
          <span class="badge badge--live">جلسه {num_fa}</span>
          <span class="tag tag--brand">{esc(COURSE['title_fa'])}</span>
        </div>
        <h1>{esc(title_fa)}</h1>
        <div class="h1-en" dir="ltr">{esc(title_en)}</div>
        {f'<div class="session-summary"><strong>خلاصه: </strong>{inline_md(summary)}</div>' if summary else ''}
        <div class="session-meta">{''.join(meta_bits)}</div>
      </header>

      {mobile_toc}

      <div class="prose">
{body}
      </div>

      <div class="session-foot-note">
        این صفحه یادداشت مطالعاتی دانشجویان بر اساس جلسهٔ کلاس است و جایگزین اعلام‌های رسمی استاد نیست.
        منبع اصلی درس: <span dir="ltr">Jurafsky &amp; Martin, Speech and Language Processing (3rd ed. draft)</span>.
        برای اصلاح یا تکمیل یادداشت‌ها، از طریق مخزن گیت‌هاب اقدام کنید.
      </div>

      <nav class="session-nav" aria-label="ناوبری جلسات">
        {prev_html}
        {next_html}
      </nav>
    </article>

    <aside class="toc" data-toc aria-label="فهرست مطالب">
      <div class="toc-title">در این صفحه</div>
      <ol>{toc_html}</ol>
    </aside>
  </div>
</main>

<footer class="site-footer">
  <div class="container">
    <div class="footer-brand" style="margin-bottom:14px">
      <span class="brand-logo" aria-hidden="true"><img src="../assets/img/sbu-logo.svg" alt=""></span>
      <span><strong>{esc(COURSE['title_fa'])}</strong><span>NLP · SBU</span></span>
    </div>
    <div class="footer-bottom" style="margin-top:0;border-top:0;padding-top:0">
      <span>© <span data-year>2026</span> — {esc(COURSE['title_fa'])} · {esc(COURSE['university'])}</span>
      <span class="mono">NLP · SBU</span>
    </div>
  </div>
</footer>
<script src="../assets/js/site.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Injections
# ---------------------------------------------------------------------------

def published_map() -> Dict[int, Dict[str, str]]:
    result: Dict[int, Dict[str, str]] = {}
    for path in sorted(CONTENT.glob("*.md")):
        meta, _ = parse_front_matter(path.read_text(encoding="utf-8"))
        try:
            num = int(meta.get("session", "0"))
        except ValueError:
            continue
        if num:
            meta["_file"] = f"session-{num:02d}.html"
            meta["_path"] = str(path)
            result[num] = meta
    return result


def schedule_rows(published: Dict[int, Dict[str, str]]) -> str:
    rows = []
    for num in sorted(published):
        meta = published[num]
        rows.append(
            "<tr>"
            f'<td class="cell-session"><span class="num">{to_fa_digits(str(num).zfill(2))}</span></td>'
            f'<td class="cell-topic"><span class="topic">{esc(meta.get("title_fa", "جلسه"))}</span>'
            f'<br><span class="small muted" dir="ltr">{esc(meta.get("title_en", ""))}</span></td>'
            f'<td class="cell-status"><a class="badge badge--live" href="sessions/session-{num:02d}.html">مطالعه</a></td>'
            "</tr>"
        )
    return "\n".join(rows)


def note_cards(published: Dict[int, Dict[str, str]], prefix: str = "") -> str:
    cards = []
    for num in sorted(published):
        meta = published[num]
        title_fa = meta.get("title_fa", "جلسه")
        title_en = meta.get("title_en", "")
        summary = meta.get("summary_fa", "")
        date_fa = meta.get("date_fa", "")
        reading = meta.get("reading", "—")
        tags = parse_tags(meta.get("tags", ""))
        tag_html = "".join(f'<span class="tag">{esc(tag)}</span>' for tag in tags[:3])
        search_blob = " ".join([title_fa, title_en, summary, " ".join(tags), date_fa])
        cards.append(f"""<a class="note-card" href="{prefix}sessions/session-{num:02d}.html" data-note-card data-tags="{esc(','.join(tags))}" data-search="{esc(search_blob)}">
  <div class="note-top">
    <span class="note-num">جلسه {to_fa_digits(str(num).zfill(2))}</span>
    {f'<span class="note-date">{esc(date_fa)}</span>' if date_fa else ""}
  </div>
  <h3>{esc(title_fa)}</h3>
  <p class="note-summary">{esc(summary)}</p>
  <div class="note-foot">
    {tag_html}
    <span class="note-arrow">مطالعه <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg></span>
  </div>
</a>""")
    return "\n".join(cards)


def inject(path: Path, start: str, end: str, value: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(text):
        print(f"  ! marker not found in {path.relative_to(ROOT)}")
        return False
    replacement = start + "\n" + value + "\n" + end
    path.write_text(pattern.sub(replacement, text), encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate only")
    args = parser.parse_args()

    if not CONTENT.exists():
        print(f"missing content directory: {CONTENT}")
        return 1

    published = published_map()
    if not published:
        print("no session markdown files found")
        return 1

    OUT.mkdir(exist_ok=True)
    errors = 0
    ordered = [published[n] for n in sorted(published)]

    for index, meta in enumerate(ordered):
        path = Path(meta["_path"])
        num = int(meta["session"])
        raw = path.read_text(encoding="utf-8")
        front, markdown = parse_front_matter(raw)
        if not front.get("title_fa"):
            print(f"  ! {path.name}: missing title_fa")
            errors += 1
            continue
        renderer = Renderer()
        body = renderer.render(markdown)
        prev_meta = None
        next_meta = None
        if index > 0:
            p = ordered[index - 1]
            prev_meta = {"file": f"session-{int(p['session']):02d}.html",
                         "label": f"جلسه {to_fa_digits(str(int(p['session'])).zfill(2))} — {p.get('title_fa', '')}"}
        if index + 1 < len(ordered):
            n = ordered[index + 1]
            next_meta = {"file": f"session-{int(n['session']):02d}.html",
                         "label": f"جلسه {to_fa_digits(str(int(n['session'])).zfill(2))} — {n.get('title_fa', '')}"}
        page = session_page(front, body, renderer.toc, prev_meta, next_meta)
        if not args.check:
            (OUT / f"session-{num:02d}.html").write_text(page, encoding="utf-8")
        print(f"  ✓ session {num:02d}: {front.get('title_fa')} ({len(renderer.toc)} headings)")

    if not args.check:
        rows = schedule_rows(published)
        cards = note_cards(published)
        inject(ROOT / "index.html", "<!-- SCHEDULE:START -->", "<!-- SCHEDULE:END -->", rows)
        inject(ROOT / "notes.html", "<!-- NOTE_CARDS:START -->", "<!-- NOTE_CARDS:END -->", cards)
        print(f"  ✓ injected {len(published)} session rows and note cards")

    if errors:
        print(f"\n{errors} error(s)")
        return 1
    print(f"\nBuilt {len(ordered)} session page(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
