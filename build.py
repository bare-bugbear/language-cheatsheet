#!/usr/bin/env python3
"""Build index.html (filterable cheat sheet) from README.md.

README.md is the single source of truth. After editing the table, run:
    python3 build.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"
OUTPUT = ROOT / "index.html"


def split_cells(line: str) -> list[str]:
    """Split a Markdown table row, honouring escaped pipes inside cells."""
    protected = line.replace("\\|", "\x00")
    parts = protected.split("|")
    if parts[0] != "" or parts[-1].strip() != "":
        raise ValueError(f"malformed table row: {line[:80]}")
    return [p.strip().replace("\x00", "|") for p in parts[1:-1]]


def clean(cell: str) -> str:
    # Markdown formatters may rewrite <br> as <br /> and &nbsp; as a literal NBSP.
    cell = re.sub(r"<br\s*/?>", "\n", cell, flags=re.IGNORECASE)
    return cell.replace("&nbsp;", "\u00a0")


def parse() -> dict:
    rows = [l for l in README.read_text(encoding="utf-8").splitlines() if l.startswith("|")]
    if len(rows) < 3:
        raise ValueError("no Markdown table found in README.md")

    header = split_cells(rows[0])
    languages = header[1:]
    if not languages:
        raise ValueError("no language columns found")

    sections: list[dict] = []
    current: dict | None = None
    for line in rows[2:]:
        cells = split_cells(line)
        first, rest = cells[0], cells[1:]
        if len(rest) != len(languages):
            raise ValueError(
                f"column mismatch ({len(rest)} != {len(languages)}): {first}"
            )
        if first.startswith("**") and first.endswith("**"):
            current = {"name": first.strip("*"), "rows": []}
            sections.append(current)
        elif first.startswith(":"):
            continue
        else:
            if current is None:
                raise ValueError(f"row outside a section: {first}")
            current["rows"].append(
                {"feature": first, "cells": [clean(c) for c in rest]}
            )

    if not sections or not any(s["rows"] for s in sections):
        raise ValueError("no feature rows parsed")
    return {"languages": languages, "sections": sections}


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Language Cheatsheet</title>
<style>
:root {
  --bg:#f6f7f9; --panel:#ffffff; --text:#111827; --muted:#6b7280;
  --border:#e5e7eb; --code-bg:#f1f5f9; --code-fg:#0f172a;
  --accent:#2563eb; --section:#f8fafc; --hover:#eff6ff;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}
[data-theme="dark"] {
  --bg:#0f172a; --panel:#1e293b; --text:#e2e8f0; --muted:#94a3b8;
  --border:#334155; --code-bg:#0b1220; --code-fg:#e2e8f0;
  --accent:#60a5fa; --section:#172033; --hover:#1e3a5f;
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }
.app { max-width:1680px; margin:0 auto; padding:22px 22px 36px; }
.top { display:flex; align-items:center; gap:16px; margin-bottom:16px; flex-wrap:wrap; }
h1 { font-size:23px; margin:0 0 3px; letter-spacing:-.4px; }
.sub { margin:0; font-size:13px; color:var(--muted); }
.stat { margin-left:auto; font-size:12px; color:var(--muted); }
.ghost { border:1px solid var(--border); background:var(--panel); color:var(--text);
  border-radius:8px; padding:7px 13px; font-size:12px; cursor:pointer; }
.ghost:hover { border-color:var(--accent); color:var(--accent); }
.controls { background:var(--panel); border:1px solid var(--border); border-radius:12px;
  padding:14px 16px; margin-bottom:14px; }
.search-row { display:flex; align-items:center; gap:12px; margin-bottom:11px; flex-wrap:wrap; }
#search { flex:1 1 320px; max-width:440px; padding:8px 12px; font-size:13px;
  border:1px solid var(--border); border-radius:8px; background:var(--bg); color:var(--text); }
#search:focus { outline:none; border-color:var(--accent); box-shadow:0 0 0 2px rgba(37,99,235,.15); }
.hint { font-size:12px; color:var(--muted); }
.chips { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px; }
.chip { border:1px solid var(--border); background:var(--panel); color:var(--muted);
  border-radius:999px; padding:5px 12px; font-size:12px; cursor:pointer;
  transition:background .12s,color .12s,border-color .12s; }
.chip:hover { border-color:var(--accent); }
.chip.on { background:var(--accent); border-color:var(--accent); color:#fff; }
.presets { display:flex; flex-wrap:wrap; gap:6px; align-items:center; }
.presets .label { font-size:12px; color:var(--muted); margin-right:2px; }
.presets button { font-size:11px; padding:4px 9px; border:1px solid var(--border);
  background:var(--bg); color:var(--muted); border-radius:6px; cursor:pointer; }
.presets button:hover { color:var(--accent); border-color:var(--accent); }
.table-wrap { background:var(--panel); border:1px solid var(--border); border-radius:12px;
  overflow:auto; max-height:70vh; }
table { border-collapse:separate; border-spacing:0; width:max-content; min-width:100%; font-size:12.5px; }
th, td { border-bottom:1px solid var(--border); border-right:1px solid var(--border);
  padding:9px 11px; text-align:left; vertical-align:top; }
thead th { position:sticky; top:0; z-index:5; background:var(--section);
  font-weight:600; font-size:12px; white-space:nowrap; }
thead th.lang-col { cursor:pointer; }
thead th.lang-col:hover { color:var(--accent); }
.th-hint { display:block; font-weight:400; font-size:10px; color:var(--muted); margin-top:2px; }
.feature-col { position:sticky; left:0; z-index:4; background:var(--panel);
  min-width:205px; max-width:205px; width:205px; font-weight:600; font-size:12px; }
thead .feature-col { z-index:6; background:var(--section); }
tbody td { min-width:215px; max-width:310px; line-height:1.55; }
.data-row:hover td, .data-row:hover th { background:var(--hover); }
td.col-hl { background:var(--hover); }
code { font-family:var(--mono); font-size:11.5px; background:var(--code-bg);
  color:var(--code-fg); padding:1px 4px; border-radius:4px;
  white-space:pre-wrap; word-break:break-word; }
.na { color:var(--muted); }
.section-row td { background:var(--section); font-weight:600; font-size:12px;
  padding:8px 11px; cursor:pointer; letter-spacing:.02em; }
.section-row:hover td { color:var(--accent); }
.caret { color:var(--muted); margin-right:5px; }
.sec-count { float:right; font-weight:400; color:var(--muted); font-size:11px; }
.empty { padding:34px; text-align:center; color:var(--muted); }
footer { margin-top:13px; font-size:11px; color:var(--muted); line-height:1.7; }
footer code { font-size:11px; }
@media (max-width:640px) {
  .app { padding:14px; } .stat { margin-left:0; } .table-wrap { max-height:65vh; }
}
</style>
</head>
<body>
<div class="app">
  <header class="top">
    <div>
      <h1>Language Cheatsheet</h1>
      <p class="sub">One row = one syntax feature, one column = one programming language.</p>
    </div>
    <div class="stat"><span id="langCount"></span> languages &middot; <span id="featCount"></span> features</div>
    <button id="themeBtn" class="ghost" type="button">Dark</button>
  </header>

  <section class="controls">
    <div class="search-row">
      <input id="search" type="search" placeholder="Search features or code, e.g. lambda / async / print" autocomplete="off">
      <span id="matchInfo" class="hint"></span>
    </div>
    <div class="chips" id="chips"></div>
    <div class="presets">
      <span class="label">Presets:</span>
      <button type="button" data-preset="all">All</button>
      <button type="button" data-preset="none">Clear</button>
      <button type="button" data-preset="web">Web</button>
      <button type="button" data-preset="systems">Systems</button>
      <button type="button" data-preset="mobile">Mobile</button>
      <button type="button" data-preset="scripting">Scripting</button>
      <button type="button" data-preset="jvm">JVM / .NET</button>
      <button type="button" data-preset="apple">Apple</button>
    </div>
  </section>

  <main class="table-wrap">
    <table id="grid">
      <thead id="thead"></thead>
      <tbody id="tbody"></tbody>
    </table>
  </main>

  <footer>
    Generated from <code>README.md</code> by <code>python3 build.py</code> &mdash; edit the table, re-run, done.
    Toggle languages above, click a column header to focus one language, click a section title to fold it.
    Press <code>/</code> to search, <code>Esc</code> to clear.
  </footer>
</div>

<script id="sheet-data" type="application/json">__DATA__</script>
<script>
(function () {
  'use strict';
  var DATA = JSON.parse(document.getElementById('sheet-data').textContent);
  var LANGS = DATA.languages;
  var SECTIONS = DATA.sections;
  var TOTAL = SECTIONS.reduce(function (n, s) { return n + s.rows.length; }, 0);
  var $ = function (id) { return document.getElementById(id); };

  var PRESETS = {
    all: LANGS.slice(),
    none: [],
    web: ['JavaScript', 'TypeScript', 'ArkTS', 'PHP', 'Ruby'],
    systems: ['Go', 'Rust', 'C++', 'Objective-C'],
    mobile: ['Swift', 'Kotlin', 'Dart', 'ArkTS', 'Objective-C'],
    scripting: ['Python', 'Ruby', 'Lua', 'PHP', 'JavaScript'],
    jvm: ['Java', 'Kotlin', 'C#'],
    apple: ['Swift', 'Objective-C', 'C++']
  };
  Object.keys(PRESETS).forEach(function (k) {
    PRESETS[k] = PRESETS[k].filter(function (l) { return LANGS.indexOf(l) >= 0; });
  });

  var state = {
    selected: new Set(LANGS),
    query: '',
    collapsed: new Set(),
    dark: false
  };

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function renderText(t) {
    return esc(t).replace(/\n/g, '<br>').replace(/—/g, '<span class="na">—</span>');
  }
  function renderCell(raw) {
    if (!raw) { return ''; }
    var re = /``\s*([\s\S]*?)\s*``|`([^`\n]*?)`/g;
    var out = '', last = 0, m;
    while ((m = re.exec(raw)) !== null) {
      out += renderText(raw.slice(last, m.index));
      out += '<code>' + esc(m[1] !== undefined ? m[1] : m[2]) + '</code>';
      last = re.lastIndex;
    }
    return out + renderText(raw.slice(last));
  }
  function plain(raw) {
    return raw.replace(/`+/g, '').replace(/\n/g, ' ');
  }
  function visibleRows(sec) {
    var q = state.query.trim().toLowerCase();
    if (!q) { return sec.rows; }
    return sec.rows.filter(function (r) {
      return r.feature.toLowerCase().indexOf(q) >= 0 ||
        r.cells.some(function (c) { return plain(c).toLowerCase().indexOf(q) >= 0; });
    });
  }

  function renderChips() {
    $('chips').innerHTML = LANGS.map(function (l) {
      return '<button type="button" class="chip' + (state.selected.has(l) ? ' on' : '') +
        '" data-lang="' + esc(l) + '">' + esc(l) + '</button>';
    }).join('');
  }
  function renderHead(langs) {
    $('thead').innerHTML = '<tr><th class="feature-col">Feature' +
      '<span class="th-hint">click a language to focus it</span></th>' +
      langs.map(function (l) {
        return '<th class="lang-col" data-lang="' + esc(l) + '" title="Show only ' + esc(l) +
          '">' + esc(l) + '</th>';
      }).join('') + '</tr>';
  }
  function renderBody() {
    var langs = LANGS.filter(function (l) { return state.selected.has(l); });
    var indices = [];
    LANGS.forEach(function (l, i) { if (state.selected.has(l)) { indices.push(i); } });
    if (!langs.length) {
      $('tbody').innerHTML = '<tr><td class="empty">No language selected. Pick one above or press "All".</td></tr>';
      return { langs: langs, shown: 0, matched: 0 };
    }
    var html = '', shown = 0, matched = 0;
    SECTIONS.forEach(function (sec, si) {
      var rows = visibleRows(sec);
      if (!rows.length) { return; }
      matched += rows.length;
      var open = !state.collapsed.has(si);
      html += '<tr class="section-row" data-sec="' + si + '"><td colspan="' + (langs.length + 1) +
        '"><span class="caret">' + (open ? '&#9662;' : '&#9656;') + '</span>' + esc(sec.name) +
        '<span class="sec-count">' + rows.length + ' / ' + sec.rows.length + '</span></td></tr>';
      if (!open) { return; }
      rows.forEach(function (r) {
        shown++;
        html += '<tr class="data-row"><th class="feature-col">' + esc(r.feature) + '</th>' +
          indices.map(function (i) {
            return '<td data-col="' + i + '">' + renderCell(r.cells[i]) + '</td>';
          }).join('') + '</tr>';
      });
    });
    if (!shown) {
      var msg = matched === 0
        ? 'No feature matches "' + esc(state.query) + '".'
        : 'All matching sections are folded. Click a section title to expand.';
      html = '<tr><td class="empty" colspan="' + (langs.length + 1) + '">' + msg +
        '</td></tr>';
    }
    $('tbody').innerHTML = html;
    return { langs: langs, shown: shown, matched: matched };
  }
  function updateInfo(res) {
    $('langCount').textContent = res.langs.length + ' / ' + LANGS.length;
    $('featCount').textContent = TOTAL;
    $('matchInfo').textContent = state.query
      ? res.matched + ' of ' + TOTAL + ' features match'
      : res.shown + ' features shown';
  }
  function render() {
    renderChips();
    renderHead(LANGS.filter(function (l) { return state.selected.has(l); }));
    updateInfo(renderBody());
  }

  $('chips').addEventListener('click', function (e) {
    var b = e.target.closest('.chip');
    if (!b) { return; }
    var l = b.getAttribute('data-lang');
    if (state.selected.has(l)) { state.selected.delete(l); } else { state.selected.add(l); }
    render();
  });
  document.querySelector('.presets').addEventListener('click', function (e) {
    var b = e.target.closest('[data-preset]');
    if (!b) { return; }
    state.selected = new Set(PRESETS[b.getAttribute('data-preset')] || []);
    render();
  });
  $('thead').addEventListener('click', function (e) {
    var th = e.target.closest('[data-lang]');
    if (!th) { return; }
    state.selected = new Set([th.getAttribute('data-lang')]);
    render();
  });
  $('tbody').addEventListener('click', function (e) {
    var tr = e.target.closest('.section-row');
    if (!tr) { return; }
    var si = Number(tr.getAttribute('data-sec'));
    if (state.collapsed.has(si)) { state.collapsed.delete(si); } else { state.collapsed.add(si); }
    updateInfo(renderBody());
  });

  var highlighted = null;
  function clearHighlight() {
    if (highlighted === null) { return; }
    document.querySelectorAll('td.col-hl').forEach(function (el) { el.classList.remove('col-hl'); });
    highlighted = null;
  }
  $('tbody').addEventListener('mouseover', function (e) {
    var cell = e.target.closest('td[data-col]');
    if (!cell) { return; }
    var c = cell.getAttribute('data-col');
    if (highlighted === c) { return; }
    clearHighlight();
    highlighted = c;
    document.querySelectorAll('td[data-col="' + c + '"]').forEach(function (el) {
      el.classList.add('col-hl');
    });
  });
  $('tbody').addEventListener('mouseleave', clearHighlight);

  var timer;
  $('search').addEventListener('input', function (e) {
    var v = e.target.value;
    clearTimeout(timer);
    timer = setTimeout(function () { state.query = v; updateInfo(renderBody()); }, 110);
  });
  $('themeBtn').addEventListener('click', function () {
    state.dark = !state.dark;
    document.documentElement.setAttribute('data-theme', state.dark ? 'dark' : 'light');
    $('themeBtn').textContent = state.dark ? 'Light' : 'Dark';
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== $('search')) {
      e.preventDefault(); $('search').focus();
    }
    if (e.key === 'Escape' && document.activeElement === $('search')) {
      $('search').value = ''; state.query = ''; updateInfo(renderBody());
    }
  });

  render();
})();
</script>
</body>
</html>
"""


def main() -> None:
    data = parse()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # Keep the JSON safe inside a <script> block without changing parsed values.
    payload = (
        payload.replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    OUTPUT.write_text(TEMPLATE.replace("__DATA__", payload), encoding="utf-8")
    n = sum(len(s["rows"]) for s in data["sections"])
    print(
        f"generated {OUTPUT.name}: {len(data['languages'])} languages x {n} features, "
        f"{len(data['sections'])} sections"
    )


if __name__ == "__main__":
    main()
