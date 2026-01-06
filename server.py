import boto3
import json
import logging
import os
import uvicorn  
from datetime import date, datetime
from mcp.server.fastmcp import FastMCP
from botocore.exceptions import ClientError

# 設定 Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AWS-God-Mode-Sidecar")

# 1. 初始化 (注意：這裡不寫死 Port)
mcp = FastMCP("AWS-God-Sidecar", host="0.0.0.0")

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

# 2. 啟動邏輯：繞過 FastMCP 的限制，直接啟動內核
if __name__ == "__main__":
    import uvicorn
    print("🌟 God Mode Sidecar starting on port 8000...")
    
    # 🕵️‍♂️ 駭客解法：挖出 FastMCP 隱藏的內部 App
    # 官方套件通常把真正的 ASGI App 藏在 _fastapi_app 這個變數裡
    internal_app = getattr(mcp, "_fastapi_app", None)
    
    if not internal_app:
        # 如果找不到 _fastapi_app，試試看有沒有 .app 屬性
        internal_app = getattr(mcp, "app", None)

    if internal_app:
        print("✅ 成功抓到內部 ASGI App！正在強制綁定 0.0.0.0 ...")
        # 這裡我們就能完全控制 host 和 port 了！
        uvicorn.run(internal_app, host="0.0.0.0", port=8000)
    else:
        # 萬一真的運氣不好版本不對，只能兩手一攤試試看預設值 (可能會因為綁定 localhost 而失敗)
        print("❌ 找不到內部 App，死馬當活馬醫，嘗試使用預設 run()...")
        mcp.run(transport='sse')
