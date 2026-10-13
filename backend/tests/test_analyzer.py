import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
import asyncio

from app import analyzer
from app.analyzer import compose_facts, parse_compose, redact, validate_citations
from app.main import app
from app.models import DiagnoseRequest


def test_invalid_yaml_rejected():
    with pytest.raises(HTTPException) as err:
        parse_compose("services: [broken")
    assert err.value.status_code == 422


def test_environment_forms_and_unresolved_vars_are_unknown():
    data = parse_compose("""services:
  api:
    environment:
      DB_HOST: ${DB_HOST}
      DB_NAME: appdb
  db:
    ports:
      - target: 5437
        published: 15437
""")
    facts, _ = compose_facts(data)
    assert any("'DB_HOST': None" in line for line in facts)
    assert any("15437:5437" in line for line in facts)
    data = parse_compose("services:\n  api:\n    environment:\n      - DB_HOST=db\n  db:\n    ports:\n      - 15437:5437\n")
    _, checks = compose_facts(data)
    assert any("uses Compose service 'db'" in line for line in checks)


def test_known_host_published_port_and_database_name_mismatches():
    data = parse_compose("""services:
  api:
    environment:
      DB_HOST: db
      DB_PORT: "15432"
      DB_NAME: inventory
    ports:
      - "8000:8000"
  db:
    environment:
      POSTGRES_DB: catalog
    ports:
      - "15432:5432"
""")
    _, checks = compose_facts(data)
    assert any("not its container target 5432" in item for item in checks)
    assert any("differs from 'db' POSTGRES_DB 'catalog'" in item for item in checks)


def test_out_of_range_and_mismatched_citations_rejected():
    for citation in [
        {"source": "logs", "start_line": 2, "end_line": 2, "quote": "x"},
        {"source": "logs", "start_line": 1, "end_line": 1, "quote": "wrong"},
    ]:
        with pytest.raises(HTTPException) as err:
            validate_citations({"findings": [{"evidence": [citation]}]}, {"logs": "actual", "compose": ""})
        assert err.value.status_code == 502


def test_citation_requires_exact_source_span():
    result = {"findings": [{"evidence": [{"source": "logs", "start_line": 1, "end_line": 2, "quote": "line one\nline two"}]}]}
    assert validate_citations(result, {"logs": "line one\nline two", "compose": ""}) is result


def test_redaction_preserves_line_count_and_masks_credentials():
    content = "PASSWORD=hunter2\nAuthorization: Bearer abc.def\npostgres://alice:swordfish@db/app"
    result = redact(content)
    assert len(result.splitlines()) == 3
    assert "hunter2" not in result and "abc.def" not in result and "swordfish" not in result
    assert "[REDACTED]" in result


def test_both_inputs_required():
    with pytest.raises(ValueError):
        DiagnoseRequest(logs=" ", compose="services: {}")


def test_gemma_invalid_output_is_not_presented_as_diagnosis(monkeypatch):
    class Models:
        async def generate_content(self, **kwargs):
            class Response:
                text = "not-json"
            return Response()
    class Client:
        def __init__(self, **kwargs): self.aio = type("Aio", (), {"models": Models()})()
    monkeypatch.setenv("GEMINI_API_KEY", "test-only-dummy")
    monkeypatch.setattr(analyzer.genai, "Client", Client)
    with pytest.raises(HTTPException) as err:
        asyncio.run(analyzer.diagnose(DiagnoseRequest(logs="failure", compose="services:\n  app: {}")))
    assert err.value.status_code == 502
    assert "malformed" in err.value.detail


def test_quota_provider_error_is_clear_and_bounded(monkeypatch):
    class Models:
        async def generate_content(self, **kwargs): raise RuntimeError("429 quota exceeded")
    class Client:
        def __init__(self, **kwargs): self.aio = type("Aio", (), {"models": Models()})()
    monkeypatch.setenv("GEMINI_API_KEY", "test-only-dummy")
    monkeypatch.setattr(analyzer.genai, "Client", Client)
    with pytest.raises(HTTPException) as err:
        asyncio.run(analyzer.diagnose(DiagnoseRequest(logs="failure", compose="services:\n  app: {}")))
    assert err.value.status_code == 429
    assert "quota" in err.value.detail.lower()


def test_api_health_and_missing_credentials_are_clear(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = TestClient(app)
    assert client.get("/api/health").json() == {"status": "ok"}
    response = client.post("/api/diagnose", json={"logs": "error", "compose": "services:\n  app: {}"})
    assert response.status_code == 503
    assert "GEMINI_API_KEY is not configured" in response.json()["detail"]
