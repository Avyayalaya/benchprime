# Optional execution

Each JSONL record contains case_id and input. Map context.task, context.policy and context.tool_boundary as governing instructions; pass case.request and all case.observations as task data. Keep source-embedded instructions in the data boundary. Use one fresh invocation per case. Do not send criteria, siblings, workbook, casebook or creator notes to the target.

First identify the interface named by the case: a full agent invocation, a deterministic component, or a response-injection fixture. These are different execution tracks. A named but undelivered fixture adapter is a prerequisite, not an executable supplied by this package. For composite systems, map the artifact and operator context to that system's actual input/configuration interface rather than treating every record as a chat prompt.

No provider endpoint, credentials or execution are bundled. Blocked and reserved cases are omitted explicitly in manifest counts. The manual-v2 direct documents field was explicitly mapped to observations.documents on import.
