# Inspector — final sign-off (scope: final)

Loaded by the inspector skill's scope dispatch. The SKILL.md attitude, inputs, BLOCKED
conditions, UI rules, and FAIL-vs-BLOCKED routing all apply here; this file adds only what is
specific to the final sign-off. The spec is the authority at final — the feature is verified
against the spec's `**Done when:**` items, which no mid-slice check ever touched.

## Read-set — spec in full, blueprint by search

- Read the **spec** (`Planning/specs/[feature]_spec.md`) in full.
- Read `CLAUDE.md` — the test command and run/demo command.
- **Search the blueprint parts; don't read them cover to cover.** The step text is builder's
  business, already verified slice by slice — what final needs from the blueprint is exactly
  three patterns. Grep every part file for:
  1. `[inspect]` slice headings, checked against `✅ Inspector: PASS` stamps — an unstamped
     flagged slice was **deferred** and is yours to inspect now (below);
  2. `**Deviation:**` lines — collect them all;
  3. the final checkpoint and the `- [ ] **Fully inspected**` box — where your stamps go.

  Read a slice in full **only** when the deferred sweep requires inspecting it.

## Step 1 — Sweep deferred inspections first

Any `[inspect]`-flagged slice with no `✅ Inspector: PASS` stamp was skipped mid-build (a `none`
run). Inspect each now exactly as a mid-slice check would — read that slice in full, confirm its
Scope holds in the built code, judge the fidelity of the tests it wrote, and stamp it. A
`flagged`/`full` run leaves nothing to sweep. Either way, **no `[inspect]` slice ships
uninspected.**

## Step 2 — Collect the criteria

Parse every `**Done when:**` item from the spec. Record: item text, tag, feature it belongs to.
State totals: **[N] automated, [M] human-required.** If any item carries **neither** tag, stop
and report the untagged-criterion `BLOCKED` condition (SKILL.md Inputs) — never guess a tag.

## Step 3 — Run each automated item

For each `[automated]` item:
- **Prefer the committed test that encodes it.** If a test in the suite verifies this item, run
  it — that's the repeatable, pinned check, and its result is the evidence.
- **Judge the test's fidelity, not just its result.** A green test proves the criterion only if
  the test encodes it. Read the backing test and ask: *would this test fail if the criterion
  were violated?* Vacuous assertions, behavior mocked away, the wrong route or fixture
  exercised — any of these means the item is **not proven**, however green the run. Record
  `fidelity: ok` or `fidelity: weak — [reason]` per item. A weak test is a finding routed to
  builder, never a pass. This check matters most when an economy model wrote the tests for its
  own code.
- **If no such test exists,** drive the software directly (run/demo command or the invocation
  the item implies) to verify it this once — *and flag the gap*: an `[automated]` item with no
  backing test is a foreman/builder miss to close, not a permanent state. Note it in the report.
- Capture **observable evidence**: command run, stdout/stderr, exit code, file output, or
  screenshot for UI. Judge pass/fail strictly against the item text. If an `[automated]` item is
  too vague to judge mechanically, that is a **defect in the criterion** (it was never
  observable) — report it back as such; do not silently downgrade it to `needs-human`.

## Step 4 — Capture human-required items

For each `[human-required]` item: run the software to the point the item describes; capture
supporting evidence. Do not judge pass/fail — status is always `needs-human`; the human signs it
off.

Also check the collected **Deviation** notes against the spec criteria — confirm none contradict
them.

## Step 5 — Record the result

**Stamp the blueprint's final checkpoint first** (in the last part file):
- Pass: `✅ Inspector: PASS — YYYY-MM-DD HH:MM`
- Fail: `❌ Inspector: FAIL — YYYY-MM-DD HH:MM — off spec: [criterion] — expected [x], observed [y]
  — see output/inspect/Inspect_[feature]_Final_[date]_[HH-MM].md` (for several items, summarize:
  `[N] items off spec: [a]; [b]; …`)

**On a clean pass only — tick `Fully inspected`:** change `- [ ] **Fully inspected**` to `- [x]`.
That tick guarantees every `[inspect]` slice *and* the final sign-off passed; **never** tick it
while any flagged slice is unstamped or any item failed.

**Always write the report** to `output/inspect/Inspect_[feature]_Final_[YYYY-MM-DD]_[HH-MM].md`
(create the folder if needed — the `HH-MM` keeps a post-fix re-inspection from overwriting the
failed one, so the audit shows both). Name evidence files
`[spec|blueprint]_[feature]_final_[YYYY-MM-DD]_[HH-MM].png|txt` for traceability.

```
# Inspect Report — [Feature] · Final
Spec: Planning/specs/[feature]_spec.md
Blueprint: Planning/blueprints/[feature]_BP.md   (or the _p-N part set)
Date: YYYY-MM-DD
Run/demo command: `...`

Summary: [X] passed · [Y] failed · [Z] need human sign-off

## Results
| Criterion | Status | Fidelity | Evidence |
|-----------|--------|----------|----------|
| [item text] | PASS / FAIL / needs-human | ok / weak — [reason] / n/a | command + key output (or path under output/inspect/) |

## Deviations noted
| Step | Deviation | Impact |
|------|-----------|--------|
| [step] | [what changed] | None / [describe if it affects criteria] |

## Human sign-off
Review each, tick when verified:
- [ ] [item text] — evidence: [screenshot path / output snippet]

## Failures
- [item text] — expected [x], observed [y]. Evidence: [...]
```

Drop **Deviations noted**, **Failures**, or **Human sign-off** if empty.

## Step 6 — Hand off

Report for a human, and end with the **status line** the caller routes on:

- **All passing:** "Feature verified — Fully inspected. Review human sign-off items in the
  report, then ship." → `PASS · needs-human: [Z]`
- **Failures found:** "Inspection failed — [N] items off spec. See report. Run **builder** to
  fix, then re-run inspector." → `FAIL: [N]`
- **Couldn't inspect:** "Cannot verify — [reason]." → `BLOCKED: [reason]`
