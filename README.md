# Plumbline — a spec-driven workflow of AI-agent skills

*To build a house well you follow the plans, double-check the work, and keep everything plumb. The plumb line is the builder's reference of truth — here, your spec is that line.*

## Description

A "trust, but verify" set of agent skills that build code in a trackable way — even reporting their own deviations as they go — for better, more accountable coding.

- **Agents build, you approve.** Run by hand, the work moves across five single-responsibility stages — from spec to signed-off code — stopping for your sign-off at each handoff.
- **No stage does the next one's job.** `inspector` can't edit the spec to pass a test; `builder` can't invent requirements. Those boundaries are what keep it honest.
- **Coordinated by files, not calls.** Stages never call each other, so any one runs on its own — and the spec stays the single source of truth end to end.
- **Inspectable, not trusted.** A deviation log records where the build left the plan; test evidence backs every "done."
- **Two unattended orchestrators.** `homeowner` takes a written brief to verified code on its own, halting only when it hits a gap it can't safely cross; `walkthrough` keeps a built project aligned to its spec. Both drive the same single-responsibility skills rather than reimplementing them — and those skills also run by hand, where you approve each handoff.

*Built for a solo developer's real projects — and run end-to-end on real features, spec through signed-off code, not just designed on paper. [Polis](https://github.com/BytesFromToby/Polis), a political-simulation game with a live-LLM negotiation layer, was specced, built, and signed off under it.*

---

## Two modes: build, then maintain

Plumbline runs in two directions. **Build** takes an idea to verified code through five forward stages. **Maintain** keeps an already-built project honest over time, on its own. The two share the same spec, the same file conventions, and one skill — `inspector` — that does duty in both.

### Build — idea to verified code

```
scaffold ──▶ architect ──▶ foreman ──▶ builder ──▶ inspector
 (once)       (spec)       (blueprint)   (code)      (proof)
                                          ▲             │
                                          └──── fix ◀───┘
```

| Stage | Owns | Produces |
|-------|------|----------|
| **scaffold** | Bootstrapping a greenfield project (run once) | The folder skeleton + a `CLAUDE.md` contract (+ `git init` in git mode) |
| **architect** | Defining *what* to build | `Planning/specs/[feature]_spec.md` with inline acceptance criteria, a decision log |
| **foreman** | Planning *how* to build it | `Planning/blueprints/[feature]_BP.md` — slices of ordered steps |
| **builder** | Writing the code | Code + tests, executed one slice at a time, with a deviation log |
| **inspector** | Proving it works | An evidence report; a dated PASS/FAIL stamp on the blueprint |

Each stage hands off through the filesystem. The user approves between stages — the agent does the work, the human stays the judge.

By default every project starts in **git** — `scaffold` runs `git init` with the skeleton, and the log is the history from day one (decision docs carry the *why*; no manual changelog to silently fall behind). A **`none`** history mode is available for non-git workflows: scaffold skips git, and the dated artifact trail (`docs/decisions/` + `output/`) is the history — a full audit record, minus per-file diffs. A project still grows through stages — **small** (one spec, flat structure) → **big** (split specs, reference tier, architecture doc); graduating across that boundary — splitting a monolith spec, extracting the reference tier — is currently a **manual** step. (Automating it in a dedicated skill is a planned addition, not part of this version.)

**Or hand the whole job to `homeowner`.** `homeowner` is the build-mode orchestrator — the counterpart to `walkthrough`. Give it a written brief and it runs the five stages on its own, with no human approval gate, halting only when it hits something it can't safely cross:

```
homeowner  ── one session: a written brief to verified code, unattended ──
   │
   ├─ calls ─▶ scaffold ..... greenfield skeleton + CLAUDE.md (once)
   ├─ calls ─▶ architect .... expands the brief into a spec; gaps → assumptions (proceed) or forks (halt)
   │            └─▶ homeowner reviews that spec against the brief it holds   ◀── its own gate
   ├─ calls ─▶ foreman ...... breaks the spec into a blueprint
   ├─ calls ─▶ builder ...... every slice, building till the tests pass
   └─ calls ─▶ inspector .... fresh-eyes proof, as a separate subagent
```

It removes the human spec gate and stands its own spec self-review in its place — the principal checking the plan against the brief it holds, not a self-graded build. But it never papers over trouble: unresolved Open Questions, a `builder` that gets stuck, or a failed inspection **halt the run and surface it** for a human. And it can't grade its own work — `inspector` always runs as a separate agent, so the proof stays independent. Like `walkthrough`, it reimplements nothing; it only sequences.

