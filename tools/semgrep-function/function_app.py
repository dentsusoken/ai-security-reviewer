"""Semgrep Azure Function – runs Semgrep scans and returns normalised findings.

The function receives code files as a JSON payload, writes them to a temp
directory, executes ``semgrep`` with auto-rules, and returns normalised
finding objects compatible with the backend finding schema.
"""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

import azure.functions as func

app = func.FunctionApp()

logger = logging.getLogger(__name__)


@app.function_name(name="RunSemgrep")
@app.route(route="scan", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def run_semgrep(req: func.HttpRequest) -> func.HttpResponse:
    """Execute a Semgrep scan on the provided code files.

    Request body (JSON)::

        {
            "files": [
                {"path": "src/app.py", "content": "import os ..."},
                ...
            ],
            "rules": "auto"          // optional, defaults to "auto"
        }

    Response (JSON)::

        {
            "findings": [ ... ],     // normalised finding list
            "errors": [ ... ],       // semgrep errors if any
            "version": "1.x.x"
        }
    """
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json",
        )

    files = body.get("files", [])
    if not files:
        return func.HttpResponse(
            json.dumps({"error": "No files provided"}),
            status_code=400,
            mimetype="application/json",
        )

    rules = body.get("rules", "auto")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Write code files to temp directory
        for file_entry in files:
            file_path = Path(tmpdir) / file_entry["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_entry["content"], encoding="utf-8")

        # Run semgrep
        try:
            result = subprocess.run(
                [
                    "semgrep",
                    "scan",
                    "--config",
                    rules,
                    "--json",
                    "--no-git-ignore",
                    "--quiet",
                    tmpdir,
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )
        except FileNotFoundError:
            return func.HttpResponse(
                json.dumps({"error": "semgrep binary not found"}),
                status_code=500,
                mimetype="application/json",
            )
        except subprocess.TimeoutExpired:
            return func.HttpResponse(
                json.dumps({"error": "Semgrep scan timed out (300s)"}),
                status_code=504,
                mimetype="application/json",
            )

        # Parse semgrep output
        try:
            semgrep_output = json.loads(result.stdout) if result.stdout else {}
        except json.JSONDecodeError:
            logger.error("Failed to parse semgrep output: %s", result.stdout[:500])
            semgrep_output = {}

        raw_results = semgrep_output.get("results", [])
        errors = semgrep_output.get("errors", [])
        version = semgrep_output.get("version", "unknown")

        # Normalise findings
        findings = []
        for i, r in enumerate(raw_results):
            finding = _normalise_finding(r, i, tmpdir)
            if finding:
                findings.append(finding)

    response = {
        "findings": findings,
        "errors": [{"message": e.get("message", str(e))} for e in errors],
        "version": version,
    }

    return func.HttpResponse(
        json.dumps(response),
        status_code=200,
        mimetype="application/json",
    )


def _normalise_finding(raw: dict, index: int, tmpdir: str) -> dict | None:
    """Convert a raw Semgrep result to the normalised finding schema."""
    extra = raw.get("extra", {})
    metadata = extra.get("metadata", {})

    severity_map = {"ERROR": "high", "WARNING": "medium", "INFO": "low"}
    severity = severity_map.get(extra.get("severity", "INFO"), "low")

    # Strip tmpdir prefix from path
    file_path = raw.get("path", "")
    if file_path.startswith(tmpdir):
        file_path = file_path[len(tmpdir) :].lstrip("/\\")

    cwe_ids = []
    for cwe in metadata.get("cwe", []):
        if isinstance(cwe, str):
            # Extract "CWE-xxx" from strings like "CWE-89: SQL Injection"
            cwe_id = cwe.split(":")[0].strip()
            cwe_ids.append(cwe_id)

    owasp = metadata.get("owasp", [])
    if isinstance(owasp, str):
        owasp = [owasp]

    return {
        "id": f"sast-{index + 1}",
        "source": "semgrep",
        "rule_id": raw.get("check_id", "unknown"),
        "severity": severity,
        "title": metadata.get("message", extra.get("message", "Semgrep finding")),
        "description": extra.get("message", ""),
        "file_path": file_path,
        "line_start": raw.get("start", {}).get("line", 0),
        "line_end": raw.get("end", {}).get("line", 0),
        "code_snippet": extra.get("lines", ""),
        "cwe_ids": cwe_ids,
        "owasp_ids": owasp,
        "confidence": metadata.get("confidence", "MEDIUM"),
        "references": metadata.get("references", []),
    }
