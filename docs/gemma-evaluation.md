# Gemma live evaluation

## Current result

**Attempted on 2026-10-13; no diagnosis was returned for any case.** The evaluator used the locally configured `gemma-4-26b-a4b-it` setting and dummy case inputs:

| Case | Observed result |
| --- | --- |
| Wrong database port | Backend HTTP 502, generic provider request failure |
| Database-name mismatch | Backend HTTP 502, Google Gen AI HTTP 504 temporary server error |
| Incomplete context | Backend HTTP 502, Google Gen AI HTTP 504 temporary server error |
| Healthy input | Backend HTTP 502, generic provider request failure |

A separate minimal provider probe returned Google Gen AI HTTP 500 `INTERNAL`. A later single direct backend diagnosis invocation also raised the sanitized HTTP 502 provider request failure. It was not issued from the browser UI. These results do not establish whether a credential, account permission, network, model access, or provider service caused the failures. There were no successful model identifiers, findings, citations, or proposals, so model access and response quality remain unverified; no accuracy or success is claimed.

During the Phase 4 retest, the configured local `.env` key was present, but its rotation from the previously exposed key was not confirmed. One direct invocation of `app.analyzer.diagnose()` returned the generic HTTP 502. No second live request was made, no response was served through the browser, and the UI must not be described as completing a live diagnosis.

The key used in the local ignored `.env` had previously been pasted into chat. Rotation was not independently confirmed. Rotate it in Google AI Studio if that has not already happened. Do not copy credential values into this document, chat, screenshots, or Git.

The Google Gen AI Python SDK is installed, and the backend's structured JSON response schema is accepted by the installed SDK. That verifies local SDK configuration compatibility only; it does not prove API access or model availability.

## Run when credentials are available

After rotation and a basic provider/account access check, set `GEMINI_API_KEY` and `GEMMA_MODEL` in the repository-root `.env` file. Keep `.env` local and uncommitted. First make at most one small live request. If it fails, stop and investigate the provider/key/model access rather than repeating it. If a live diagnosis succeeds, the four-case runner can be used:

```bash
.venv/bin/python backend/evaluate_gemma.py
```

The evaluator makes one sequential SDK call per case with no application-level retry loop, prints only outcome metadata and a short summary, and does not write raw samples or provider responses to disk. It stops after a quota response. The cases use dummy credentials and cover wrong database port, database-name mismatch, incomplete context, and healthy input. Record the observed output here only after the run; do not replace actual results with expected diagnoses.

## Interpretation limits

- A successful response and source-matched citation demonstrate API behavior and traceability, not causal correctness.
- The healthy case is an input for model evaluation, not a runtime health check.
- A YAML syntax-valid suggestion is not proof of deployment recovery.
- Provider/model availability can depend on the account and may change over time.
