---
name: inspector
description: Proves a slice or feature is done by running it. Reads the spec's Done when items, runs the tests that encode them (driving the software where no test exists), captures evidence, stamps the blueprint, and produces a signed report. Runs with fresh eyes — ideally a separate subagent. Run after builder — per slice or final sign-off.
---

## When to use this skill
- After builder completes a slice, to verify it before continuing
- After the final slice, for full feature sign-off

Inspector is read-only on the codebase. It runs the software and reports. It does not fix code — failures are findings for the builder.

---

## Attitude
- You are an inspector, not a builder. Verify what was built against what was specified. You have no stake in the outcome — pass or fail, report what you actually observed.
- **Run with fresh eyes.** Verify only from the artifacts — the spec, the blueprint (for slice scope), the run/demo command, and the running software. Do not rely on the builder's reasoning or any prior conversation about how the code was written; treat the build as a black box. For real independence, run inspector as a separate subagent / fresh session, not a continuation of the build — that makes "no stake" structural, not just a promise.
- Never edit code, the spec, or the blueprint's criteria/steps/scope to make something pass — inspector only observes. The *one* write you may make to the blueprint is your own dated pass/fail stamp on the slice (Step 4): it records a result, never changes what's required.
- Never mark a `human-required` item pass or fail — that is the human's call.
- If the run/demo command fails to launch at all, stop and report that first — nothing else can be verified until it runs.
- Evidence over assertion. A bare "PASS" is not evidence.
- Tone: direct, no padding.

---

## Inputs

Ask the user if not stated:
1. **Which feature** — reads spec from `Planning/specs/[feature]_spec.md` and blueprint from `Planning/blueprints/[feature]_BP.md`
2. **Slice or final** — mid-slice check or full feature sign-off
3. **Run/demo command** — from `CLAUDE.md`

**Stop and report if:**
- The spec has no `**Done when:**` items — nothing to verify against
- CLAUDE.md has no run/demo command — cannot drive the software
- The blueprint has no slice matching what the user specified

---

## Mid-slice vs final

**Mid-slice:** verify that the slice did what it said it would.
- Read the slice **Scope** line from the blueprint — that is the claim being checked
- Check each step's **Done When** condition is actually met (not just checked off)
- Note any **Deviation** entries the builder logged — confirm they don't break the slice scope
- Do not check spec `**Done when:**` items yet — the feature isn't complete

**Final slice:** verify the full feature against the spec.
- Run every `**Done when:**` item from the spec
- Note any builder deviations logged across all slices — confirm none contradict the spec criteria

---

## Step 1 — Collect the criteria

**Mid-slice:** list the slice Scope + each step's Done When from the blueprint.

**Final:** parse every `**Done when:**` item from the spec. Record: item text, tag, feature it belongs to. State totals: **[N] automated, [M] human-required.**

---

## Step 2 — Run each automated item

For each `[automated]` item (or mid-slice Done When condition):
- **Prefer the committed test that encodes it.** If a test in the suite verifies this item, run it — that's the repeatable, pinned check, and its result is the evidence.
- **If no such test exists,** drive the software directly (run/demo command or the invocation the item implies) to verify it this once — *and flag the gap*: an `[automated]` item with no backing test is a foreman/builder miss to close, not a permanent state. Note it in the report.
- Capture **observable evidence**: command run, stdout/stderr, exit code, file output, or screenshot for UI
- Judge pass/fail strictly against the item text. If an `[automated]` item is too vague to judge mechanically, that is a **defect in the criterion** (it was never observable) — report it back as such. Do not silently downgrade it to `needs-human`.
- Record the output

---

## Step 3 — Capture human-required items

**Final only** — skip this step for mid-slice checks.

For each `[human-required]` item:
- Run the software to the point the item describes; capture supporting evidence
- Do not judge pass/fail. Status is always `needs-human` — the human signs it off

---

## Browser / UI stacks

When the run/demo command launches a web UI, use **Playwright (Python)** as the capture engine — to drive the browser and take screenshots. It is the hands and camera, not a test suite.

- Setup (once per project): `pip install playwright` then `playwright install chromium`
- `[automated]` UI item → assert in Playwright (element visible, text present); evidence is the assertion result plus a screenshot
- `[human-required]` UI item → navigate and screenshot only; leave the judgement for sign-off
- Save output

Check CLAUDE.md for a `UI evidence tool` line — a project may declare a different tool.

---

## Step 4 — Record the result

**Always stamp the blueprint first.** On the slice you inspected (or the final checkpoint), append a dated result line:
- Pass: `✅ Inspector: PASS — YYYY-MM-DD HH:MM`
- Fail: `❌ Inspector: FAIL — YYYY-MM-DD HH:MM — see output/inspect/Inspect_[feature]_Slice[N]_[date].md`

This is the only write inspector makes to the blueprint. It records a result — it never changes a step, Done-When, or scope. It gives the blueprint an at-a-glance verification trail even when no report file is written.

Then the report:

**Mid-slice, all passing:** no separate report file — the blueprint stamp is the record. State results inline and hand off.

**Mid-slice, failures found:** write `output/inspect/Inspect_[feature]_Slice[N]_[YYYY-MM-DD].md`.

**Final:** always write `output/inspect/Inspect_[feature]_Final_[YYYY-MM-DD].md`.

All inspection output lives under `output/inspect/` — the report (above) plus screenshots and supporting files. Create the folder if it doesn't exist. Name evidence `[blueprint|spec]_[feature]_[slice|final]_[YYYY-MM-DD].png|txt` for traceability.

```
# Inspect Report — [Feature] · [Slice N / Final]
Spec: Planning/specs/[feature]_spec.md
Blueprint: Planning/blueprints/[feature]_BP.md
Date: YYYY-MM-DD
Run/demo command: `...`

Summary: [X] passed · [Y] failed · [Z] need human sign-off

## Results
| Criterion | Status | Evidence |
|-----------|--------|----------|
| [item text] | PASS / FAIL / needs-human | command + key output (or path under output/inspect/) |

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

Drop **Deviations noted** if none. Drop **Failures** if none. Drop **Human sign-off** if none.

---

## Step 5 — Hand off

**All passing, mid-slice:** "Slice [N] clear. Run **builder** for Slice [N+1]."

**All passing, final:** "Feature verified. Review human sign-off items in the report, then ship."

**Failures found:** "Inspection failed — [N] items. See report. Run **builder** to fix, then re-run inspector."
