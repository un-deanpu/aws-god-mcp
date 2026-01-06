FROM python:3.11-slim

# 讓 Log 不會被卡住，直接印出來
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install "mcp[sse]" uvicorn boto3

COPY server.py .

# 內部統一用 8000，這裡寫 8000 就好 
EXPOSE 8000

CMD ["python", "server.py", "--sse"]
