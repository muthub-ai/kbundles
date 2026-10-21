# Evaluations

Three evaluations in the best-practices format (`skills`, `query`, `files`,
`expected_behavior`), each pinned to a repository and commit so results are
reproducible. `run_evals.py` checks the **deterministic** half of each eval
(graph bands, parse-error reporting, validator verdicts) without a model:

```bash
python3 run_evals.py --source-cache /path/to/clones   # needs the pinned commits checked out or network
```

The **behavioral** half (`expected_behavior`) is judged by running a fresh
agent with the skill loaded on each `query` and comparing against a baseline
run of the same agent **without** the skill:

| Eval | Baseline (no skill) | With skill | Status |
|---|---|---|---|
| 01 Python repo graph | not yet recorded | not yet recorded | protocol defined |
| 02 Low-code inventory | not yet recorded | not yet recorded | protocol defined |
| 03 Negative citation | not yet recorded | not yet recorded | protocol defined |

Record the transcripts' pass/fail per expected behavior here after each run,
across the model tiers you deploy (Haiku, Sonnet, Opus). The five bundles in
`application-bundles/` were produced by agents following this skill's
authoring guide; all passed the validator, which is evidence for the
workflow but not a substitute for the baseline comparison.
