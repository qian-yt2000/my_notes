#!/usr/bin/env python3
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
NOTES_DIR = ROOT / "notes"
OUTPUT_DIR = ROOT / "output"

# ── Markdown → HTML ────────────────────────────────────────────────────────
MD_EXTENSIONS = ["extra", "toc", "sane_lists"]


def md_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=MD_EXTENSIONS, output_format="html5")


# ── 提取元数据 ─────────────────────────────────────────────────────────────
def extract_title(md_text: str, filename: str) -> str:
    m = re.search(r"^#\s+(.+)", md_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return filename.replace(".md", "").replace("-", " ").replace("_", " ")


def extract_excerpt(md_text: str) -> str:
    lines = md_text.split("\n")
    in_heading = True
    for line in lines:
        if in_heading and (line.startswith("#") or line.strip() == ""):
            continue
        in_heading = False
        stripped = line.strip()
        if stripped:
            return stripped[:150]
    return ""


def extract_headings(body_html: str) -> list:
    """从生成的 body_html 中提取所有标题 (h1-h6) 及其 id"""
    headings = []
    for m in re.finditer(r'<h([1-6])\s+id="([^"]*)"[^>]*>(.*?)</h\1>', body_html, re.DOTALL):
        level = int(m.group(1))
        heading_id = m.group(2)
        text = re.sub(r'<[^>]*>', '', m.group(3)).strip()
        headings.append({"level": level, "id": heading_id, "text": text})
    return headings


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_note_page(title: str, body_html: str, all_notes: list, rel_prefix: str, headings: list = None) -> str:
    """rel_prefix: 从当前页面到 output/ 根的相对路径。笔记页用 '../' """
    if headings is None:
        headings = []
    nav_items = []
    for n in all_notes:
        active = ' class="active"' if n["title"] == title else ""
        href = n["slug"]  # 同目录，直接用文件名
        nav_items.append(f'<li><a href="{esc(href)}"{active}>{esc(n["title"])}</a></li>')

    nav_html = "\n".join(nav_items)

    # 构建 TOC HTML
    toc_items = []
    if headings:
        for h in headings:
            indent = "  " * (h["level"] - 1)
            toc_items.append(f'{indent}<li class="toc-item toc-lv{h["level"]}"><a href="#{esc(h["id"])}" class="toc-link">{esc(h["text"])}</a></li>')
    toc_html = "\n".join(toc_items)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} - My Notes</title>
