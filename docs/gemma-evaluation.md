# Gemma live evaluation

## Current result

**Live evaluation attempted on 2026-10-13; no diagnosis was returned for any case.** The evaluator made one sequential request for each case using the locally configured key and `gemma-4-26b-a4b-it`:

| Case | Observed backend result |
| --- | --- |
| Wrong database port | HTTP 502; generic provider request failure |
| Database-name mismatch | HTTP 502; Google Gen AI HTTP 504 temporary server error |
| Incomplete context | HTTP 502; Google Gen AI HTTP 504 temporary server error |
| Healthy input | HTTP 502; generic provider request failure |

A separate minimal provider probe returned Google Gen AI HTTP 500 `INTERNAL`. These errors did not produce model identifiers, findings, citations, or proposed changes. **Model availability and response quality therefore remain unverified; no accuracy or successful diagnosis is claimed.** The generic failures do not establish whether the key, network, provider service, or model access caused those individual requests to fail.

The Google Gen AI Python SDK is installed, and the backend's structured JSON response schema is accepted by the installed SDK. That verifies local SDK configuration compatibility only; it does not prove API access or model availability.

## Run when credentials are available

After confirming provider access, set `GEMINI_API_KEY` and `GEMMA_MODEL` in the repository-root `.env` file. Keep `.env` local and uncommitted. Then run:

```bash
.venv/bin/python backend/evaluate_gemma.py
```

The evaluator makes one sequential SDK call per case with no application-level retry loop, prints only outcome metadata and a short summary, and does not write raw samples or provider responses to disk. It stops after a quota response. The cases use dummy credentials and cover wrong database port, database-name mismatch, incomplete context, and healthy input. Record future observed outputs here; do not replace actual results with expected diagnoses.

## Interpretation limits

- A successful response and source-matched citation demonstrate API behavior and traceability, not causal correctness.
- The healthy case is an input for model evaluation, not a runtime health check.
- A YAML syntax-valid suggestion is not proof of deployment recovery.
- Provider/model availability can depend on the account and may change over time.