For a *supervised* build — a human approving the spec — run the stages by hand instead: `architect` interviews you, you review the spec, then `foreman` → `builder` → `inspector`.

### Maintain — keep a built project honest

Once code exists, `walkthrough` takes over — the maintain-mode orchestrator, what `homeowner` is to building turned toward upkeep: run it and walk away. It works a project end-to-end — baseline, drift, coverage, docs — applying only changes safe enough to make unattended and routing everything else to a list you approve. It doesn't reimplement the checks it needs; it calls the same skills the build mode uses.

```
walkthrough  ── one autonomous session, fenced to safe changes ──
   │
   ├─ calls ─▶ surveyor    static: spec-vs-code drift
   ├─ calls ─▶ inspector   runtime: proof against the Done-when items
   │
   ├─▶ Quick-Path fixes ........ applied in place, tests re-run after each
   └─▶ everything larger ....... a dated, prioritized Recommendations list
```

| Skill | Owns | Produces |
|-------|------|----------|
| **walkthrough** | An autonomous maintenance session (no check-ins, commits nothing) | Quick-Path fixes applied + `output/walkthrough/Recommendations_YYYY-MM-DD_HH-MM.md` |
| **surveyor** | Static spec-vs-code drift — reads and compares, never runs the software | A dated `output/surveys/Survey_YYYY-MM-DD.md` (written even when clean) |
| **inspector** | Runtime proof against the spec — *the same skill the build lifecycle ends on* | An evidence report in `output/inspect/` |

`surveyor` and `inspector` also run standalone — `surveyor` before a feature or after a refactor when you just want a drift report; `inspector` to sign off a single slice. `walkthrough` is the hands-off orchestration of both, fenced by the **Change rules** in `CLAUDE.md`: it applies Quick-Path fixes itself and never authors a decision doc or touches a schema unattended.

---

## Where model strength goes

Plumbline is built so capability is spent where it pays and saved where it doesn't. The strong
models do the thinking at the ends of the pipeline; the rails in the middle are what make an
economy model a dependable builder.

| Stage | Model | Why |
|-------|-------|-----|
| `architect` | strong | elicits the spec — the one artifact everything else hangs on |
| `foreman` | strong | plans the slices, commits a test per criterion, writes the forward constraints a budget builder needs |
| `builder` | **economy** | fine-grained steps with exact names and addresses — the blueprint *is* the hand-holding |
| `inspector` | strong | judges evidence and test fidelity; the last line of defense, never the place to save money |

