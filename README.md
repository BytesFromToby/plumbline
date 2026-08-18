# Plumbline — a spec-driven workflow of AI-agent skills

*To build a house well you follow the plans, double-check the work, and keep everything plumb. The plumb line is the builder's reference of truth — here, your spec is that line.*

A **"trust, but verify"** set of Claude Code agent skills that build code in a trackable way — reporting their own deviations as they go — for more accountable AI development.

- **Agents build, you approve.** Work moves across single-responsibility stages — from spec to signed-off code — each stage stopping for your sign-off at its handoff.
- **No stage does the next one's job.** `inspector` can't edit the spec to pass a test; `builder` can't invent requirements. Those boundaries are what keep it honest.
- **Coordinated by files, not calls.** Stages never call each other, so any one runs on its own — and the spec stays the single source of truth end to end.
- **Inspectable, not trusted.** A deviation log records where the build left the plan; test evidence backs every "done."
- **Greenfield or brownfield.** Start an empty project with `scaffold`, or wrap Plumbline around an existing codebase with `adopt` — retrofitting a test-backed spec onto code that had none.
- **Unattended or supervised.** Two orchestrators (`homeowner`, `walkthrough`) take a job start-to-finish on their own; or run the same skills by hand and approve each handoff.

> **Just want to run it?** → **[DIRECTIONS.md](DIRECTIONS.md)** — install, quickstart, and the operational reference. This page is what it is and why.

*Built for a solo developer's real projects — and run end-to-end on real work, spec through signed-off code, not just designed on paper. [Polis](https://github.com/BytesFromToby/Polis), a political-simulation game with a live-LLM negotiation layer, was specced, built, and signed off under it.*

---

## The pipeline

Plumbline runs in two directions. **Build** takes an idea to verified code through the forward stages. **Maintain** keeps an already-built project honest over time, on its own. The two share the same spec, the same file conventions, and one skill — `inspector` — that does duty in both.

### Build — idea to verified code

```
                    ┌─ scaffold (greenfield) ─┐
                    │                          ▼
                    └─ adopt (brownfield) ─▶ architect ─▶ foreman ─▶ builder ─▶ inspector
                                              (spec)      (blueprint)  (code)     (proof)
                                                                        ▲            │
                                                                        └─── fix ◀───┘
```

| Stage | Owns | Produces |
|-------|------|----------|
| **scaffold** | Bootstrapping a greenfield project (run once) | The folder skeleton + a `CLAUDE.md` contract (+ `git init`) |
| **adopt** | Onboarding an existing project (run once) | The skeleton laid non-destructively; Stack/Commands detected from the real code |
| **architect** | Defining *what* to build | `Planning/specs/[feature]_spec.md` with inline acceptance criteria, a decision log |
| **foreman** | Planning *how* to build it | `Plumbline/blueprints/[feature]_BP.md` — slices of ordered steps |
| **builder** | Writing the code | Code + committed tests, executed one slice at a time, with a deviation log |
| **inspector** | Proving it works | An evidence report; a dated PASS/FAIL stamp on the blueprint |

Each stage hands off through the filesystem — the agent does the work, the human stays the judge. **Or hand the whole job to `homeowner`:** give it a written brief and it runs the build unattended, standing its own spec self-review in place of the human gate and halting only when it hits a gap it can't safely cross (an unresolved Open Question, a stuck builder, a failed inspection). It can't grade its own work — `inspector` always runs as a separate agent.

### Maintain — keep a built project honest

Once code exists, `walkthrough` takes over — what `homeowner` is to building, turned toward upkeep. It works a project end-to-end (drift, coverage, docs), applying only changes safe enough to make unattended and routing everything else to a list you approve.

| Skill | Owns | Produces |
|-------|------|----------|
| **walkthrough** | An autonomous maintenance session (no check-ins, commits nothing) | Quick-Path fixes applied + a dated Recommendations list |
| **surveyor** | Static spec-vs-code drift — reads and compares, never runs the software | A dated drift report (written even when clean) |
| **inspector** | Runtime proof against the spec — *the same skill the build lifecycle ends on* | An evidence report |

Both orchestrators reimplement nothing — they only sequence the same single-responsibility skills, which all still run standalone.

---

## Brownfield adoption

Most spec-driven tooling assumes you start from zero. Plumbline's `adopt` wraps the workflow around a project that **already exists** — and because every artifact it generates lives in one self-contained `Plumbline/` folder, it drops in without colliding with whatever structure the repo already has.

