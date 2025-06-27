# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# 從 game_logic.py 導入你的邏輯
from game_logic import START_ID, get_scene_data

app = FastAPI(
    title="互動式故事遊戲 API",
    description="提供遊戲場景數據的後端 API",
    version="1.0.0"
)

# --- CORS (跨域資源共享) 配置 ---
# 允許前端應用程式訪問後端。在開發環境中通常設置為 "*" 允許所有來源。
# 在生產環境中，請務必將 allow_origins 替換為你的前端網域！
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 允許所有來源 (開發階段)
#     allow_credentials=True,
#     allow_methods=["GET"], # 只允許 GET 請求
#     allow_headers=["*"],  # 允許所有標頭
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://alexanderchen5966.github.io",
                   ],  # 開發時前端 Vue 執行的網址
    # allow_origins=["*"],  # ⚠️ 僅限開發階段使用，生產環境建議寫明確網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API 端點 ---

@app.get("/api/start_id", summary="獲取遊戲的起始場景ID")
async def get_game_start_id():
    """
    回傳遊戲的起始場景 ID，前端應用程式會以此 ID 開始載入遊戲。
    """
    return {"start_id": START_ID}

@app.get("/api/scene/{scene_id}", summary="根據場景ID獲取場景數據")
async def get_scene_details(scene_id: int):
    """
    根據提供的場景 ID 獲取該場景的詳細數據，
    包括標題、對話、背景圖片、背景音樂以及所有可用的互動選項。
    """
    try:
        scene_data = get_scene_data(scene_id)

        # --- 調整媒體資源路徑為前端可用的 URL ---
        # 假設前端的靜態資源 (圖片, 音效) 最終會放在網站根目錄下的 /assets/images 和 /assets/sounds
        if scene_data.get("image"):
            scene_data["image"] = f"public/assets/images/{scene_data['image']}"
        if scene_data.get("sound"):
            scene_data["sound"] = f"public/assets/sounds/{scene_data['sound']}"
        # 點擊特效的音效和圖片路徑讓前端自己處理，因為它們通常是小型的、固定的資源

        return scene_data
    except KeyError:
        # 如果 get_scene_data 找不到場景，會拋出 KeyError
        raise HTTPException(status_code=404, detail=f"場景 ID {scene_id} 未找到。")
    except Exception as e:
        # 捕捉其他可能的錯誤
        raise HTTPException(status_code=500, detail=f"伺服器內部錯誤: {str(e)}")

# --- 運行伺服器 (開發模式) ---
if __name__ == "__main__":
    # 在 PyCharm 中，你可以配置運行/調試配置來執行這個檔案
    # 或者在終端機中，進入 backend 資料夾，運行以下命令：
    # uvicorn main:app --reload --host 0.0.0.0 --port 8000
    print("FastAPI 服務已啟動，請訪問 http://127.0.0.1:8000/docs 查看 API 文件。")
    uvicorn.run(app, host="0.0.0.0", port=8080)
    # uvicorn.run("main:app", host="0.0.0.0", port=8080)