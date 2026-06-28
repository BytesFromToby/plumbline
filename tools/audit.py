#!/usr/bin/env python3
"""Plumbline contract audit (deterministic pass).

Checks the framework's own skills and agents against the conventions TERMS.md
encodes -- the mechanical half of the hybrid auditor. It never judges semantics
(that is the optional LLM pass); it only checks things that have a single right
answer, so it can run in CI and cannot itself hallucinate.

Checks:
  1. Frontmatter  -- every SKILL.md / agent .md has parseable frontmatter with
                     `name` + `description`, and no unquoted colon-space in a
                     value (the YAML break that silently drops all frontmatter).
  2. Contract load -- every skill loads ${CLAUDE_PLUGIN_ROOT}/TERMS.md.
  3. Resolvable    -- every ${CLAUDE_PLUGIN_ROOT}/<path> reference points at a
                     file that actually exists in the repo.
  4. Skill names   -- every `run/spawn/call **name**` invocation names a real skill.

Exit code 0 = clean, 1 = findings (CI-friendly). Stdlib only.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # tools/ -> repo root

PLUGIN_ROOT_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`)\"'\]]+)")
INVOCATION = re.compile(r"(?:run|spawn|invoke|calls?)\s+\*\*([a-z][a-z-]+)\*\*", re.IGNORECASE)
FM_LINE = re.compile(r"^([A-Za-z_][\w-]*):\s+(.*)$")

findings = []  # (check, path, line, message)


def add(check, path, line, message):
    findings.append((check, path.relative_to(ROOT).as_posix(), line, message))


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def frontmatter_block(text):
    """Return (lines, start_line) for the YAML frontmatter, or (None, 0)."""
    if not text.startswith("---"):
        return None, 0
    end = text.find("\n---", 3)
    if end == -1:
        return None, 0
    block = text[text.index("\n") + 1 : end]
    return block.splitlines(), 2


def check_frontmatter(path, text):
    lines, start = frontmatter_block(text)
    if lines is None:
        add("frontmatter", path, 1, "no parseable YAML frontmatter block")
        return
    keys = set()
    for i, raw in enumerate(lines):
        m = FM_LINE.match(raw)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        keys.add(key)
        quoted = len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]
        if not quoted and re.search(r":\s", value):
            add(
                "frontmatter",
                path,
                start + i,
                f"`{key}:` value has an unquoted colon-space -- YAML drops all "
                f"frontmatter at runtime (quote it or use an em-dash)",
            )
    for required in ("name", "description"):
        if required not in keys:
            add("frontmatter", path, start, f"frontmatter missing `{required}`")


def check_load_line(path, text):
    if "${CLAUDE_PLUGIN_ROOT}/TERMS.md" not in text:
        add("contract-load", path, 1,
            "skill never loads ${CLAUDE_PLUGIN_ROOT}/TERMS.md -- runs blind to the contract")


def check_resolvable(path, text):
    for m in PLUGIN_ROOT_REF.finditer(text):
        rel = m.group(1).rstrip(".,;:)`*")
        if not (ROOT / rel).exists():
            add("resolvable", path, line_of(text, m.start()),
                f"reference ${{CLAUDE_PLUGIN_ROOT}}/{rel} does not resolve to a file")


def check_invocations(path, text, skill_names):
    for m in INVOCATION.finditer(text):
        name = m.group(1).lower()
        if name not in skill_names:
            add("skill-name", path, line_of(text, m.start()),
                f"invokes **{name}**, which is not a known skill")


def main():
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    agents = sorted((ROOT / "agents").glob("*.md"))
    if not skills:
        print(f"No skills found under {ROOT/'skills'} -- run from the plugin repo.")
        return 2
    skill_names = {p.parent.name for p in skills}

    for path in skills:
        text = path.read_text(encoding="utf-8")
        check_frontmatter(path, text)
        check_load_line(path, text)
        check_resolvable(path, text)
        check_invocations(path, text, skill_names)

    for path in agents:
        text = path.read_text(encoding="utf-8")
        check_frontmatter(path, text)
        check_resolvable(path, text)
        check_invocations(path, text, skill_names)

    print(f"Plumbline contract audit -- {ROOT}")
    print(f"Skills: {len(skills)} | Agents: {len(agents)}\n")

    if not findings:
        print("OK - clean: skills and agents conform to the contract.")
        return 0

    by_check = {}
    for check, path, line, msg in findings:
        by_check.setdefault(check, []).append((path, line, msg))
    for check in sorted(by_check):
        print(f"[{check}]")
        for path, line, msg in by_check[check]:
            print(f"  x {path}:{line} -- {msg}")
        print()
    print(f"{len(findings)} finding(s) across {len(by_check)} check(s).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
