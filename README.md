# aws-god-mcp
A set of MCP server code and a dockerfile, which can establish a image that we can deploy as a server.

# AWS God Mode Sidecar for MCP ⚡

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Docker](https://img.shields.io/badge/docker-supported-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An omnipotent AWS tool implementing the **Model Context Protocol (MCP)** via `FastMCP`.
This sidecar allows LLMs (like Claude) to execute **ANY** AWS API call directly using `boto3`.

一個基於 `FastMCP` 實作的全能 AWS 工具。
此 Sidecar 允許 LLM（如 Claude）透過 `boto3` 直接執行 **任何** AWS API 呼叫。

> [!CAUTION]
> **⚠️ WARNING / 警告**
> 
> This tool provides extensive access to your AWS account. Use with extreme caution. Always adhere to the Principle of Least Privilege when configuring IAM roles.
> 
> 此工具提供對 AWS 帳號的廣泛存取權限。使用時請極度謹慎，並務必遵循 IAM 最小權限原則。

---

## Features (功能)

* **God Mode Access**: Wraps `boto3` to call any service and any method dynamically.
* **Docker Ready**: Includes a `Dockerfile` for easy deployment and isolation.
* **FastMCP Hack**: Includes a workaround to force `uvicorn` to bind to `0.0.0.0`.
* **Safety Latch**: Built-in protection against dangerous keywords (e.g., `delete`, `terminate`).

## Prerequisites (前置需求)

* **Option A (Python)**: Python 3.10+, `pip`
* **Option B (Docker)**: Docker Desktop installed
* **AWS Credentials**: Configured via `~/.aws/credentials` or Environment Variables.

---

## Installation & Usage (安裝與使用)

### Method 1: Using Python (Recommended for Local Dev)
**方法一：使用 Python (本機開發推薦)**

1.  **Clone and Install / 下載並安裝**:
    ```bash
    git clone [https://github.com/un-deanpu/aws-god-mcp.git](https://github.com/un-deanpu/aws-god-mcp.git)
    cd aws-god-mcp
    pip install -r requirements.txt
    ```

2.  **Run Server / 啟動伺服器**:
    ```bash
    python server.py
    ```

### Method 2: Using Docker
**方法二：使用 Docker**

1.  **Build Image / 建置映像檔**:
    ```bash
    docker build -t aws-god-mode .
    ```

2.  **Run Container / 啟動容器**:
    (Remember to mount your AWS credentials so the container can access them)
    ```bash
    docker run -it --rm -p 8000:8000 \
      -v ~/.aws:/root/.aws \
      -e AWS_PROFILE=default \
      aws-god-mode
    ```

---

## Connect to Claude Desktop (連接到 Claude Desktop)

Add the corresponding configuration to your `claude_desktop_config.json`.

請將以下對應的設定加入您的 `claude_desktop_config.json` 檔案中。

### Option A: If you run with Python (Local File)
**選項 A：如果您使用 Python 直接執行**

```json
{
  "mcpServers": {
    "aws-god-mode": {
      "command": "python",
      "args": [
        "/absolute/path/to/aws-god-mcp/server.py"
      ],
      "env": {
        "AWS_PROFILE": "default",
        "AWS_REGION": "ap-northeast-1"
      }
    }
  }
}
```
*(Note: Replace /absolute/path/to/... with your actual file path)*

### Option B: If you want Claude to run Docker
**選項 B：如果您希望用 Docker 執行 Claude**

```json
{
  "mcpServers": {
    "aws-god-mode": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/Users/your_username/.aws:/root/.aws",
        "-e", "AWS_PROFILE=default",
        "-e", "AWS_REGION=ap-northeast-1",
        "aws-god-mode"
      ]
    }
  }
}
```
*(Note: You must build the image using docker build -t aws-god-mode . first. Windows users may need to adjust the volume path format.)*

## Example Prompts (提示詞範例)

You can ask Claude to perform almost any AWS task:

* "List all S3 buckets in my account."
* "Check the status of EC2 instance `i-xxxxxx`."
* "Create a Lambda function named `hello-world`." (Will trigger safety confirmation)

---

## Technical Details (技術細節)

### The FastMCP Host Hack

Standard `FastMCP` does not easily expose the host binding configuration (defaulting to localhost). This script uses introspection to find the underlying ASGI app and runs it directly with `uvicorn` to bind to `0.0.0.0`.

標準的 `FastMCP` 封裝較嚴格，不易修改 Host 綁定。本腳本使用 Python 的 Introspection 技術抓出底層的 ASGI App，並透過 `uvicorn` 強制執行，以支援外部連線。

## License

MIT License. See [LICENSE](LICENSE) for more details.