<script>
  (function() {{
    var theme = localStorage.getItem('notes-theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
  }})();
</script>
<link rel="icon" type="image/x-icon" href="{rel_prefix}icon/title.ico">
<link rel="stylesheet" href="{rel_prefix}style.css">
</head>
<body>
<button class="sidebar-toggle" id="sidebarToggle" title="切换侧边栏">☰</button>
<div class="top-right-btns">
  <a href="{rel_prefix}index.html" class="home-btn" id="homeBtn" title="返回主目录"><img src="{rel_prefix}icon/homepage.svg" alt="首页"></a>
  <div class="theme-switch" id="themeSwitch" role="switch" aria-checked="false" aria-label="切换日/夜间模式" tabindex="0">
  <div class="theme-switch-track"></div>
  <div class="theme-switch-thumb">
    <img src="{rel_prefix}icon/sun.svg" alt="日间模式" id="themeIcon">
  </div>
</div>
</div>
<div class="layout">
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <h2><span class="sidebar-brand"><img src="{rel_prefix}icon/mynote.svg" class="sidebar-logo" alt=""> My Notes</span></h2>
      <button class="sidebar-collapse-btn" id="sidebarCollapseBtn" title="收起侧边栏">✕</button>
    </div>
    <div class="sidebar-section sidebar-section-toc" id="sidebarToc">
<h3 class="toc-title"><a href="{rel_prefix}home.html" class="sidebar-back" id="sidebarBack" title="返回主目录"><img src="{rel_prefix}icon/back.svg" alt="返回" style="width:16px;height:16px;vertical-align:middle;"></a>  目录</h3>
        {toc_html}
      </ul>
    </div>
    <div class="sidebar-section sidebar-section-nav" id="sidebarNav" style="display:none">
      <nav>
        <ul class="note-list">
          {nav_html}
        </ul>
      </nav>
    </div>
  </aside>
  <div class="sidebar-overlay" id="sidebarOverlay"></div>
  <main class="content" id="content">
    <article class="note">
      <h1>{esc(title)}</h1>
      <div class="note-body">
        {body_html}
      </div>
    </article>
  </main>
</div>
<script src="{rel_prefix}app.js"></script>
</body>
</html>"""


# ── 构建首页 ───────────────────────────────────────────────────────────────
# ── 构建封面页（index.html）───────────────────────────────────────────────
def build_cover_page() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>My Notes</title>
<link rel="icon" type="image/x-icon" href="icon/title.ico">
<link rel="stylesheet" href="style.css">
</head>
<body class="cover-page">
<div class="cover" id="cover">
  <div class="cover-overlay"></div>
  <div class="cover-stars" id="coverStars"></div>
  <div class="cover-hero">
    <div class="cover-bubble">
      <h1 class="cover-title">
        <span class="cover-title-text" id="coverTitleText"></span>
      </h1>
    </div>
    <div class="cover-actions">
      <button class="cover-btn" id="coverBtn">开始阅读</button>
    </div>
  </div>
  <div class="cover-scroll-hint" id="coverScrollHint" title="进入笔记">
    <svg viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.8)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M7 13l5 5 5-5"/>
      <path d="M7 7l5 5 5-5"/>
    </svg>
  </div>
</div>
<script src="app.js"></script>
</body>
</html>"""


# ── 构建笔记列表页（home.html）───────────────────────────────────────────
def build_home_page(all_notes: list) -> str:
    cards = []
    for n in all_notes:
        date_str = ""
        if n.get("date"):
            dt = datetime.fromtimestamp(n["date"])
            date_str = f'<time>{dt.strftime("%Y年%m月%d日")}</time>'
        cards.append(f"""
      <a href="notes/{esc(n["slug"])}" class="note-card">
        <h3>{esc(n["title"])}</h3>
        {date_str}
        <p>{esc(n["excerpt"])}</p>
      </a>""")

    cards_html = "\n".join(cards)
    nav_items = "\n".join(
        f'<li><a href="notes/{esc(n["slug"])}">{esc(n["title"])}</a></li>'
        for n in all_notes
    )
    empty_hint = (
        '<p class="empty">这个家伙很懒，什么也没留下</p>'
        if not all_notes else ""
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>My Notes</title>
<script>
  (function() {{
    var theme = localStorage.getItem('notes-theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
  }})();
</script>
<link rel="icon" type="image/x-icon" href="icon/title.ico">
<link rel="stylesheet" href="style.css">
</head>
<body>
<button class="sidebar-toggle" id="sidebarToggle" title="切换侧边栏">☰</button>
<div class="top-right-btns">
  <a href="index.html" class="home-btn" id="homeBtn" title="返回封面"><img src="icon/homepage.svg" alt="封面"></a>
  <div class="theme-switch" id="themeSwitch" role="switch" aria-checked="false" aria-label="切换日/夜间模式" tabindex="0">
  <div class="theme-switch-track"></div>
  <div class="theme-switch-thumb">
    <img src="icon/sun.svg" alt="日间模式" id="themeIcon">
  </div>
</div>
</div>
<div class="layout" id="mainContent">
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <h2><span class="sidebar-brand"><img src="icon/mynote.svg" class="sidebar-logo" alt=""> My Notes</span></h2>
      <button class="sidebar-collapse-btn" id="sidebarCollapseBtn" title="收起侧边栏">✕</button>
    </div>
    <div class="search-box">
      <input type="text" id="search" placeholder="搜索笔记..." autocomplete="off">
    </div>
    <nav>
      <ul class="note-list" id="noteList">
        {nav_items}
      </ul>
    </nav>
  </aside>
  <div class="sidebar-overlay" id="sidebarOverlay"></div>
  <main class="content">
    <div class="home">
      <h1><img src="icon/mynote.svg" class="home-logo" alt=""> My Notes</h1>
      <p class="subtitle">共 {len(all_notes)} 篇笔记</p>
      <div class="note-grid" id="noteGrid">
        {cards_html}
      </div>
      {empty_hint}
    </div>
  </main>
</div>
<script src="app.js"></script>
</body>
</html>"""


# ── CSS ────────────────────────────────────────────────────────────────────
CSS = r"""

/* ── 变量：日间模式 ──────────────────────────────── */
:root {
  --bg: #faf9f6;
  --sidebar-bg: #1e1e2e;
  --sidebar-text: #cdd6f4;
  --sidebar-hover: #313244;
  --sidebar-active: #45475a;
  --text: #2e2e2e;
  --text-muted: #6b6b6b;
  --accent: #4a86cf;
  --border: #e0e0e0;
  --card-bg: #ffffff;
  --card-shadow: 0 1px 3px rgba(0,0,0,0.08);
  --code-bg: #f0f0f0;
  --blockquote-border: #4a86cf;
  --blockquote-bg: rgba(74,134,207,0.05);
  --table-stripe: #fafafa;
  --table-header-bg: #f5f5f5;
  --toggle-bg: rgba(0,0,0,0.06);
  --toggle-text: #333;
}

/* ── 夜间模式 ────────────────────────────────────── */
[data-theme="dark"] {
  --bg: #1a1a2e;
  --sidebar-bg: #0f0f1a;
  --sidebar-text: #cdd6f4;
  --sidebar-hover: #1e1e30;
  --sidebar-active: #2a2a40;
  --text: #e0e0e0;
  --text-muted: #999;
  --accent: #7aa2f7;
  --border: #333;
  --card-bg: #22223a;
  --card-shadow: 0 1px 3px rgba(0,0,0,0.3);
  --code-bg: #2a2a3e;
  --blockquote-border: #7aa2f7;
  --blockquote-bg: rgba(122,162,247,0.08);
  --table-stripe: #2a2a3e;
  --table-header-bg: #2a2a3e;
  --toggle-bg: rgba(255,255,255,0.08);
  --toggle-text: #ddd;
}

/* ── Reset & Base ────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.75;
  font-size: 16px;
  transition: background 0.3s, color 0.3s;
  opacity: 0;
  animation: pageIn 0.35s ease both;
}
@keyframes pageIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
body.page-out {
  animation: pageOut 0.2s ease forwards;
}
@keyframes pageOut {
  from { opacity: 1; }
  to   { opacity: 0; }
}


a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* ── 右上角按钮组 ─────────────────────────────────── */
.top-right-btns {
  position: fixed;
  top: 16px;
  right: 24px;
  z-index: 100;
  display: flex;
  gap: 8px;
  align-items: center;
}

.home-btn {
  background: var(--toggle-bg);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  transition: background 0.2s, color 0.2s;
  padding: 10px;
}
.home-btn:hover { background: var(--card-bg); }
.home-btn img {
  width: 20px;
  height: 20px;
  display: block;
}

/* ── 主题切换开关 ────────────────────────────────── */
.theme-switch {
  position: relative;
  display: inline-block;
  width: 56px;
  height: 28px;
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  flex-shrink: 0;
}

.theme-switch-track {
  position: absolute;
  inset: 0;
  border-radius: 28px;
  background: #f3f4f6;
  transition: background 0.3s ease;
  box-shadow: inset 0 0 0 1px rgba(0,0,0,0.06);
}

[data-theme="dark"] .theme-switch-track {
  background: #2c2c34;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.08);
}

.theme-switch-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0,0,0,0.18), 0 1px 2px rgba(0,0,0,0.06);
}

[data-theme="dark"] .theme-switch-thumb {
  background: #fafafa;
  transform: translateX(28px);
  box-shadow: 0 1px 3px rgba(0,0,0,0.35), 0 1px 2px rgba(0,0,0,0.12);
}

.theme-switch-thumb img {
  width: 14px;
  height: 14px;
  display: block;
  pointer-events: none;
}

/* ── 侧边栏切换按钮 ──────────────────────────────── */
/* ── 侧边栏折叠按钮 ──────────────────────────────── */
.sidebar-toggle {
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 100;
  background: var(--toggle-bg);
  color: var(--toggle-text);
  border: 1px solid var(--border);
  border-radius: 8px;
  width: 40px;
  height: 40px;
  font-size: 18px;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, opacity 0.2s;
}
.sidebar-toggle:hover { background: var(--card-bg); }

/* 收起状态下，左上角显示汉堡呼出按钮 */
body.sidebar-collapsed .sidebar-toggle { display: flex; }
body.sidebar-open .sidebar-toggle { display: flex; }

/* ── 侧边栏内部关闭按钮 ──────────────────────────── */
.sidebar-collapse-btn {
  position: absolute;
  top: 18px;
  right: 14px;
  background: none;
  border: none;
  color: var(--sidebar-text);
  font-size: 16px;
  cursor: pointer;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  opacity: 0.6;
  transition: opacity 0.15s, background 0.15s;
}
.sidebar-collapse-btn:hover {
  opacity: 1;
  background: var(--sidebar-hover);
}

.sidebar-header {
  position: relative;
  padding: 24px 40px 12px 20px;
}
/* ── 侧边栏返回按钮 ──────────────────────────────── */
.sidebar-back {
  display: inline;
  background: none;
  color: var(--sidebar-text);
  border: none;
  font-size: 16px;
  font-family: inherit;
  cursor: pointer;
  padding: 0 2px;
  margin-right: 2px;
  opacity: 0.6;
  transition: opacity 0.15s;
  vertical-align: baseline;
}
.sidebar-back:hover { opacity: 1; }
.sidebar-back.done {
  opacity: 0.25;
  cursor: default;
  pointer-events: none;
}
.sidebar-back img {
  width: 16px;
  height: 16px;
  vertical-align: middle;
  filter: invert(1); 
}

/* 移动端始终用页面风格 */
@media (max-width: 768px) {
  .sidebar-toggle {
    background: var(--toggle-bg);
    color: var(--toggle-text);
    border: 1px solid var(--border);
  }
  .sidebar-toggle:hover { background: var(--card-bg); }
}

/* ── Layout ──────────────────────────────────────── */
.layout { display: flex; min-height: 100vh; }

/* ── 侧边栏 ──────────────────────────────────────── */
.sidebar {
  width: 260px;
  min-width: 260px;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  overflow-y: auto;
  z-index: 50;
  transition: transform 0.3s ease;
}

.sidebar-header { position: relative; padding: 24px 40px 12px 20px; border-bottom: 1px solid rgba(255,255,255,0.08); }
.sidebar-header h2 { font-size: 18px; font-weight: 600; }
.sidebar-header a { color: var(--sidebar-text); }
.sidebar-brand { color: var(--sidebar-text); cursor: default; }
/* ── 侧边栏 Logo ────────────────────────────────── */
.sidebar-logo {
  width: 20px;
  height: 20px;
  vertical-align: -3px;
  margin-right: 6px;
}
.home-logo {
  width: 28px;
  height: 28px;
  vertical-align: -6px;
  margin-right: 6px;
}

.search-box { padding: 12px 16px; }
.search-box input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px;
  background: rgba(255,255,255,0.06);
  color: var(--sidebar-text);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}
