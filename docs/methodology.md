# Why the process has separate stages

The process starts from the evaluation purpose and the requirements of what
is being evaluated. The tools used to create or run it are a separate choice.

The [README](../README.md#how-the-evaluation-is-built) explains the sequence.
The [workflow](../workflows/generate.md) contains the instructions the assistant
follows. These notes explain the boundaries between the stages.

## Agree on the requirements before writing cases

A task's rules determine what a response is required to do. Source documents
can also contain observations, proposals, examples and preferences. Treating
all of these as instructions can produce a test that demands the wrong thing.

The profile and challenge passes read the same frozen task separately. Their
findings are compared before the test plan is written. The source compiler
checks the declared classifications and exact references. A person must still
decide which rules have authority when the supplied material does not settle it.

The test categories describe requirements of the target. The generator's own
quality checks describe whether the evaluation was built carefully. These
are different questions and use different records.

## Record what changes between cases

A comparison is useful when the changed input explains a difference in the
expected behavior, or establishes that the behavior should stay the same.
The case author states that relationship and the facts held constant.

Python checks the recorded JSON paths against the actual input differences.
A single changed text field can contain several changed facts. Deciding
whether the comparison isolates one factor therefore needs semantic review.

## Keep the intended answer out of initial criterion writing

A case author already has a failure in mind. Passing that intended answer
straight into the criteria-writing context can turn the criteria into a
restatement of the author's assumption.

The initial criteria writer receives one candidate's input in a separate
context. It derives the expected behavior from those instructions and facts.
A later reviewer can see both the case and the criteria and challenge the
reasoning. A revision using that feedback is recorded as review-guided.

This separation is managed by the assistant runtime or operator. The local
commands do not create independent model sessions. Reusing one context must
remain visible in the result's provenance.

## Check whether the criteria reject valid answers

The review considers correct responses, valid alternatives and plausible
mistakes. It checks whether each criterion applies and whether the source
supports it. A stylistic preference should not become a correctness rule.
Missing information can also change what a valid answer is able to establish.

Internal control annotations distinguish a met criterion, a failed criterion,
an unresolved judgment and a criterion that does not apply. These labels have
different meanings. Authored/model-proposed controls do not establish human
calibration.

## Separate coverage from performance

Coverage records which declared requirements have cases and which remain
untested. That tells the reviewer where the collection has gaps. Case counts,
coverage entries and priority weights are not measurements of a target's
success rate.

The casebook presents the definitions. Candidate JSONL contains only the input
for each target invocation. Actual target execution and response grading
require a separate process.

## Use structural checks for the things they can verify

The tools check field types, source text and hashes, identifiers, links,
declared coverage and recorded case differences. These checks catch broken
or inconsistent files.

A reviewer still assesses source authority, the choice of scenarios and the
correctness of the grading criteria. The review record should make any
remaining uncertainty clear.
