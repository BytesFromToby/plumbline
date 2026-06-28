<!-- The CLAUDE.md contract scaffold emits (R4 — 2026-06-10: git from birth, version stamp;
     supersedes R3 2026-05-25). Fill the [bracketed] bits. -->

# [Project Name]

One line: *what this is and why it exists.* ← from the brief / project name; `architect` refines it if thin.

Plumbline: v1.0

## Stack
[pending — `architect` fills this when it writes the first spec; the stack is a consequence of *what* gets built]

## Commands
- Test: `[pending — architect]`
- Run/demo: `[pending — architect; must be real, inspector depends on it]`
- Shell/OS: `[scaffold fills — e.g. PowerShell on Windows]` — write all Test and Run commands in this dialect
<!-- UI-evidence tool: `architect` adds `playwright (python)` here only if the spec calls for a browser frontend. -->

## History: git
History is the git log — scaffold ran `git init` at birth. Commit each change with a clear
message; there is no separate changelog. *Why* a non-obvious choice was made goes to
`docs/decisions/`; *what changed when* is the log's job.

## Where things live
| Path | Holds |
|------|-------|
| `Planning/specs/` | **Source of truth for behavior** — one `[feature]_spec.md` per feature, inline **Done when:** |
| `Planning/reference/` | Shared definitions specs cite (data models, constants) — fills as specs need it |
| `Planning/blueprints/` | `foreman`'s per-feature build plans |
| `docs/decisions/` | Why a non-obvious choice was made (`[feature]_YYYY-MM-DD.md`, append-only) |
| `output/` | Skill output — `inspector` evidence, etc. |
| `docs/architecture.md` | The as-built system map — written once modules need one |

(Folders are scaffolded empty up front as guide-rails; `docs/architecture.md` is written when modules need a map.)

## Specs
`architect` writes them. The `**Done when:**` format (tagged `[automated]` / `[human-required]`)
is authoritative in the `architect` skill.

## Change rules
Every code/data/structure change picks a path. History lives in **git** — each path ends in a commit.

**Quick Path** — no files added/removed/renamed (new *test* files excepted — those are
Quick Path), no schema/core-logic change, nothing a future reader needs explained:
1. Write/edit the code  2. Run the test command  3. Commit

**Full Path** — everything else:
1. Update the spec (if the change reshapes it, run `architect`)  2. Write/edit the code
3. Run the test command  4. Run `inspector` if tracked by a blueprint
5. Update this file's "Where things live" if files moved
6. Write a decision doc to `docs/decisions/` if a non-obvious choice was made
7. Commit

## How to work here
- Write in plain, clear language.
- Ask clarifying questions before assuming; when unsure, say so.
- The spec is truth — where code and spec disagree, fix one deliberately.

## Skills
`scaffold` (done) → `architect` (spec) → `foreman` → `builder` (code) → `inspector`.
- **blueprint** (`foreman`) — an ordered build plan built for the AI builder: slices of steps,
  one concern each; risky slices flagged `[inspect]` for a mid-slice inspector stop.
- **proof** (`inspector`) — runs the software and captures evidence that each **Done when:**
  item actually holds; judges whether each committed test could actually fail; stamps PASS/FAIL.
  "Done" means *shown* to work, not asserted.

When the project grows, graduating it (split specs into per-feature files, extract a reference
tier, add `docs/architecture.md`) is a manual step for now.
