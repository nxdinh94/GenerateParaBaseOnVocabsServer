# 1. Tạo virtualenv, cài deps:

```python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
# 2. Thiết lập credentials:

-- Option A (recommended for server-side production): Tạo Service Account trên Google Cloud, tải `sa.json`, export:

```export GOOGLE_APPLICATION_CREDENTIALS="/path/to/sa.json"
```

- Option B (prototype): đặt `GEMINI_AUTH_METHOD=api_key` và `GEMINI_API_KEY=YOUR_KEY` (tuỳ theo model và Google docs). Mình khuyến nghị dùng `ADC/service `account cho server. 
Google Cloud
Medium

# 3. Chạy server:

```uvicorn app.main:app --reload --port 8000
```

# 4. Ví dụ curl gửi prompt từ frontend:

```curl -X POST "http://127.0.0.1:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Give a short English lesson about present perfect tense for beginners.","max_tokens":200}'
```

Response mẫu:
```
{"result":"The present perfect tense is used to ..."}```


Các URL quan trọng

Swagger UI: 👉 http://127.0.0.1:8000/docs

ReDoc UI: 👉 http://127.0.0.1:8000/redoc


- api `generate-paragraph`: it will 
  - save the **vocabs** to the learned_vocabs collection
  - increase the count field in  the streak collection, if count == 5, 
  make the is_qualified to be true