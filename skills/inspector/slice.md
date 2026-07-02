# Inspector — mid-slice check (scope: slice N)

Loaded by the inspector skill's scope dispatch. The SKILL.md attitude, inputs, BLOCKED
conditions, UI rules, and FAIL-vs-BLOCKED routing all apply here; this file adds only what is
specific to a mid-slice check.

## Read-set — deliberately narrow

- The **blueprint part file holding slice N** (or the single blueprint file), and
- `CLAUDE.md` — the test command and run/demo command.

**Do not read the spec.** Mid-slice verifies the *slice's own claim* — its Scope line and step
Done-Whens — not the feature's acceptance criteria; spec judgment belongs to the final sign-off,
when the feature is complete. Do not read other part files or later slices either: your scope is
this slice, and reading beyond it spends fresh eyes on things you may not act on.

## What you are verifying

- Read the slice **Scope** line — that is the claim being checked.
- Check each step's **Done When** condition is actually met (not just checked off).
- **Judge the fidelity of the tests this slice wrote.** A flagged slice is flagged *because* a
  late catch is expensive, so a vacuous test here is exactly what mid-slice inspection exists to
  catch, before code stacks on it. Read each test the slice committed and ask: *would this test
  fail if the condition it encodes were violated?* Record `fidelity: ok` or
  `fidelity: weak — [reason]`. A weak test is a finding routed to builder, never a pass.
- Note any **Deviation** entries the builder logged in this slice — confirm they don't break the
  slice Scope.

## Run the checks

For each step Done-When: prefer the committed test that encodes it; run it and capture the
result. Where no test covers a condition, drive the software directly (run/demo command) to
verify it. Capture **observable evidence** — command run, stdout/stderr, exit code, file output,
or screenshot for UI — and judge pass/fail strictly against the condition text.

## Stamp the blueprint — the stamp is the whole record

Mid-slice writes **no report file**. Append a dated result line to slice N in its part file:

- Pass: `✅ Inspector: PASS — YYYY-MM-DD HH:MM`
- Fail: `❌ Inspector: FAIL — YYYY-MM-DD HH:MM — off spec: [criterion] — expected [x], observed [y]`
  (for several items, summarize: `[N] items off spec: [a]; [b]; …`)

**A FAIL stamp says *why*, not just where.** Name the slice Done-When it violated and the
expected-vs-observed — builder fix mode reads its findings from this stamp and re-runs the
slice's tests for specifics. These stamps are the only write you make; they record a result,
never change a step, Done-When, or scope.

## Hand off

State results inline for a human, and end with the **status line** the caller routes on:

- **All passing:** "Slice [N] clear. Run **builder** for Slice [N+1]." → `PASS`
- **Failures found:** "Slice [N] failed — [N] items off spec; see the stamp. Run **builder** in
  fix mode, then re-run inspector." → `FAIL: [N]`
- **Couldn't inspect:** "Cannot verify — [reason]." → `BLOCKED: [reason]`
