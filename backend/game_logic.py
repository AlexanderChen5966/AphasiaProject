# backend/game_logic.py
import os
import json

# 定義 JSON 檔案的路徑
# os.path.dirname(__file__) 獲取當前檔案 (game_logic.py) 的目錄
# os.path.join 確保路徑在不同操作系統下都能正確組合成 / 或 \
JSON_PATH = os.path.join(os.path.dirname(__file__), "assets", "zombie_interactive_story_fully_ready3.json")

# 全局變數用於儲存載入的遊戲數據
GAME_DATA = {}
START_ID = 1
SCENES = {} # 用於快速查找場景資訊，特別是 title

def load_game_data():
    """載入遊戲 JSON 數據並初始化全局變數。"""
    global GAME_DATA, START_ID, SCENES
    if not os.path.exists(JSON_PATH):
        raise FileNotFoundError(f"遊戲數據文件未找到: {JSON_PATH}")

    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            GAME_DATA = json.load(f)
        START_ID = GAME_DATA.get("start_id", 1) # 如果 JSON 沒有定義，預設為 1

        # 將 scenes 轉換為字典以便於通過 ID 快速查找
        SCENES = {scene['id']: scene for scene in GAME_DATA.get("scenes", [])}
        print(f"遊戲數據載入成功，起始 ID: {START_ID}, 共 {len(SCENES)} 個場景。")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 文件解析錯誤: {e}")
    except Exception as e:
        raise RuntimeError(f"載入遊戲數據時發生未知錯誤: {e}")

def get_scene_data(scene_id: int):
    """
    根據場景 ID 獲取該場景的數據。
    返回的數據結構會包含前端所需的所有資訊，並調整路徑。
    """
    if not GAME_DATA:
        load_game_data() # 確保數據已載入

    scene_info = SCENES.get(scene_id)
    if not scene_info:
        raise KeyError(f"場景 ID {scene_id} 未找到。")

    # 提取必要資訊並組裝成前端需要的格式
    extracted_data = {
        "id": scene_info.get("id"),
        "title": scene_info.get("title", "未知場景"),
        "dialogue": [scene_info.get("text", "")], # 根據你的需求，這裡是一個列表
        "hint": scene_info.get("hint", ""),
        "triggers": [],
        "image": scene_info.get("image"),
        "sound": scene_info.get("sound")
    }

    # 處理 triggers
    for trigger in scene_info.get("triggers", []):
        extracted_data["triggers"].append({
            "pattern": trigger.get("pattern", ""),
            "response": trigger.get("response", ""),
            "next_id": trigger.get("next_id")
            # fx_sound 和 fx_image 暫時不在這裡處理，前端可能會自行處理點擊特效
        })

    return extracted_data

# 首次載入模組時即載入數據
load_game_data()

if __name__ == '__main__':
    # 測試載入和獲取數據
    try:
        print(f"遊戲起始 ID: {START_ID}")
        scene_1 = get_scene_data(START_ID)
        print("\n場景 1 數據:")
        print(json.dumps(scene_1, ensure_ascii=False, indent=2))

        scene_invalid = get_scene_data(999) # 測試不存在的 ID
    except (KeyError, FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"錯誤: {e}")