# The choices behind BenchPrime

I built the workflow around a simple requirement: an eval should withstand scrutiny.
Why these cases? Why this expected behavior? What would make a different
answer valid? Each stage makes one of those questions easier to examine.

The workflow separates decisions that are easy to blur together: understanding
the job, choosing the cases, writing the criteria and judging the result.
You can inspect each step and change a bad assumption before it spreads.
The [README](../README.md#how-the-evaluation-is-built) summarizes the choices; the
[workflow](../workflows/generate.md) gives your assistant the execution instructions.

## Establish what the answer is actually required to do

A source can contain a policy, a preference, an observation or a proposed
change. Those roles need to stay explicit. Otherwise, the evaluation can turn
"someone suggested this" into "the answer must do this."

The profile and challenge passes read the same frozen brief separately, then
their interpretations are reconciled. The compiler checks declared source
roles and exact references. A reviewer still has to settle which rules govern
the task when the material is ambiguous.

The evaluation's purpose and the system's instructions serve different jobs.
"Help me choose between two models" is a reason to evaluate.
It is not an extra requirement for either model's response.

## Map the job before multiplying the cases

The collection should explain its categories before asking you to inspect
individual cases. Each category needs a reason to exist, and each deeper
branch needs to expose another meaningful distinction.

The [design catalogue](../benchprime/patterns/design_principles.json) contains
eleven responsibilities and ten guiding principles for designing the evaluation.
The capabilities being evaluated come from your use case. A well-formed
test suite can still miss the behavior that matters to you.

<picture>
  <source media="(max-width: 640px)" srcset="../assets/methodology-atlas-mobile.png">
  <img src="../assets/methodology-atlas.png" alt="Eleven responsibilities for designing an evaluation, distinct from the capabilities being evaluated.">
</picture>

## Use controlled changes to make a failure easier to explain

A useful pair of cases shows what changed and why the expected answer
should change or stay stable. When several facts change together, attributing
the result to just one of them needs further evidence.

The local tools compare the recorded JSON paths with the actual input
differences. That catches a mismatch in the files. Review still matters:
one changed paragraph can contain three changed facts.

Include cases where the system should succeed, where stronger evidence
changes the answer, and where two requirements interact. This gives a
reviewer more to work with than a collection of difficult-looking questions.

<picture>
  <source media="(max-width: 640px)" srcset="../assets/methodology-depth-mobile.png">
  <img src="../assets/methodology-depth.png" alt="From capability to distinction, failure mechanism and an observable difference; each deeper branch needs a reason to exist.">
</picture>

## Keep the intended answer out of the first criteria-writing pass

Designing a case around a failure creates an expectation.
Handing that expectation to the criteria writer can make the key repeat
the same assumption. The first pass therefore receives only one case's input
and an opaque ID in a fresh context.

A later reviewer sees both the case and the proposed criteria. Feedback can
change either. A repair using that feedback is labelled **review-guided**, because
the information available in that pass differs from the initial reading.

Your assistant/runtime must manage those separate contexts. The Python tools
do not create them. Work that shares a context throughout stays labelled
**author-assisted**.

## Try to break the grading criteria before trusting them

Try a competent alternative, a convincing mistake and a case where the check
stops applying. A plausible expected answer alone leaves those weaknesses
unexamined.

The [review guide](reviewing-an-evaluation.md) gives a concrete example:
a task makes section references optional, but the proposed rubric requires
them. The answer is valid. The check needs correcting.

Criterion validity and response performance need separate judgments. Correcting a
bad check improves the evaluation; the target's output has not changed.
Similarly, `met`, `not_met`, `unresolved` and `not_applicable` answer different
questions. Collapsing them can hide the very problem the eval should reveal.
Authored or model-proposed controls still need human calibration.

<picture>
  <source media="(max-width: 640px)" srcset="../assets/methodology-review-mobile.png">
  <img src="../assets/methodology-review.png" alt="Case-only initial criteria writing followed by review of valid alternatives, mistakes, ambiguity and repairs.">
</picture>

## Make gaps and limits part of the result

Every declared requirement gets a case or a named gap. Importance, severity
and case allocation remain separate design choices. Performance requires
actual target responses and judgments; a coverage map alone cannot establish it.

Read the evaluation as HTML or inspect the JSON, with a separate
export of candidate inputs. That lets you use your own runner while keeping
the answer key out of the test.

The tools verify file structure, source quotations and hashes, references,
declared coverage and recorded differences. A person still decides whether
the tests are useful and the criteria are fair. The
[evidence page](evidence-and-limitations.md) records where the current examples
stand on those questions.