.search-box input:focus { border-color: var(--accent); }
.search-box input::placeholder { color: rgba(255,255,255,0.3); }

.sidebar nav { flex: 1; overflow-y: auto; padding: 8px 0; }

.note-list { list-style: none; }
.note-list li a {
  display: block;
  padding: 8px 20px;
  font-size: 14px;
  color: var(--sidebar-text);
  transition: background 0.15s;
  border-left: 3px solid transparent;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.note-list li a:hover { background: var(--sidebar-hover); text-decoration: none; }
.note-list li a.active {
  background: var(--sidebar-active);
  border-left-color: var(--accent);
}

/* ── 侧边栏分区 ──────────────────────────────────── */
.sidebar-section { padding: 0 16px 16px; overflow-y: auto; flex: 1; }

.toc-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,0.45);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 16px 4px 10px;
}

/* 侧边栏 TOC 列表 */
.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.toc-item {
  list-style: none;
}
.toc-link {
  display: block;
  padding: 4px 8px;
  font-size: 13px;
  color: var(--sidebar-text);
  opacity: 0.75;
  text-decoration: none;
  border-radius: 4px;
  transition: background 0.15s, opacity 0.15s, border-color 0.15s, padding-left 0.15s;
}
.toc-link:hover {
  opacity: 1;
  background: var(--sidebar-hover);
  text-decoration: none;
}
/* 高亮当前阅读位置 */
.toc-link.active {
  background: var(--sidebar-active);
  opacity: 1;
  font-weight: 600;
  border-left: 3px solid var(--accent);
  padding-left: 5px;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05);
}
/* TOC 缩进 */
.toc-lv2 { padding-left: 12px; }
.toc-lv3 { padding-left: 24px; }
.toc-lv4 { padding-left: 36px; }
.toc-lv5 { padding-left: 48px; }
.toc-lv6 { padding-left: 60px; }


