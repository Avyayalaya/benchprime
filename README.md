<!--
THESIS: Make the reasoning behind evaluation design visible inside the README.
OWN-WORLD: Plain GitHub documentation, neutral paper, navy branching maps and short paragraphs.
STORY: Map the design responsibilities, deepen useful distinctions, then challenge the evaluation.
FIRST VIEWPORT: What this is, what it produces and the command to begin.
FORM: Three connected methodology maps extending the existing surface; examples remain references.
-->

# BenchPrime

### Create evals for the purpose and use case you define.

**BenchPrime is an evaluation-creation system.** Start with what you want to
learn, compare or decide, and what you are evaluating. BenchPrime works
through what to test, builds the cases and defines how the results should
be judged.

The purpose shapes the test design. The use case supplies the requirements
and context. You get test cases, grading criteria and a record of what the
evaluation covers and leaves open.

**[Start with your task](START_HERE.md)** ·
**[Read the full workflow](workflows/generate.md)** ·
**[Command reference](docs/getting-started.md)**

## Use the current local package

This repository packages one way to use BenchPrime: an assistant-led workflow
with Python tools for checking and exporting files. Use an AI assistant with
local file access and Python 3.10+ for this route.

```powershell
python -m benchprime start work/my-eval
```

Describe the task in `work/my-eval/task.md`, add the sources it may use, and
paste `work/my-eval/KICKOFF.md` into the assistant. The command creates the
workspace. The assistant then follows the process below using its normal
model runtime.

## How the evaluation is built

### Map the decisions the evaluation needs to support

The use case supplies the capabilities being tested. BenchPrime's eleven
design responsibilities examine the evaluation itself: its intent, grounding,
coverage, scenarios, standards, measurement and usefulness over time.

<picture>
  <source media="(max-width: 640px)" srcset="assets/methodology-atlas-mobile.png">
  <img src="assets/methodology-atlas.png" alt="Eleven evaluation-design responsibilities form three connected groups: intent, boundary and grounding; coverage, scenarios, acceptable behavior and measurement; usability, generation quality, dependable delivery and revision. Source authority constrains criteria; controlled differences constrain diagnosis; review can reopen coverage.">
</picture>

Start by reading the requirements twice, in separate contexts, and reconcile
the findings. A source may contain a governing rule, a preference, a recorded
fact or an instruction for the evaluation's creator. Its role determines what
it can justify. Unsettled authority stays an open question.

Before individual cases, show the collection's scope, categories and why they
were chosen. Connect them to principles and task-specific dimensions, then
lay out themes and scenario groups. The
[design catalogue](benchprime/patterns/design_principles.json) records the
eleven responsibilities and ten guiding principles.

### Deepen each capability until a test can distinguish the failure

Build breadth first, then follow consequential branches:
**capability → distinction → failure mechanism → observable difference**.
Ask which conditions change a valid outcome, what evidence is available,
and which requirements depend on each other.

<picture>
  <source media="(max-width: 640px)" srcset="assets/methodology-depth-mobile.png">
  <img src="assets/methodology-depth.png" alt="An illustrative capability branches into authority, information and dependencies. Each branch separates potential failure mechanisms and proposes a controlled input change. Each contrast records whether behavior should change or remain stable. Interactions receive their own tests; repeated distinctions or unjustified deeper splits become explicit stopping points or gaps.">
</picture>

Each retained scenario must reveal something useful. A comparison records
what changed, what stayed fixed and why the expected behavior should change
or remain stable. A single changed text field can contain several changed
facts; causal isolation still needs review.

Include clear-success and stronger-evidence cases alongside stress cases.
Check combinations where one requirement changes how another applies.
Stop splitting when the next branch repeats a distinction or cannot be
justified with available evidence, and record the gap.

### Challenge the grading criteria with answers that could fool them

The first criteria writer receives only one case's input and an opaque ID.
The author's intended answer, family label and failure hypothesis stay outside
that initial read. Each proposed criterion needs evidence, applicability and
acceptable alternatives.

<picture>
  <source media="(max-width: 640px)" srcset="assets/methodology-review-mobile.png">
  <img src="assets/methodology-review.png" alt="The case packet goes to a separate criteria-writing context. A later reviewer sees the case and proposed criteria, checking competent answers, valid alternatives, plausible mistakes and ambiguous responses. Feedback can revise either the case or its criteria. Met, not met, unresolved and not applicable remain distinct review annotations.">
</picture>

The reviewer then challenges both the case and its criteria. Would a valid
alternative fail? Could a plausible mistake pass? Does the criterion apply
when information is missing? Review can send the work back to either artifact.
Revisions using that feedback are recorded as **review-guided**.

Separate contexts are an operator/runtime responsibility. A shared-context
run remains **author-assisted**. Proposed controls help examine the criteria;
they do not establish human calibration.

### Make coverage and remaining uncertainty inspectable

Trace each declared requirement to a case or an explicit gap. Keep importance,
failure severity and case allocation separate. These describe design choices;
actual target runs and grading establish performance.

Export the evaluation definition, HTML casebook and candidate-only inputs.
Keep criteria and reviewer notes outside the material supplied to what is
being evaluated. The [methodology notes](docs/methodology.md) explain these
boundaries in detail.

## What the tools check

The scripts can check whether a quoted passage matches the case input, whether
an ID points to an existing case, and whether every declared requirement has
a coverage entry. They reject inconsistent files and refuse output overwrites.

Judging whether a test is useful or a criterion is correct still requires
review. The assistant runtime or operator manages the separate contexts.
When a single context is used throughout, the result must say that it was
author-assisted.

Running the target and scoring its responses are separate steps. This
repository currently provides one guided creation route and local file tools.
The evaluation purpose, the subject being evaluated and the tools used to
create or run the evaluation are separate choices.

## Files and further detail

Use [Start here](START_HERE.md) for the input and output files,
[the methodology notes](docs/methodology.md) for the reasoning behind the
separate stages, and [the command reference](docs/getting-started.md) for
preparation, validation, rendering and export.

[Sample outputs](packs/README.md) and an
[authored walkthrough](docs/walkthrough.md) are available as references.
Their review limits are recorded with them.

The bundled input formats and examples currently use English text. Other
formats and execution systems need appropriate support; those implementation
limits are separate from BenchPrime's purpose as an eval-creation system.
This is a developer preview. No reuse license has been selected; public
visibility does not grant an open-source license.
See [evidence and limitations](docs/evidence-and-limitations.md) and
[release status](RELEASE_STATUS.json).
