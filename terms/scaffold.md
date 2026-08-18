<!-- GENERATED from TERMS.md by `python tools/audit.py --write-terms` -- do not edit.
     This is scaffold's slice of the Plumbline contract: the preamble plus every
     section whose audience line names it. TERMS.md is the source of truth. -->

# Plumbline TERMS — the cross-skill contract

**Version:** v1.0 (tracks the skill suite version)

Single source of truth for every term, token, and status string shared by more than one
Plumbline skill. One skill **produces** a token; one or more others **consume** it. When
producer and consumer disagree on the exact string, the chain breaks silently — this file
keeps them identical.

**Rules of use**
- **Tokens are literal.** Reproduce them verbatim — exact case, punctuation, spacing.
  `**Done when:**` (spec) and `**Done When:**` (blueprint step) are *different* tokens.
- **This file wins.** Where a skill's prose describes a token differently than defined here,
  this file is canonical and the skill is the thing to fix.
- **Cross-skill only.** A term used inside one skill stays in that skill. This is a registry to
  match against, not a narrative — see the README for what each skill *does*.
- **Referencing.** At runtime each skill reads its **generated slice** of this contract —
  `terms/<skill>.md` under the plugin root, holding only the sections whose
  `<!-- audience: ... -->` line names that skill. Regenerate the slices with
  `python tools/audit.py --write-terms`; the audit fails while they are stale, so a slice
  can never silently drift from this file. A skill that cannot load its slice must stop
  and report, never guess the contract.

---

## §8 — Paths & naming
<!-- audience: scaffold, adopt, architect, foreman, builder, inspector, surveyor, homeowner, walkthrough -->

Every skill must agree byte-for-byte. `[feature]` is the feature's lowercase slug, identical across its spec, blueprint, and output files. Dates are `YYYY-MM-DD`.

**The tree splits in two.** `Planning/` holds **human intent** — the specs and reference the build is judged against. `Plumbline/` holds **everything the workflow generates** — blueprints, decision logs, and every skill's reports. Code lives wherever the stack puts it, outside both.

| Path / pattern | Owner | Notes |
|---|---|---|
| `Planning/specs/[feature]_spec.md` | architect | source of truth |
| `Planning/reference/` | architect | shared definitions specs cite (data models, constants) |
| `Plumbline/blueprints/[feature]_BP.md` | foreman | single-file blueprint |
| `Plumbline/blueprints/[feature]_BP_p-1.md`, `_p-2.md`, … | foreman | part files past 10 slices; **slice numbering is continuous across parts** (p-2 opens at Slice 11) |
| `Plumbline/decisions/[feature]_YYYY-MM-DD.md` | architect | decision log (append-only) |
| `Plumbline/architecture.md` | manual | as-built map; written only once modules need one |
| `Plumbline/inspect/Inspect_[feature]_Final_[YYYY-MM-DD]_[HH-MM].md` | inspector | final report; **`HH-MM` uses a hyphen** (filenames forbid `:`); the time suffix stops a re-inspection overwriting the failed one |
| `Plumbline/deviations/Deviations_[feature]_[YYYY-MM-DD]_[HH-MM].md` | builder | deviation rollup; written even when none ("None.") |
| `Plumbline/surveys/Survey_[YYYY-MM-DD]_[HH-MM].md` (or `Survey_[feature]_[YYYY-MM-DD]_[HH-MM].md`) | surveyor | dated drift report |
| `Plumbline/walkthrough/WalkthroughLog_[YYYY-MM-DD]_[HH-MM].md`, `Recommendations_[YYYY-MM-DD]_[HH-MM].md` | walkthrough | |
| `Plumbline/homeowner/HomeownerLog_[YYYY-MM-DD]_[HH-MM].md` | homeowner | run log |
| `CLAUDE.md` | scaffold / adopt (write) / architect (fills) | the project contract (§9) |

**Every generated report under `Plumbline/` carries `_YYYY-MM-DD_HH-MM`** (hyphens) — so reruns sort by time and never overwrite a prior run. Blueprint **stamps** use `HH:MM` (colon — they are text, not filenames). The append-only decision log stays date-only (`[feature]_YYYY-MM-DD.md`).

---

## §10 — Contract & lifecycle terms
<!-- audience: scaffold, adopt, architect, inspector, homeowner, walkthrough -->

| Term | Definition |
|---|---|
| `CLAUDE.md` | The per-project contract scaffold writes and every skill reads: identity, stack, commands, change rules, folder map, Plumbline version stamp. |
| `[pending — architect]` | Placeholder scaffold leaves in `CLAUDE.md` for **Stack** and **Commands**. **architect** fills them when it writes the first spec — the one time architect writes to the contract. walkthrough must route an unfilled placeholder to Recommendations, **never fill it**. |
| `UI evidence tool` | A `CLAUDE.md` **Commands** line — `- UI evidence tool: <tool>` (e.g. `playwright (python)`) — that **architect** adds when the spec calls for a browser UI and **inspector** reads to choose its capture engine. Match the key exactly: inspector greps the literal `UI evidence tool` (no hyphen). |
| `History` mode | A `CLAUDE.md` field — `git` (**default**) or `none`. `git`: scaffold inits git, every change ends in a commit, history is the git log. `none`: no git; history is the dated artifact trail (`Plumbline/` — decisions, reports, and blueprint stamps) — a full audit trail, no per-file diffs, no manual changelog. scaffold sets it; the Change-rules terminal step and homeowner's closing file-list both branch on it. |
| **Quick Path / Full Path** | The change-rules in `CLAUDE.md`. Quick Path: no files added/removed/renamed (new *test* files excepted), no schema/core-logic change → edit, test, commit. Full Path: everything else → spec, code, test, inspect, decision doc, commit. |
| **Build mode / Maintain mode** | Build = idea → verified code (scaffold → architect → foreman → builder → inspector). Maintain = keep built code honest (surveyor, inspector, walkthrough). |
| **adopt (brownfield bootstrap)** | The existing-project counterpart to **scaffold**. Lays the single `Plumbline/` machinery folder + `Planning/` skeleton into a repo that already has code (non-destructively), **detects and fills** Stack/Commands from the real project rather than leaving `[pending]`, sets History from the repo (`git` if already a git repo), and asks where the project's existing spec docs live. It does not write specs itself: it records that source location and hands to **architect** in *adapt mode*, which ingests those docs + the code into Plumbline specs under `Planning/specs/` (the originals are left untouched as reference). Runs once, at first onboarding. |
| **Orchestrator** | A skill that sequences others without reimplementing them: **homeowner** (build), **walkthrough** (maintain). |