.sidebar-footer {
  padding: 16px 20px;
  font-size: 12px;
  opacity: 0.5;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.sidebar-footer code {
  background: rgba(255,255,255,0.08);
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 11px;
}

/* ── 侧边栏遮罩 ──────────────────────────────────── */
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 45;
}

/* ── 侧边栏折叠状态 ──────────────────────────────── */
body.sidebar-collapsed .sidebar {
  transform: translateX(-100%);
}
body.sidebar-collapsed .sidebar-overlay { display: none; }
body.sidebar-collapsed .sidebar-toggle { display: flex; }

/* 大屏下始终显示切换按钮，方便折叠 */


/* ── 内容区 ──────────────────────────────────────── */
.content {
  margin-left: 260px;
  flex: 1;
  padding: 40px 48px;
  padding-top: 64px;
  max-width: 880px;
  transition: margin-left 0.3s ease;
}
body.sidebar-collapsed .content { margin-left: 0; }
body.sidebar-collapsed .layout { padding-left: 0; }

/* ── 首页 ────────────────────────────────────────── */
.home h1 { font-size: 28px; margin-bottom: 4px; }
.subtitle { color: var(--text-muted); margin-bottom: 32px; }

.empty { text-align: center; color: var(--text-muted); padding: 60px 0; }
.empty code { background: var(--code-bg); padding: 2px 6px; border-radius: 3px; font-size: 14px; }

.note-grid { display: flex; flex-direction: column; gap: 16px; }

.note-card {
  display: block;
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px 24px;
  color: var(--text);
  box-shadow: var(--card-shadow);
  transition: box-shadow 0.2s, transform 0.15s, background 0.3s;
}
.note-card:hover {
  box-shadow: 0 4px 14px rgba(0,0,0,0.12);
  transform: translateY(-1px);
  text-decoration: none;
}
.note-card h3 { font-size: 18px; margin-bottom: 4px; color: var(--accent); }
.note-card time { font-size: 13px; color: var(--text-muted); display: block; margin-bottom: 8px; }
.note-card p {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ── 笔记正文 ────────────────────────────────────── */
.note h1 { font-size: 28px; margin-bottom: 32px; padding-bottom: 12px; border-bottom: 2px solid var(--border); }

.note-body h2 { font-size: 22px; margin: 36px 0 14px; }
.note-body h3 { font-size: 18px; margin: 28px 0 10px; }
.note-body h4, .note-body h5, .note-body h6 { margin: 24px 0 8px; }

.note-body p { margin-bottom: 16px; }

.note-body ul {
  list-style: none;
  padding-left: 0;
}
.note-body ol {
  padding-left: 24px;  /* 有序列表保留编号和缩进 */
}
.note-body li {
  margin-bottom: 4px;
}
.note-body code {
  background: var(--code-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: "SF Mono", "Fira Code", "Consolas", monospace;
}

.note-body pre {
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 20px 24px;
  border-radius: 10px;
  overflow-x: auto;
  margin-bottom: 20px;
  font-size: 14px;
  line-height: 1.6;
}
.note-body pre code {
  background: none;
  padding: 0;
  color: inherit;
  font-size: inherit;
}

.note-body blockquote {
  border-left: 4px solid var(--blockquote-border);
  padding: 8px 20px;
  margin: 0 0 20px;
  background: var(--blockquote-bg);
  border-radius: 0 8px 8px 0;
  color: var(--text-muted);
}

.note-body hr { border: none; border-top: 1px solid var(--border); margin: 32px 0; }

.note-body img { max-width: 100%; border-radius: 8px; margin: 16px 0; }

.note-body a { text-decoration: underline; text-underline-offset: 2px; }

.note-body strong { font-weight: 600; }

.note-body table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
  font-size: 14px;
}
.note-body th, .note-body td {
  padding: 10px 14px;
  border: 1px solid var(--border);
  text-align: left;
}
.note-body th { background: var(--table-header-bg); font-weight: 600; }
.note-body tr:nth-child(even) td { background: var(--table-stripe); }

/* ── 响应式 ──────────────────────────────────────── */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    box-shadow: 2px 0 12px rgba(0,0,0,0.3);
  }
  body.sidebar-open .sidebar { transform: translateX(0); }
  body.sidebar-open .sidebar-overlay { display: block; }
  .sidebar-toggle { display: flex; }
  .content {
    margin-left: 0;
    padding: 20px 16px;
    padding-top: 56px;
    max-width: 100%;
  }
  body.sidebar-collapsed .content { margin-left: 0; }