The blueprint's granularity isn't ceremony — it's the exchange rate. The finer the foreman
plans, the cheaper the builder can be. And because the builder model can differ from run to run
on the same project — it's not a known, stable thing — `foreman` always plans for the weakest
builder that might show up: a strong model following fine steps loses minutes, a weak model
improvising through coarse steps loses the build. `walkthrough` reads the accumulated deviation
logs as plan-quality evidence (trivial-deviation noise → the blueprint pinned tactics that
didn't matter; repeated stucks → it left addresses thin) — the framework improves its plans on
evidence, not anyone's self-assessment.

---

## Principles

- **The spec is the spine.** `architect` writes it, `builder` checks its work against it, `inspector` verifies the running software against it. The blueprint in the middle is a disposable plan; the spec is truth at both ends *and* in the middle.
- **Evidence over assertion.** "Done" means *shown* to work. `inspector` runs the software and captures output — a bare "PASS" is not evidence.
- **Independence is structural, not promised.** `inspector` runs with fresh eyes — ideally as a separate agent that never saw the build — so "no stake in the outcome" is enforced by isolation, not by good intentions.
- **Convention-coupled, not call-coupled.** The single-responsibility skills never call each other — they share documented file contracts (the `CLAUDE.md` declarations + folder layout) and are sequenced by data dependency, not a hard-wired chain. The two orchestrators (`homeowner`, `walkthrough`) *do* invoke them, but only to sequence — they reimplement nothing, so every skill stays independently runnable.
- **Proportional ceremony.** A one-line fix doesn't get a decision doc; a schema change does. `architect` sizes its interview to the work; the **Change rules** in each project's `CLAUDE.md` give trivia a Quick Path and reserve the Full Path for features and schema.
- **Gates must earn their place.** Every stop, check, and document exists to catch a specific failure. The ones that don't get cut — this framework has been pruned as hard as it's been built.

**Design priorities, in order:** *repeatable > reliable > easy > fast.* When they conflict, the higher one wins — a reliability gain is worth a small speed cost, and consistency across runs beats either.

---

## The "Done when" contract

Acceptance criteria live *inline in the spec*, attached to each feature — not in a separate checklist that drifts. Each is observable and tagged:

```
**Done when:**
- `POST /login` with valid creds → 200 + a session cookie; bad creds → 401   `[automated]`
- the dashboard's 4 KPI cards sit above the fold at 1280px                    `[human-required]`
```

- `[automated]` — `foreman` plans a committed test that encodes it; `builder` writes that test; `inspector` runs it. "Automated" means *there is a test*, not "the agent improvised a check."
- `[human-required]` — `inspector` captures evidence (e.g. a screenshot) but never grades it; the human signs it off.

A green test proves a criterion only if the test *encodes* it — so at final sign-off `inspector`
also reads each backing test and asks: *would this fail if the criterion were violated?* A test
that can't fail (vacuous assertion, behavior mocked away) is a finding, not a pass.

---

## How the stages stay honest

- **`builder` reads the spec, not just the blueprint.** If a step contradicts the spec, it stops rather than faithfully building the wrong thing — closing the "telephone game" between plan and intent.
- **`builder` stops cleanly when stuck.** Clear rules: don't improvise a different approach, don't retry forever, never run a destructive action on the blueprint's say-so alone, and leave the codebase in a known state when you stop.
- **Deviations are an audit trail, not a blocker.** When the build diverges from the plan in a behavior-preserving way, it's logged inline and rolled up to `output/deviations/` — visible at the end whether or not inspection runs.
- **`inspector` may stamp a result but never edit criteria.** It can record `✅ Inspector: PASS — YYYY-MM-DD HH:MM` on the blueprint; it cannot touch a step, a Done-when, or the spec to make something pass.
- **Inspection is risk-weighted, not ritual.** `foreman` flags slices that touch schema, auth/security, destructive operations, or cross-module seams `[inspect]`; the rest flow on green tests. A build also picks an **inspection level** — inspect every slice, only the flagged ones (the default), or defer all mid-build checks to the end — so a human driving by hand isn't forced to stop at each flagged slice, while an unattended `homeowner` run always inspects them early. Whatever the level, the final sign-off is always inspected, and no `[inspect]` slice ever ships uninspected.
- **Repairs run on rails too.** A failed inspection routes back to `builder` in **fix mode**: the report's failure items become the step list, the same stuck/deviation rules apply, and the loop always closes with re-inspection — the most fragile moment in the pipeline is governed, not improvised.
- **The blueprint never forgets.** Regenerating after a spec update preserves checkboxes, inspector stamps, and deviation notes on unaffected slices; changed slices are marked stale, not erased. Regeneration can't delete the audit.

---

## Folder conventions

**`Planning/` = the living plan · `docs/` = the record & reference · `output/` = skill output.**

| Path | Holds |
|------|-------|
| `Planning/specs/[feature]_spec.md` | Specs — the source of truth |
| `Planning/reference/` | Shared definitions specs cite (data models, constants) |
| `Planning/blueprints/[feature]_BP.md` | Per-feature build plans (split into `_p-1`, `_p-2`, … past 10 slices) |
| `docs/decisions/` | Decision logs (append-only) |
| `docs/architecture.md` | The as-built system map — written once modules need one |
| `output/inspect/` | Inspector reports + evidence |
| `output/deviations/` | Builder deviation rollups |
| `output/surveys/` | Surveyor drift reports (`Survey_YYYY-MM-DD_HH-MM.md`) |
| `output/walkthrough/` | Walkthrough log + recommendations (`…_YYYY-MM-DD_HH-MM.md`) |
| `output/homeowner/` | Homeowner run logs (`HomeownerLog_YYYY-MM-DD_HH-MM.md`) |

`scaffold` lays the full folder skeleton up front as guide-rails and, in **git** mode (the default),
inits git — the log is the history from day one; `docs/decisions/` carries the why. In **`none`** mode
it skips git and the dated artifacts are the history.

---

## The CLAUDE.md contract

`scaffold` writes a single `CLAUDE.md` contract into each project — the structure plus the parts knowable up front; every skill reads it. It carries:

- **Identity** — one line on what the project is and why.
- **Stack + Commands** — the test command and the run/demo command (must be *real* — `inspector` depends on it), plus a `UI evidence tool` line for web stacks. `scaffold` makes no design decisions, so it leaves these as `[pending — architect]` placeholders; **`architect` fills them when it writes the first spec**, since the stack is a consequence of *what* gets built, not something to settle before any design exists.
- **History** — git by default, from scaffold onward (the log is the history); a `none` mode for non-git projects uses the dated artifact trail instead. `docs/decisions/` carries the rationale either way.
- **Where things live** — the folder map, so a reader or agent orients without spelunking.
- **Change rules** — the Quick Path / Full Path for any change (new *test* files are the one Quick-Path file-creation exception). Doctrine every skill reads, not a skill you invoke.
- **Version stamp** — the Plumbline version the project was scaffolded under, so skill drift is detectable later.
- **How to work here** + the skills flow.

The spec *format* isn't copied into the contract — it's authoritative in `architect` (which writes specs), so there's no separate template to drift.

---

## The shared contract: TERMS.md

`CLAUDE.md` is the per-*project* contract. `TERMS.md` is the per-*framework* one: the single, canonical definition of every token, status line, file path, and invariant the skills share — `**Done when:**`, the `[automated]` / `[human-required]` tags, the routing status lines, the `[inspect]` trigger list, and the rest.

It exists because a skill is read **cold**. A fresh agent — or a different model — loads one skill with none of the context it was written in, so any shared convention that lives only "in the author's head" is a silent failure waiting to happen: a stamp spelled two ways, a status line an orchestrator no longer recognizes. TERMS makes that shared ground explicit.

At runtime, though, no skill reads the whole thing. Each TERMS section carries an `<!-- audience: ... -->` line naming the skills bound by it, and `tools/audit.py --write-terms` generates a per-skill **slice** — `terms/<skill>.md` — holding only those sections. A skill reads its slice first (`${CLAUDE_PLUGIN_ROOT}/terms/<skill>.md`) and stops if it can't load it, rather than guessing. The point: an orchestrator spawns many subagents per run, and every spawn was paying to load contract sections that didn't bind it — the slices keep the runtime drift-guard while cutting that fixed cost roughly in half (`scaffold` loads about a third of the full contract).

And the contract is **verified, not decorative.** `tools/audit.py` checks every skill and agent against it — frontmatter validity, the slice load-line, reference resolvability, skill-name resolution, and that every generated slice still matches `TERMS.md` — deterministically, on every push via CI. A slice can't drift from the contract: it's generated, and the audit fails while it's stale. `tools/auditor.md` is the semantic half: a runbook for the producer/consumer agreement a script can't judge. It's the framework's own "trust, but verify" turned on itself.

---

## Not a skill: the order of operations

The sequence for any *single* change isn't a stage you invoke — it lives as the **Change rules** in each project's `CLAUDE.md` (Quick Path for trivia, Full Path for features and schema). Every skill reads the same doctrine, so the workflow stays consistent without one skill ever having to call another.

---

## Repository layout

Plumbline is packaged as a Claude Code plugin — `.claude-plugin/plugin.json` declares it, and the default scans discover the skills and agents.

```
plumbline/
├── .claude-plugin/plugin.json   # plugin manifest
├── skills/        # the 8 skills (architect · foreman · builder · inspector ·
│                  #   scaffold · surveyor · walkthrough · homeowner)
├── agents/        # thin worker subagents that delegate to the skills
├── TERMS.md       # the cross-skill contract — source of truth, audience-tagged per section
├── terms/         # generated per-skill slices of TERMS.md — what each skill reads at runtime
├── tools/
│   ├── audit.py   # deterministic contract audit + terms/ slice generator (run in CI)
│   ├── auditor.md # the semantic-pass runbook
│   └── README.md  # how the audit system works (portable to other projects)
├── .github/workflows/audit.yml   # runs the audit on every push
└── README.md · LICENSE
```

---

## Version

**v1.0** — each skill carries a `version:` in its frontmatter, and every scaffolded project's
`CLAUDE.md` records the version it was born under, so a project can tell when the skills have
moved on without it.

## License

[MIT](LICENSE) © 2026 BytesFromToby
