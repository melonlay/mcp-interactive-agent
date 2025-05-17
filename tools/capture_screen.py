import mss
from PIL import Image as PillowImage # 新增 Pillow 導入
import base64
import os
from pathlib import Path
from pydantic import BaseModel # 新增 Pydantic 導入
# utils.path_utils から _normalize_path をインポートする
from utils.path_utils import _normalize_path
# import urllib.parse # For URL decoding path components - Moved to path_utils
# import platform # To check OS - Moved to path_utils
# import re # Import re for regex matching - Moved to path_utils

class ScreenCaptureInfo(BaseModel):
    file_path: str
    width: int
    height: int

async def capture_screen(current_working_dir: str) -> ScreenCaptureInfo:
    """
    Captures the entire screen, saves it to a /tmp directory
    within the provided current_working_dir, and returns the file path along with image dimensions.
    The current_working_dir is normalized, and a normalized file_path is returned.
    """
    try:
        # 標準化 current_working_dir
        normalized_cwd = _normalize_path(current_working_dir)
        
        # 定義儲存路徑
        save_dir = normalized_cwd / "tmp"
        # 建立 /tmp 資料夾 (如果不存在)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        file_name = "screenshot.png"
        # file_path is now a Path object, and will be OS-specific
        file_path_obj = save_dir / file_name

        with mss.mss() as sct:
            monitor = sct.monitors[1]  # 主螢幕
            sct_img = sct.grab(monitor)
            
            # 將圖片儲存到檔案
            # mss.tools.to_png expects a string path
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=str(file_path_obj))
            
            # 使用 Pillow 打開已儲存的圖片以獲取尺寸
            with PillowImage.open(file_path_obj) as img:
                width, height = img.size
            
            # 返回標準化的字串路徑
            return ScreenCaptureInfo(file_path=str(file_path_obj), width=width, height=height)
    except Exception as e:
        print(f"Error capturing and saving screen: {e}")
        # 在錯誤情況下，可以考慮返回包含錯誤訊息的特定結構或引發異常
        # 為了保持返回類型一致，即使是錯誤也用模型結構，但可能包含錯誤標記
        return ScreenCaptureInfo(file_path=f"Error: {str(e)}", width=0, height=0) 