body.sidebar-collapsed .layout { padding-left: 0; }
}


/* ── 封面 ────────────────────────────────────────── */
.cover {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 200;
  background: #1a1a2e url('fengmian.png') center/cover no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.5s ease, visibility 0.5s ease;
}
/* ???????? */
.cover::before,
.cover::after {
  content: '';
  position: absolute;
  top: 0; bottom: 0;
  width: 15%;
  z-index: 199;
  pointer-events: none;
}
.cover::before {
  left: 0;
  background: linear-gradient(to right, #1a1a2e 0%, transparent 100%);
}
.cover::after {
  right: 0;
  background: linear-gradient(to left, #1a1a2e 0%, transparent 100%);
}

/* ── 封面 Hero ─────────────────────────────────── */
.cover-hero {
  position: relative;
  z-index: 220;
  text-align: center;
  padding: 0 24px;
}
/* ????????? */
.cover-bubble {
  display: inline-block;
  padding: 28px 44px;
  background: rgba(255,255,255,0.01);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  opacity: 0;
  transform: translateY(16px);
  animation: bubbleIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards,
             bubbleFloat 4s ease-in-out 1.5s infinite;
}
@keyframes bubbleFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
@keyframes bubbleIn {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── 渐变标题 ──────────────────────────────────── */
.cover-title {
  margin: 0;
  font-size: clamp(28px, 5vw, 48px);
  font-weight: 800;
  line-height: 1.4;
  letter-spacing: 6px;
  font-family: "Noto Serif SC", "STSong", "SimSun", "Songti SC", serif;
  color: #f5d76e;
  text-shadow: 0 2px 12px rgba(245,215,110,0.3);
  animation: titleGlow 3s ease-in-out 1.5s infinite;
}
@keyframes titleGlow {
  0%, 100% { text-shadow: 0 2px 12px rgba(245,215,110,0.3); }
  50% { text-shadow: 0 2px 24px rgba(245,215,110,0.6), 0 0 40px rgba(245,215,110,0.2); }
}
.cover-title-text {
  color: #f5d76e;
}
.cover-title-char {
  display: inline-block;
  opacity: 0;
  color: inherit;
  font-family: inherit;
  animation: charPop 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes charPop {
  0%   { opacity: 0; transform: translateY(12px) scale(0.6); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}
.cover-star-emoji {
  display: inline-block;
  opacity: 0;
  font-size: 0.85em;
  animation: starBlink 0.4s ease forwards;
  animation-delay: var(--star-delay, 1.5s);
}
@keyframes starBlink {
  0%, 50% { opacity: 0; transform: scale(0.3); }
  70% { opacity: 1; transform: scale(1.3); }
  100% { opacity: 1; transform: scale(1); }
}

/* ── 副标题 ────────────────────────────────────── */


/* ── 按钮区 ────────────────────────────────────── */
.cover-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 36px;
}
.cover-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 42px;
  font-size: clamp(14px, 2.5vw, 17px);
  font-family: inherit;
  color: #1a1a2e;
  background: linear-gradient(135deg, #f5d76e, #f0a060);
  border: none;
  border-radius: 28px;
  cursor: pointer;
  letter-spacing: 2px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 4px 24px rgba(240,192,64,0.35);
  position: relative;
}
.cover-btn::after {
  content: "→";
  font-size: 1.2em;
  transition: transform 0.3s ease;
}
.cover-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 36px rgba(240,192,64,0.5);
}
.cover-btn:hover::after {
  transform: translateX(4px);
}

/* ── 封面星星容器 ──────────────────────────────── */
.cover-stars {
  position: absolute;
  inset: 0;
  z-index: 205;
  pointer-events: none;
  overflow: hidden;
}

/* ── 流星 ──────────────────────────────────────── */
.cover-star {
  position: absolute;
  width: 3px;
  height: 3px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 0 8px 3px rgba(255,240,180,0.8);
  animation: shoot var(--dur, 1.5s) ease-out forwards;
  pointer-events: none;
}
.cover-star::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  width: 100px;
  height: 2px;
  background: linear-gradient(to right, rgba(255,240,180,0.9), transparent 70%);
  transform: translateY(-50%) rotate(-40deg);
  transform-origin: left center;
}
@keyframes shoot {
  0%   { transform: translate(0, 0) scale(1); opacity: 1; }
  100% { transform: translate(-130vw, 80vh) scale(0.1); opacity: 0; }
}
.cover-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.35);
  pointer-events: none;
}
.cover-hidden {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition: opacity 0.5s ease, visibility 0.5s ease;
}
/* ???????????????? */
#mainContent.cover-active {
  opacity: 0;
  visibility: hidden;
}

/* --- ?????? --- */
.cover-scroll-hint {
  position: absolute;
  bottom: 36px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 210;
  cursor: pointer;
  animation: bounceDown 2s ease-in-out infinite;
  opacity: 0.55;
  transition: opacity 0.3s;
}
.cover-scroll-hint:hover { opacity: 0.9; }
.cover-scroll-hint svg {
  width: 32px;
  height: 32px;
}
@keyframes bounceDown {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(10px); }
}
@media (max-width: 768px) {
  .cover-btn { padding: 12px 36px; font-size: 16px; }
}

