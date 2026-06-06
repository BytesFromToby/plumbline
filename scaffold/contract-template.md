<!-- The CLAUDE.md contract scaffold emits (R3 — agreed 2026-05-25, refined live on a test project).
     Fill the [bracketed] bits. This is the "rich" replacement for the old light template. -->

# [Project Name]

One line: *what this is and why it exists.* ← scaffold should prompt for this.

## Stack
[language / framework]

## Commands
- Test: `[test command]`
- Run/demo: `[how to launch it so behaviour is visible]`
- Shell/OS: `[e.g. PowerShell on Windows]` — write all Test and Run commands in this dialect
<!-- UI-evidence tool: `playwright (python)` — add only if there's a browser frontend. -->

## History: local
No git yet (experimental/small). History lives in `docs/changelog/` + `docs/decisions/`.
**When this project proves useful, graduate it to `git` by hand** — init the repo and shed the
manual changelog (git becomes the history).

## Where things live
| Path | Holds |
|------|-------|
| `Planning/specs/` | **Source of truth for behavior** — one `[feature]_spec.md` per feature, inline **Done when:** |
| `Planning/reference/` | Shared definitions specs cite (data models, constants) — fills as specs need it |
| `Planning/blueprints/` | `foreman`'s per-feature build plans |
| `docs/decisions/` | Why a non-obvious choice was made (`YYYY-MM-DD-title.md`, append-only) |
| `docs/changelog/` | What changed, by date (local mode only) |
| `output/` | Skill output — `inspector` evidence, etc. |
| `docs/architecture.md` | The as-built system map — written once modules need one |

(Folders are scaffolded empty up front as guide-rails; `docs/architecture.md` is written when modules need a map.)

## Specs
`architect` writes them. The `**Done when:**` format (tagged `[automated]` / `[human-required]`)
is authoritative in `architect/SKILL.md`.

## Change rules
Every code/data/structure change picks a path. History mode is **local** (see above).

**Quick Path** — no files added/removed/renamed, no schema/core-logic change, nothing a
future reader needs explained:
1. Write/edit the code  2. Run the test command  3. Add a `docs/changelog/changelog.md` entry under today's date

**Full Path** — everything else:
1. Update the spec (if the change reshapes it, run `architect`)  2. Write/edit the code
3. Run the test command  4. Run `inspector` if tracked by a blueprint
5. Update this file's "Where things live" if files moved
6. Write a decision doc to `docs/decisions/` if a non-obvious choice was made
7. Add a `docs/changelog/changelog.md` entry

## How to work here
- Write in plain, clear language.
- Ask clarifying questions before assuming; when unsure, say so.
- The spec is truth — where code and spec disagree, fix one deliberately.

## Skills
`scaffold` (done) → `architect` (spec) → `foreman` → `builder` (code) → `inspector`.
- **blueprint** (`foreman`) — an ordered build plan built for the AI builder: slices of steps, one concern each.
- **proof** (`inspector`) — runs the software and captures evidence that each **Done when:**
  item actually holds; stamps PASS/FAIL. "Done" means *shown* to work, not asserted.

When the project grows, graduating it (init git, split specs into per-feature files, extract a reference tier) is a manual step for now.
