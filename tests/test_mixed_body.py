from fastapi import FastAPI, Body, Form
from pydantic import BaseModel
from fastapi.testclient import TestClient

app = FastAPI()

class Item(BaseModel):
    name: str

@app.post("/")
def endpoint(
    json_body: Item = Body(None),
    form_name: str = Form(None)
):
    if json_body: return {"mode": "json", "name": json_body.name}
    if form_name: return {"mode": "form", "name": form_name}
    return {"error": "missing"}

client = TestClient(app)

print("--- JSON Request ---")
try:
    print(client.post("/", json={"name": "foo"}).json())
except Exception as e:
    print("JSON Failed:", e)

print("\n--- Form Request ---")
try:
    print(client.post("/", data={"form_name": "bar"}).json())
except Exception as e:
    print("Form Failed:", e)
