# Plumbline — Directions

How to install and drive Plumbline. For *what it is and why*, see the [README](README.md).

---

## Install

Plumbline is a Claude Code plugin.

```bash
claude plugin marketplace add BytesFromToby/plumbline
claude plugin install plumbline@plumbline
```

Restart Claude Code. The skills (`scaffold`, `adopt`, `architect`, `foreman`, `builder`, `inspector`, `surveyor`, `walkthrough`, `homeowner`) and their worker agents are then available.

---

## Quickstart

Plumbline has two entry points depending on whether the project already exists, then the same forward pipeline.

### New project (greenfield)

```
scaffold ─▶ architect ─▶ foreman ─▶ builder ─▶ inspector
 (once)      (spec)       (blueprint)  (code)     (proof)
```

1. **`scaffold`** — bootstraps the empty project: the folder skeleton, a `CLAUDE.md` contract, and `git init`. Run once.
2. **`architect`** — writes the spec by interviewing you, and fills the contract's Stack/Commands.
3. **`foreman`** — turns the spec into a blueprint (ordered slices, a planned test per criterion).
4. **`builder`** — writes the code and the committed tests, one slice at a time.
5. **`inspector`** — runs the software and proves each `**Done when:**` item; stamps PASS/FAIL.

### Existing project (brownfield)

```
adopt ─▶ architect (adapt) ─▶ foreman ─▶ builder ─▶ inspector
```

1. **`adopt`** — wraps Plumbline around a codebase that already exists: lays the `Planning/` + `Plumbline/` folders non-destructively, **detects and fills** Stack/Commands from the real project, keeps existing git history, and records where the project's spec docs live.
2. **`architect` (adapt mode)** — ingests those existing docs + the code into clean Plumbline specs under `Planning/specs/`, capturing current behavior as tagged `**Done when:**` items (the originals are left untouched as reference).
3. **`foreman` → `builder` → `inspector`** — as above; on an untested codebase, `builder` writes the *characterization tests* that pin existing behavior, retrofitting a test-backed spec onto code that had none.

---

## Running by hand vs. unattended

Every skill runs standalone, and the two **orchestrators** sequence them for you. Nothing is locked to one path.

- **By hand (supervised).** Run the stages yourself, approving between each — `architect` interviews you, you review the spec, then `foreman` → `builder` → `inspector`. You stay the judge at every handoff.
- **`homeowner` (unattended build).** Give it a written brief; it runs the whole build on its own — scaffold, architect, foreman, builder, inspector — halting only at an unresolved Open Question, a stuck builder, or a failed inspection. It stands its own spec self-review in place of the human spec gate, and always runs `inspector` as a separate agent so nothing grades its own work.
- **`walkthrough` (unattended maintain).** Point it at a built project; it runs `surveyor` + `inspector`, applies only Quick-Path-safe fixes in place, and routes everything larger to a dated Recommendations list. Commits nothing.

`surveyor` and `inspector` also run alone — `surveyor` for a drift report before a feature or after a refactor; `inspector` to sign off a single slice.

---

## Inspection levels

A build picks how often the independent `inspector` runs mid-build:

| Level | Stops for inspection… |
|-------|------------------------|
| `full` | after every slice |
| `flagged` (default) | only at `[inspect]`-flagged slices (schema / auth / destructive / cross-module seam), plus the mandated minimum floor |
| `none` | never mid-build — deferred to final sign-off |

Whatever the level, **the final sign-off is always inspected**, and no `[inspect]` slice ever ships uninspected. An unattended `homeowner` run always inspects flagged slices early; a human driving by hand may choose `none` and check at the end.

---

## Folder conventions — where things live

**`Planning/` = human intent (specs + reference) · `Plumbline/` = everything the workflow generates.** Code lives wherever the stack puts it, outside both.

| Path | Holds |
|------|-------|
| `Planning/specs/[feature]_spec.md` | Specs — the source of truth |
| `Planning/reference/` | Shared definitions specs cite (data models, constants) |
| `Plumbline/blueprints/[feature]_BP.md` | Per-feature build plans (split into `_p-1`, `_p-2`, … past 10 slices) |
| `Plumbline/decisions/` | Decision logs (append-only) |
| `Plumbline/architecture.md` | The as-built system map — written once modules need one |
| `Plumbline/inspect/` | Inspector reports + evidence |
| `Plumbline/deviations/` | Builder deviation rollups |
| `Plumbline/surveys/` | Surveyor drift reports |
| `Plumbline/walkthrough/` | Walkthrough logs + recommendations |
| `Plumbline/homeowner/` | Homeowner run logs |

`scaffold` (greenfield) and `adopt` (brownfield) both lay this skeleton up front as guide-rails. In **git** mode (the default) the git log is the history from day one; in **`none`** mode the dated artifacts under `Plumbline/` are the history.

---

## The CLAUDE.md contract

`scaffold`/`adopt` write a single `CLAUDE.md` into each project — the per-project contract every skill reads. It carries:

- **Identity** — one line on what the project is.
- **Stack + Commands** — the test command and run/demo command (must be *real* — `inspector` depends on it), plus a `UI evidence tool` line for web stacks. On a fresh `scaffold` these are `[pending — architect]` until `architect` fills them with the first spec; `adopt` fills them from the existing project up front.
- **History** — `git` (default) or `none`.
- **Where things live** — the folder map.
- **Change rules** — the Quick Path / Full Path (below).
- **Version stamp** — the Plumbline version the project was born under, so skill drift is detectable later.

The spec *format* isn't copied into the contract — it's authoritative in `architect`, so there's no separate template to drift.

---

## Change rules — the order of operations

The sequence for any *single* change isn't a skill you invoke; it lives as the **Change rules** in each project's `CLAUDE.md`, and every skill reads the same doctrine:

- **Quick Path** — no files added/removed/renamed (new *test* files excepted), no schema/core-logic change: edit → run tests → commit.
- **Full Path** — everything else: update the spec → edit code → run tests → run `inspector` if tracked by a blueprint → update the folder map if files moved → write a decision doc if the choice was non-obvious → commit.

---

## Verifying the framework itself — the audit

Plumbline audits its own contract. From the plugin repo:

```bash
python tools/audit.py                # verify skills/agents conform to TERMS.md (CI-friendly; exit 1 on findings)
python tools/audit.py --write-terms  # regenerate the terms/ slices from TERMS.md, then verify
```

Run `--write-terms` after any edit to `TERMS.md` and commit the regenerated slices. Plain `audit.py` (as CI runs it) only verifies, never writes. `tools/auditor.md` is the semantic-pass runbook for the producer/consumer agreements a script can't judge.

---

## Repository layout

```
plumbline/
├── .claude-plugin/plugin.json   # plugin manifest
├── skills/        # the 9 skills (scaffold · adopt · architect · foreman · builder ·
│                  #   inspector · surveyor · walkthrough · homeowner)
├── agents/        # thin worker subagents that delegate to the skills
├── TERMS.md       # the cross-skill contract — source of truth, audience-tagged per section
├── terms/         # generated per-skill slices of TERMS.md — what each skill reads at runtime
├── tools/
│   ├── audit.py   # deterministic contract audit + terms/ slice generator (run in CI)
│   ├── auditor.md # the semantic-pass runbook
│   └── README.md  # how the audit system works (portable to other projects)
├── .github/workflows/audit.yml   # runs the audit on every push
├── README.md · DIRECTIONS.md · LICENSE
```
