"""
Lambda Service 2 — luas-permukaan-kubus
=======================================
Computes the surface area of a cube (6 x luas_sisi) by calling
Lambda Service 1 (luas-persegi) over HTTP through its Function URL.

Input (POST JSON via Function URL, AuthType NONE):
    { "rusuk": 3 }

Output:
    200 { "rusuk": 3.0, "luas_sisi": 9.0, "luas_permukaan": 54.0, "satuan": "cm^2" }
    400 { "error": "..." }   invalid input
    502 { "error": "..." }   upstream luas-persegi unreachable / misconfigured
    200 ""                   CORS preflight (OPTIONS)

Required environment variable (Lambda console → Configuration →
Environment variables):
    LUAS_PERSEGI_URL = https://<id>.lambda-url.<region>.on.aws/
"""

import json
import os

import urllib3  # bundled with the Lambda Python runtime (boto3 dependency)


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
}

LUAS_PERSEGI_URL = os.environ.get("LUAS_PERSEGI_URL", "").rstrip("/")

# Reused across invocations on warm containers.
HTTP = urllib3.PoolManager(timeout=urllib3.Timeout(connect=2.0, read=5.0), retries=1)


def build_response(status_code: int, payload: dict | None = None) -> dict:
    return {
        "statusCode": status_code,
        "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
        "body": json.dumps(payload) if payload is not None else "",
    }


def parse_input(event: dict) -> dict:
    """Accept both calling conventions:
      - Function URL:  { "body": "{\"rusuk\": 3}", ... }
      - Console test:  { "rusuk": 3 }
    """
    body = event.get("body")
    if isinstance(body, str) and body.strip():
        return json.loads(body)
    if isinstance(body, dict):
        return body
    return event


def luas_satu_sisi(rusuk: float) -> float:
    """Call Lambda 1 (luas-persegi) via its public Function URL."""
    if not LUAS_PERSEGI_URL:
        raise RuntimeError("env var LUAS_PERSEGI_URL is not set")

    response = HTTP.request(
        "POST",
        LUAS_PERSEGI_URL,
        body=json.dumps({"sisi": rusuk}),
        headers={"Content-Type": "application/json"},
    )
    if response.status != 200:
        raise RuntimeError(
            f"luas-persegi answered HTTP {response.status}: "
            f"{response.data.decode('utf-8', 'ignore')}"
        )

    return float(json.loads(response.data)["luas_persegi"])


def lambda_handler(event, context):
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return build_response(200)

    try:
        rusuk = float(parse_input(event)["rusuk"])
        if rusuk < 0:
            raise ValueError("rusuk must be >= 0")
    except (KeyError, TypeError, ValueError):
        return build_response(400, {"error": "Body JSON must contain a numeric 'rusuk' >= 0"})

    try:
        luas_sisi = luas_satu_sisi(rusuk)
    except Exception as exc:  # upstream/config failure, not the caller's fault
        return build_response(502, {"error": f"Failed to call luas-persegi: {exc}"})

    luas_permukaan = round(6 * luas_sisi, 10)
    return build_response(200, {
        "rusuk": rusuk,
        "luas_sisi": luas_sisi,
        "luas_permukaan": luas_permukaan,
        "satuan": "cm^2",
    })
