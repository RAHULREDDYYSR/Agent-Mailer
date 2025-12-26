from fastapi.testclient import TestClient
from backend.main import app
from backend.core.security import get_current_user
from backend.core.database import get_db
import uuid
from unittest.mock import AsyncMock, MagicMock

# Mock user
def mock_get_current_user():
    return {"id": str(uuid.uuid4()), "email": "test@example.com"}

# Mock DB
async def mock_get_db():
    mock_session = AsyncMock()
    # Create a mock result object that behaves like the sqlalchemy result
    mock_result = MagicMock()
    mock_user = MagicMock()
    mock_user.user_context = "some existing context"
    
    # scalars().first() -> mock_user
    mock_result.scalars.return_value.first.return_value = mock_user
    
    # db.execute(...) -> mock_result
    # execute is async, so we make it return mock_result
    mock_session.execute.return_value = mock_result
    
    yield mock_session

app.dependency_overrides[get_current_user] = mock_get_current_user
app.dependency_overrides[get_db] = mock_get_db

client = TestClient(app)

# Exact payload from user
user_jd = """Hiring: ML Research Engineer (ASR & Fine-tuning Specialist)📍 Location: Bangalore | 🧠 Experience: 2+ Years | 💼 Full-time | On-site🧩 What You’ll Do🎯 Train & finetuneASRmodels(Whisper, Wav2Vec2, Conformer) for multilingual, healthcare-focused speech data.🧠 Build, optimize, and fine-tune NLP components (Intent, NER, Entity Linking) using transformer-based architectures.🧪 Research & implement SOTA fine-tuning techniques — LoRA, QLoRA, or full fine-tuning — to push real-world model performance.🧰 Design data pipelines for collection, annotation, augmentation, and synthetic generation in low-resource languages.📊 Develop robust evaluation frameworks — precision, recall, F1, and domain benchmarks.🤝 Collaborate with AI engineers to deploy optimized models into production-ready pipelines powering healthcare voice systems.
🧬 You’re a Great Fit If You Have2+ years of ML/DL research or applied model training experience.Hands-on expertise in ASR systems or LLM fine-tuning workflows.
Strong command over PyTorch or TensorFlow, distributed training, and model evaluation.
Practical exposure to multilingual datasets, cross-l"""

payload = {
    "job_description": user_jd,
    "cache_key": "string"
}

print("Sending request with EXACT USER PAYLOAD via TestClient...")
try:
    response = client.post("/generation/context", json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print("Response Body:", response.text)
    else:
        print("Success! Response:", response.json())
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Request failed: {e}")
