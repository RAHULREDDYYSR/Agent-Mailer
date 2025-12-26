import httpx
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Constructing a raw string with literal newlines in the JSON value, which is INVALID JSON.
# Valid JSON would be "line1\nline2"
# Invalid JSON is "line1
# line2"

invalid_json_body = """{
  "job_description": "Line 1
Line 2",
  "cache_key": "123"
}"""

print("Sending INVALID JSON with literal newlines...")
response = client.post(
    "/generation/context",
    content=invalid_json_body,
    headers={"Content-Type": "application/json"}
)

print(f"Status Code: {response.status_code}")
print("Response Body:", response.text)
