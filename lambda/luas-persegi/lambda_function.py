"""
Lambda Service 1 — luas-persegi
================================
Computes the area of a square (sisi x sisi).

Input (POST JSON via Function URL, AuthType NONE):
    { "sisi": 5 }

Output:
    200 { "luas_persegi": 25.0, "satuan": "cm^2" }
    400 { "error": "..." }   invalid input
    200 ""                   CORS preflight (OPTIONS)

Note: Function URLs have no built-in CORS handling. The browser sends an
OPTIONS preflight before a JSON POST, so the handler must answer it and
attach CORS headers to every response.
"""

import json


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
}


def build_response(status_code: int, payload: dict | None = None) -> dict:
    """Wrap a payload into the response shape expected by a Function URL."""
    return {
        "statusCode": status_code,
        "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
        "body": json.dumps(payload) if payload is not None else "",
    }


def parse_input(event: dict) -> dict:
    """Accept both calling conventions:
      - Function URL:  { "body": "{\"sisi\": 5}", ... }
      - Console test:  { "sisi": 5 }
    """
    body = event.get("body")
    if isinstance(body, str) and body.strip():
        return json.loads(body)
    if isinstance(body, dict):
        return body
    return event


def lambda_handler(event, context):
    # 1) CORS preflight: OPTIONS reaches the function code on a Function URL.
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return build_response(200)

    # 2) Validate input.
    try:
        sisi = float(parse_input(event)["sisi"])
        if sisi < 0:
            raise ValueError("sisi must be >= 0")
    except (KeyError, TypeError, ValueError):
        return build_response(400, {"error": "Body JSON must contain a numeric 'sisi' >= 0"})

    # 3) Compute.
    luas = round(sisi * sisi, 10)
    return build_response(200, {"luas_persegi": luas, "satuan": "cm^2"})