"""

# ── JavaScript ─────────────────────────────────────────────────────────────

JS = r"""

(function() {
// ── 主题切换 ──────────────────────────────────────
  var themeSwitch = document.getElementById("themeSwitch");
  var themeIcon = document.getElementById("themeIcon");
  var savedTheme = localStorage.getItem("notes-theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateSwitchState(savedTheme);

  function updateSwitchState(theme) {
    if (themeIcon) {
      themeIcon.src = theme === "dark" ? iconPath("moon.svg") : iconPath("sun.svg");
      themeIcon.alt = theme === "dark" ? "夜间模式" : "日间模式";
    }
    if (themeSwitch) {
      themeSwitch.setAttribute("aria-checked", theme === "dark" ? "true" : "false");
    }
  }

  // 根据当前页面位置计算图标路径
  function iconPath(name) {
    var path = window.location.pathname;
    if (path.indexOf("/notes/") !== -1) {
      return "../icon/" + name;
    }
    return "icon/" + name;
  }

  if (themeSwitch) {
    themeSwitch.addEventListener("click", function() {
      var current = document.documentElement.getAttribute("data-theme");
      var next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("notes-theme", next);
      updateSwitchState(next);
    });

    themeSwitch.addEventListener("keydown", function(e) {
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        this.click();
      }
    });
  }


  // ── 侧边栏折叠 ────────────────────────────────
  var sidebarToggle = document.getElementById("sidebarToggle");
  var sidebar = document.getElementById("sidebar");
  var overlay = document.getElementById("sidebarOverlay");
  var isMobile = window.innerWidth <= 768;

  // 移动端默认收起，桌面端记住偏好
  var savedCollapsed = localStorage.getItem("notes-sidebar-collapsed");
  if (savedCollapsed === "true" || (isMobile && savedCollapsed !== "false")) {
    document.body.classList.add("sidebar-collapsed");
    document.body.classList.remove("sidebar-open");
  }

  function toggleSidebar() {
    if (isMobile) {
      // 移动端：展开/收起覆盖层
      if (document.body.classList.contains("sidebar-open")) {
        document.body.classList.remove("sidebar-open");
      } else {
        document.body.classList.add("sidebar-open");
      }
      document.body.classList.remove("sidebar-collapsed");
    } else {
      // 桌面端：折叠/展开
      document.body.classList.toggle("sidebar-collapsed");
      document.body.classList.remove("sidebar-open");
      var collapsed = document.body.classList.contains("sidebar-collapsed");
      localStorage.setItem("notes-sidebar-collapsed", collapsed ? "true" : "false");
    }
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", toggleSidebar);
  }

  // ── 侧边栏内部折叠按钮 ──────────────────────────
  var sidebarCollapseBtn = document.getElementById("sidebarCollapseBtn");
  if (sidebarCollapseBtn) {
    sidebarCollapseBtn.addEventListener("click", toggleSidebar);
  }

  if (overlay) {
    overlay.addEventListener("click", function() {
      document.body.classList.remove("sidebar-open");
    });
  }

  window.addEventListener("resize", function() {
    var wasMobile = isMobile;
    isMobile = window.innerWidth <= 768;
    if (wasMobile !== isMobile) {
      document.body.classList.remove("sidebar-open");
      if (!isMobile) {
        var c = localStorage.getItem("notes-sidebar-collapsed");
        if (c === "true") document.body.classList.add("sidebar-collapsed");
        else document.body.classList.remove("sidebar-collapsed");
      }
    }
  });

  // ── 搜索 ──────────────────────────────────────
  var search = document.getElementById("search");
  if (search) {
    search.addEventListener("input", function() {
      var q = this.value.toLowerCase();
      var grid = document.getElementById("noteGrid");
      var list = document.getElementById("noteList");
      if (grid) {
        grid.querySelectorAll(".note-card").forEach(function(c) {
          var title = (c.querySelector("h3") || {}).textContent || "";
          var excerpt = (c.querySelector("p") || {}).textContent || "";
          c.style.display = (title + excerpt).toLowerCase().includes(q) ? "" : "none";
        });
      }
      if (list) {
        list.querySelectorAll("li").forEach(function(li) {
          li.style.display = li.textContent.toLowerCase().includes(q) ? "" : "none";
        });
      }
    });
  }
  // ── 封面交互 ──────────────────────────────────
    var cover = document.getElementById("cover");
  if (cover) {
    var bgImages = [
      "icon/bg1.webp",
      "icon/bg2.webp",
      "icon/bg3.webp",
      "icon/bg4.webp",
      "icon/bg5.webp"
    ];
    var randomBg = bgImages[Math.floor(Math.random() * bgImages.length)];

    cover.style.backgroundImage = 'url("' + randomBg + '")';
    cover.style.backgroundSize = 'cover';
    cover.style.backgroundPosition = 'center';
    cover.style.backgroundRepeat = 'no-repeat';

  }
  // 流星生成器
  (function() {
    var container = document.getElementById("coverStars");
    if (!container) return;
    function spawn() {
      var star = document.createElement("div");
      star.className = "cover-star";
      var top = Math.random() * 25;
      var left = 70 + Math.random() * 25;
      star.style.top = top + "%";
      star.style.left = left + "%";
      var dur = 2 + Math.random() * 0.6;
      star.style.setProperty("--dur", dur + "s");
      container.appendChild(star);
      setTimeout(function() { if (star.parentNode) star.parentNode.removeChild(star); }, dur * 1000 + 200);
    }
    function schedule() {
      spawn();
      setTimeout(schedule, 3000 + Math.random() * 1000);
    }
    setTimeout(schedule, 1500);
  })();

  var coverBtn = document.getElementById("coverBtn");

  // 封面标题逐字动画
    // 封面标题逐字动画（随机选择）
  var titleEl = document.getElementById("coverTitleText");
  if (titleEl) {
    // ── 预设标题列表（可自由增删） ──
    var quotes = [
      "循此苦旅，以抵繁星~",
      "学无止境，行以致远~",
      "千里之行，始于足下~"
    ];
    var randomIndex = Math.floor(Math.random() * quotes.length);
    var titleText = quotes[randomIndex];

    // 逐字动画（与原逻辑完全一致）
    var chars = titleText.split("");
    var totalDelay = 0;
    chars.forEach(function(ch, i) {
      var span = document.createElement("span");
      span.className = "cover-title-char";
      span.textContent = ch;
      var delay = 0.6 + i * 0.08;
      span.style.animationDelay = delay + "s";
      titleEl.appendChild(span);
      totalDelay = delay + 0.35;
    });
    var star = document.createElement("span");
    star.className = "cover-star-emoji";
    star.textContent = "⭐";
    star.style.setProperty("--star-delay", (totalDelay + 0.15) + "s");
    titleEl.appendChild(star);
  }

  // 进入笔记列表页
  function goToHome() {
    smoothNavigate("home.html");
  }

  if (coverBtn) {
    coverBtn.addEventListener("click", function(e) {
      e.preventDefault();
      goToHome();
    });
  }

  if (cover) {
    cover.addEventListener("wheel", function(e) {
      if (e.deltaY > 0) {
        goToHome();
      }
    }, { passive: true });
  }

  // 下滑箭头点击进入
  var scrollHint = document.getElementById("coverScrollHint");
  if (scrollHint) {
    scrollHint.addEventListener("click", function(e) {
      e.preventDefault();
      goToHome();
    });
  }

  // ── TOC 点击平滑滚动 ────────────────────────────
  var tocLinks = document.querySelectorAll(".toc-link");
  tocLinks.forEach(function(link) {
    link.addEventListener("click", function(e) {
      e.preventDefault();
      var targetId = this.getAttribute("href").substring(1);
      var target = document.getElementById(targetId);
      if (target) {
        target.scrollIntoView({ behavior: "smooth" });
        if (window.innerWidth <= 768) {
          document.body.classList.remove("sidebar-open");
        }
      }
    });
  });

  // ═══════════════════════════════════════════════════════
  // ★ 新增：TOC 滚动高亮当前阅读位置
  // ═══════════════════════════════════════════════════════
  function initTocHighlight() {
    var tocLinks = document.querySelectorAll('.toc-link');
    if (tocLinks.length === 0) return;

    // 收集标题元素与其对应的 TOC 链接
    var headingMap = [];
    tocLinks.forEach(function(link) {
      var targetId = link.getAttribute('href').substring(1);
      var heading = document.getElementById(targetId);
      if (heading) {
        headingMap.push({
          heading: heading,
          link: link
        });
      }
    });

    if (headingMap.length === 0) return;

    // 使用 Intersection Observer 检测标题进入视口
    var observer = new IntersectionObserver(function(entries) {
      // 收集当前可见的标题（至少 30% 可见）
      var visibleHeadings = entries
        .filter(function(entry) {
          return entry.isIntersecting && entry.intersectionRatio >= 0.3;
        })
        .map(function(entry) {
          return entry.target;
        });

      if (visibleHeadings.length === 0) {
        // 如果没有标题可见（滚动到顶部或底部），则根据滚动位置选择最接近的
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        var closest = null;
        var minDist = Infinity;
        headingMap.forEach(function(item) {
          var rect = item.heading.getBoundingClientRect();
          var dist = Math.abs(rect.top);
          if (dist < minDist) {
            minDist = dist;
            closest = item;
          }
        });
        if (closest) {
          setActiveLink(closest.link);
        }
        return;
      }

      // 选择第一个可见标题（按 DOM 顺序）
      var firstVisible = visibleHeadings[0];
      var activeItem = null;
      for (var i = 0; i < headingMap.length; i++) {
        if (headingMap[i].heading === firstVisible) {
          activeItem = headingMap[i];
          break;
        }
      }
      if (activeItem) {
        setActiveLink(activeItem.link);
      }
    }, {
      threshold: [0.3, 0.5, 0.7],
      rootMargin: '0px 0px -10% 0px'
    });

    headingMap.forEach(function(item) {
      observer.observe(item.heading);
    });

    // 初始高亮
    requestAnimationFrame(function() {
      var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      var activeItem = null;
      for (var i = 0; i < headingMap.length; i++) {
        var rect = headingMap[i].heading.getBoundingClientRect();
        if (rect.top >= 0 && rect.top < window.innerHeight * 0.7) {
          activeItem = headingMap[i];
          break;
        }
      }
      if (!activeItem && headingMap.length > 0) {
        activeItem = headingMap[headingMap.length - 1];
      }
      if (activeItem) {
        setActiveLink(activeItem.link);
      }
    });

    function setActiveLink(activeLink) {
      tocLinks.forEach(function(link) {
        link.classList.remove('active');
      });
      activeLink.classList.add('active');
    }
  }

  // 在页面加载完成后初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTocHighlight);
  } else {
    initTocHighlight();
  }
  // ═══════════════════════════════════════════════════════

  // ── 侧边栏返回键 → 笔记列表页 ─────────────────
  var sidebarBack = document.getElementById("sidebarBack");
  if (sidebarBack) {
    sidebarBack.addEventListener("click", function(e) {
      e.preventDefault();
      var path = window.location.pathname;
      var homeHref = path.indexOf("/notes/") !== -1 ? "../home.html" : "home.html";
      smoothNavigate(homeHref);
    });
  }

  // ── 首页按钮（右上角小房子）───────────────────
  var homeBtn = document.getElementById("homeBtn");
  if (homeBtn) {
    homeBtn.addEventListener("click", function(e) {
      e.preventDefault();
      var href = this.getAttribute("href");
      smoothNavigate(href);
    });
  }

  function smoothNavigate(href) {
    document.body.classList.add("page-out");
    setTimeout(function() {
      window.location.href = href;
    }, 200);
  }

  var noteCards = document.querySelectorAll(".note-card");
  noteCards.forEach(function(card) {
    card.addEventListener("click", function(e) {
      var href = this.getAttribute("href");
      if (href && href !== "#" && href !== window.location.href) {
        e.preventDefault();
        smoothNavigate(href);
      }
    });
  });

  var noteListLinks = document.querySelectorAll("#noteList a");
  noteListLinks.forEach(function(link) {
    link.addEventListener("click", function(e) {
      var href = this.getAttribute("href");
      if (href && href !== "#" && href !== window.location.href) {
        e.preventDefault();
        smoothNavigate(href);
      }
    });
  });

  var sidebarNavLinks = document.querySelectorAll("#sidebarNav a");
  sidebarNavLinks.forEach(function(link) {
    link.addEventListener("click", function(e) {
      var href = this.getAttribute("href");
      if (href && href !== "#" && href !== window.location.href) {
        e.preventDefault();
        smoothNavigate(href);
      }
    });
  });

})();

