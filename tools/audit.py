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
  2. Contract load -- every skill loads its slice ${CLAUDE_PLUGIN_ROOT}/terms/<skill>.md.
  3. Resolvable    -- every ${CLAUDE_PLUGIN_ROOT}/<path> reference points at a
                     file that actually exists in the repo.
  4. Skill names   -- every `run/spawn/call **name**` invocation names a real skill.
  5. Terms slices  -- every terms/<skill>.md matches what TERMS.md's audience
                     lines generate (stale/missing/orphaned slices are findings).

`python tools/audit.py --write-terms` regenerates the terms/ slices from
TERMS.md, then runs the full audit. Run it after any TERMS.md edit and commit
the slices; plain `audit.py` (as in CI) only verifies, never writes.

Exit code 0 = clean, 1 = findings (CI-friendly). Stdlib only.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # tools/ -> repo root
TERMS_MD = ROOT / "TERMS.md"
TERMS_DIR = ROOT / "terms"

PLUGIN_ROOT_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`)\"'\]]+)")
SECTION_HEAD = re.compile(r"^## §(\d+)[^\n]*$", re.MULTILINE)
AUDIENCE = re.compile(r"<!--\s*audience:\s*([a-z, -]+?)\s*-->")
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
    slice_ref = f"${{CLAUDE_PLUGIN_ROOT}}/terms/{path.parent.name}.md"
    if slice_ref not in text:
        add("contract-load", path, 1,
            f"skill never loads {slice_ref} -- runs blind to its contract slice")


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


GENERATED_HEADER = (
    "<!-- GENERATED from TERMS.md by `python tools/audit.py --write-terms` -- do not edit.\n"
    "     This is {skill}'s slice of the Plumbline contract: the preamble plus every\n"
    "     section whose audience line names it. TERMS.md is the source of truth. -->\n\n"
)


def parse_terms(skill_names):
    """Split TERMS.md into (preamble, [(section_no, audience, body)]).

    Every `## §N` section must carry an `<!-- audience: skill, skill -->` line
    in its first three lines, naming only real skills. Violations are findings;
    a section without a valid audience is skipped (so the staleness check will
    also flag every slice until the audience line is fixed).
    """
    if not TERMS_MD.exists():
        add("terms-gen", TERMS_MD, 1, "TERMS.md not found -- nothing to generate slices from")
        return None, []
    text = TERMS_MD.read_text(encoding="utf-8")
    heads = list(SECTION_HEAD.finditer(text))
    if not heads:
        add("terms-gen", TERMS_MD, 1, "no `## §N` sections found -- cannot generate slices")
        return None, []

    def strip_separator(chunk):
        return re.sub(r"\n-{3,}\s*$", "", chunk.rstrip()).rstrip()

    preamble = strip_separator(text[: heads[0].start()])
    sections = []
    for i, head in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = strip_separator(text[head.start():end])
        first_lines = "\n".join(body.splitlines()[:3])
        m = AUDIENCE.search(first_lines)
        if not m:
            add("terms-gen", TERMS_MD, line_of(text, head.start()),
                f"section §{head.group(1)} has no `<!-- audience: ... -->` line -- "
                f"the generator cannot route it into any slice")
            continue
        audience = {s.strip() for s in m.group(1).split(",") if s.strip()}
        unknown = sorted(audience - skill_names)
        if unknown:
            add("terms-gen", TERMS_MD, line_of(text, head.start()),
                f"section §{head.group(1)} audience names unknown skill(s): {', '.join(unknown)}")
            audience -= set(unknown)
        sections.append((int(head.group(1)), audience, body))
    return preamble, sections


def render_slice(skill, preamble, sections):
    parts = [GENERATED_HEADER.format(skill=skill) + preamble]
    parts += [body for _no, audience, body in sections if skill in audience]
    return "\n\n---\n\n".join(parts) + "\n"


def check_terms_slices(skill_names, write=False):
    """Generate (--write-terms) or verify the per-skill terms/ slices."""
    preamble, sections = parse_terms(skill_names)
    if preamble is None:
        return
    for skill in sorted(skill_names):
        expected = render_slice(skill, preamble, sections)
        out = TERMS_DIR / f"{skill}.md"
        if write:
            TERMS_DIR.mkdir(exist_ok=True)
            out.write_text(expected, encoding="utf-8", newline="\n")
        elif not out.exists():
            add("terms-stale", out, 1,
                "slice missing -- run `python tools/audit.py --write-terms` and commit")
        elif out.read_text(encoding="utf-8") != expected:
            add("terms-stale", out, 1,
                "slice does not match TERMS.md -- run `python tools/audit.py --write-terms` "
                "and commit (never edit slices by hand)")
    if TERMS_DIR.exists():
        for stray in sorted(TERMS_DIR.glob("*.md")):
            if stray.stem not in skill_names:
                add("terms-stale", stray, 1,
                    "orphaned slice -- no skill with this name; delete it")


def main():
    write_terms = "--write-terms" in sys.argv[1:]
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    agents = sorted((ROOT / "agents").glob("*.md"))
    if not skills:
        print(f"No skills found under {ROOT/'skills'} -- run from the plugin repo.")
        return 2
    skill_names = {p.parent.name for p in skills}

    check_terms_slices(skill_names, write=write_terms)

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
    print(f"Skills: {len(skills)} | Agents: {len(agents)}"
          + (" | terms/ slices regenerated" if write_terms else "") + "\n")

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