- `adopt` lays the skeleton **non-destructively** and **detects** the real stack and test command from the code — no re-deciding what the project already is.
- `architect` runs in **adapt mode**: it reads the project's existing docs and code as raw material and writes clean Plumbline specs, capturing *current behavior* as observable `**Done when:**` items. The originals are never touched.
- `foreman` → `builder` then plan and write **characterization tests** that pin that behavior — the payoff is a **test-backed spec retrofitted onto code that had none**, verified by an independent `inspector`.

---

## Where model strength goes

Plumbline is built so capability is spent where it pays and saved where it doesn't. Strong models do the thinking at the ends of the pipeline; the rails in the middle are what make an economy model a dependable builder.

| Stage | Model | Why |
|-------|-------|-----|
| `architect` | strong | elicits the spec — the one artifact everything else hangs on |
| `foreman` | strong | plans the slices, commits a test per criterion, writes the forward constraints a budget builder needs |
| `builder` | **economy** | fine-grained steps with exact names and addresses — the blueprint *is* the hand-holding |
| `inspector` | strong | judges evidence and test fidelity; the last line of defense, never the place to save money |

The blueprint's granularity isn't ceremony — it's the exchange rate. The finer the `foreman` plans, the cheaper the `builder` can be. And because the builder model can differ run to run, `foreman` always plans for the *weakest* builder that might show up: a strong model following fine steps loses minutes; a weak model improvising through coarse steps loses the build.

The orchestrators sit outside the table because they mostly sequence — but each holds one judgment seat of its own (`homeowner`'s spec self-review, `walkthrough`'s Quick-Path triage). Run both strong.

---

## Principles

- **The spec is the spine.** `architect` writes it, `builder` checks its work against it, `inspector` verifies the running software against it. The blueprint in the middle is a disposable plan; the spec is truth at both ends *and* in the middle.
- **Evidence over assertion.** "Done" means *shown* to work. `inspector` runs the software and captures output — a bare "PASS" is not evidence.
- **Independence is structural, not promised.** `inspector` runs with fresh eyes — ideally as a separate agent that never saw the build — so "no stake in the outcome" is enforced by isolation, not good intentions.
- **Convention-coupled, not call-coupled.** The single-responsibility skills never call each other — they share documented file contracts and are sequenced by data dependency. The orchestrators invoke them only to sequence; every skill stays independently runnable.
- **Proportional ceremony.** A one-line fix doesn't get a decision doc; a schema change does. Gates are sized to the work.
- **Gates must earn their place.** Every stop, check, and document exists to catch a specific failure. The ones that don't get cut — this framework has been pruned as hard as it's been built.

**Design priorities, in order:** *repeatable > reliable > easy > fast.* When they conflict, the higher one wins.

---

## The "Done when" contract

Acceptance criteria live *inline in the spec*, attached to each feature — not in a separate checklist that drifts. Each is observable and tagged:

```
**Done when:**
- `POST /login` with valid creds → 200 + a session cookie; bad creds → 401   [automated]
- the dashboard's 4 KPI cards sit above the fold at 1280px                    [human-required]
```

- `[automated]` — `foreman` plans a committed test that encodes it; `builder` writes that test; `inspector` runs it. "Automated" means *there is a test*, not "the agent improvised a check."
- `[human-required]` — `inspector` captures evidence (e.g. a screenshot) but never grades it; the human signs it off.

A green test proves a criterion only if the test *encodes* it — so at final sign-off `inspector` also reads each backing test and asks: *would this fail if the criterion were violated?* A test that can't fail is a finding, not a pass.

---

## Verified, not decorative — the contract audits itself

Every token, status line, file path, and invariant the skills share lives in one canonical **`TERMS.md`**. It exists because a skill is read *cold*: a fresh agent — or a different model — loads one skill with none of the context it was written in, so any convention living only "in the author's head" is a silent failure waiting to happen.

At runtime no skill reads the whole thing. Each `TERMS.md` section is audience-tagged, and `tools/audit.py --write-terms` generates a per-skill **slice** holding only the sections that bind it — cutting the fixed per-spawn cost roughly in half while keeping the drift-guard.

And it's checked. `tools/audit.py` verifies every skill and agent against the contract — frontmatter validity, slice load-lines, reference resolvability, skill-name resolution, and that every generated slice still matches `TERMS.md` — deterministically, on every push via CI. It's the framework's own "trust, but verify" turned on itself.

*(Operational detail — the folder map, the `CLAUDE.md` fields, the Change rules, running the audit — lives in **[DIRECTIONS.md](DIRECTIONS.md)**.)*

---

## Version

**v1.1** — adds brownfield `adopt` and reorganizes generated output under a single `Plumbline/` folder. Each skill carries a `version:` in its frontmatter, and every scaffolded project's `CLAUDE.md` records the version it was born under, so a project can tell when the skills have moved on without it.

## License

[MIT](LICENSE) © 2026 BytesFromToby
