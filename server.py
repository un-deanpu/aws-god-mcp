import boto3
import json
import logging
import os
import sys
from datetime import date, datetime
from mcp.server.fastmcp import FastMCP
from botocore.exceptions import ClientError

# 設定 Log
# 注意：如果是 Stdio 模式，Log 不能印到 stdout，否則會干擾 MCP 協定
# 這裡簡單設定為只顯示 Warning，或者你可以導向 stderr
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("AWS-God-Mode-Sidecar")

# 1. 初始化
mcp = FastMCP("AWS-God-Sidecar")

# ⚠️ 定義高風險關鍵字
DANGEROUS_KEYWORDS = [
    "delete", "terminate", "remove", "stop", "reboot", 
    "deregister", "detach", "release", "purge"
]

@mcp.tool()
def execute_aws_api(
    service: str, 
    action: str, 
    params_json: str = "{}", 
    region: str = "ap-northeast-1",
    confirm_danger: bool = False
) -> str:
    """
    Directly execute ANY AWS API command using boto3.
    """
    try:
        # 安全檢查
        is_dangerous = any(keyword in action.lower() for keyword in DANGEROUS_KEYWORDS)
        
        if is_dangerous and not confirm_danger:
            return (
                f"🛑 安全攔截 (Safety Latch) 🛑\n"
                f"動作 '{action}' 是高風險操作。\n"
                f"請向使用者確認後，將 'confirm_danger' 設為 True 再執行。"
            )

        logger.info(f"🤖 Request: Service={service}, Action={action}")

        client = boto3.client(service, region_name=region)
        if not hasattr(client, action):
            return f"❌ Error: Service '{service}' does not have method '{action}'."

        try:
            params = json.loads(params_json)
        except json.JSONDecodeError:
            return "❌ Error: params_json must be valid JSON."

        method = getattr(client, action)
        response = method(**params)

        def json_serial(obj):
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        result = json.dumps(response, default=json_serial, indent=2)
        
        if len(result) > 90000: 
            return result[:90000] + "\n... (truncated)"
            
        return result

    except ClientError as e:
        return f"❌ AWS API Error: {e}"
    except Exception as e:
        return f"❌ System Error: {str(e)}"

# 2. 啟動邏輯：自動判斷是「本機 Stdio」還是「Docker/Server SSE」
if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--sse", action="store_true", help="Run in SSE mode (Web Server)")
    args, unknown = parser.parse_known_args()

    # 判斷邏輯：
    # 1. 如果有 --sse 參數，或者環境變數有 MCP_MODE=sse -> 跑 Web Server (Docker 用)
    # 2. 否則 -> 跑 Stdio (Claude Desktop 本機直接用)
    
    if args.sse or os.getenv("MCP_MODE") == "sse":
        print("🌟 God Mode Sidecar starting on 0.0.0.0:8000 (SSE Mode)...", file=sys.stderr)
        
        # 🕵️‍♂️ 駭客解法：挖出 FastMCP 隱藏的內部 App
        internal_app = getattr(mcp, "_fastapi_app", None)
        if not internal_app:
            internal_app = getattr(mcp, "app", None)

        if internal_app:
            uvicorn.run(internal_app, host="0.0.0.0", port=8000)
        else:
            mcp.run(transport='sse')
            
    else:
        # 預設模式：支援 Claude Desktop 的 "command" 設定 (Stdio)
        # 注意：這裡不要 print 任何東西到 stdout，否則會壞掉
        mcp.run()