"""


# ── 构建主流程 ─────────────────────────────────────────────────────────────
def build():
    print("[BUILD] 开始构建笔记网站...\n")

    out_notes_dir = OUTPUT_DIR / "notes"

    # ★ 关键修改：清空 output/notes/ 目录，确保删除旧笔记页
    if out_notes_dir.exists():
        shutil.rmtree(out_notes_dir)
    out_notes_dir.mkdir(parents=True, exist_ok=True)

    # 复制封面图片
    cover_src = ROOT / "fengmian.png"
    if cover_src.exists():
        shutil.copy2(cover_src, OUTPUT_DIR / "fengmian.png")
        print("  [OK] fengmian.png 封面")

    # 复制图标
    icon_src = ROOT / "icon"
    icon_dst = OUTPUT_DIR / "icon"
    if icon_src.exists():
        if icon_dst.exists():
            shutil.rmtree(icon_dst)
        shutil.copytree(icon_src, icon_dst)
        print("  [OK] icon/ (sun.svg, moon.svg)")

    # 写入 CSS
    (OUTPUT_DIR / "style.css").write_text(CSS, encoding="utf-8")
    print("  [OK] style.css")

    # 写入 JS
    (OUTPUT_DIR / "app.js").write_text(JS, encoding="utf-8")
    print("  [OK] app.js")

    # 读取所有 .md 文件
    note_files = sorted(f for f in NOTES_DIR.iterdir() if f.suffix == ".md")

    if not note_files:
        print("  [WARN] notes/ 目录中没有 .md 文件，将生成空的首页。")

    all_notes = []

    # 第一遍：收集元数据
    for filepath in note_files:
        raw = filepath.read_text(encoding="utf-8")
        if raw and ord(raw[0]) == 0xFEFF:
            raw = raw[1:]
        title = extract_title(raw, filepath.name)
        excerpt = extract_excerpt(raw)
        slug = filepath.stem + ".html"

        all_notes.append({
            "file": filepath.name,
            "title": title,
            "excerpt": excerpt,
            "slug": slug,
            "url": f"notes/{slug}",
            "date": filepath.stat().st_mtime,
            "raw": raw,
        })

    # 第二遍：生成笔记页面
    for note in all_notes:
        body_html = md_to_html(note["raw"])
        headings = extract_headings(body_html)
        page_html = build_note_page(note["title"], body_html, all_notes, rel_prefix="../", headings=headings)
        (out_notes_dir / note["slug"]).write_text(page_html, encoding="utf-8")
        print(f"  [OK] notes/{note['slug']}  (- {note['title']})")

    # 生成封面页
    cover_html = build_cover_page()
    (OUTPUT_DIR / "index.html").write_text(cover_html, encoding="utf-8")
    print("  [OK] index.html (封面页)")

    # 生成笔记列表页
    home_html = build_home_page(all_notes)
    (OUTPUT_DIR / "home.html").write_text(home_html, encoding="utf-8")
    print("  [OK] home.html (列表页)")

    print(f"\n[DONE] 构建完成！共 {len(all_notes)} 篇笔记。")
    print(f"   打开 output/index.html 即可预览（封面页）。")
    print(f"   笔记列表页：output/home.html")


if __name__ == "__main__":
    build()