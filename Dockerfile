FROM python:3.11-slim

# ⭐ 新增這行：讓 Log 不會被卡住，直接印出來
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 這裡已經有 uvicorn 了，非常好！不用動
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install "mcp[sse]" uvicorn boto3

COPY server.py .

# 修正：既然我們決定內部統一用 8000，這裡寫 8000 就好 (寫 8001 也沒壞處，只是沒用到)
EXPOSE 8000

CMD ["python", "server.py"]