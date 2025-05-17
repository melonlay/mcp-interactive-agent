from google import genai # 更新導入方式以符合 Gemini API 快速入門的主要範例
import os
import io
# import base64 #不再需要，因為我們直接處理檔案路徑
from PIL import Image as PillowImage # Pillow 用於圖片處理
# from mcp.server.fastmcp import Image as MCPImage # 不再直接用於函數簽名，改用下面的 ToolImageInput
from pydantic import BaseModel # 導入 BaseModel
import asyncio # 新增導入 asyncio
# import urllib.parse # For URL decoding path components - Moved to path_utils
# import platform # To check OS - Moved to path_utils
from pathlib import Path # For path manipulation
# import re # Import re for regex matching - Moved to path_utils
from utils.path_utils import _normalize_path

# 從環境變數讀取 API 金鑰。
API_KEY = os.getenv("genaikey")

if not API_KEY:
    # 如果環境變數未設定，則拋出錯誤。
    raise ValueError("Google API Key not found. Please set the 'genaikey' environment variable.")

# 注意：根據新的模式，不再需要 genai.configure(api_key=API_KEY)
# Client 將在初始化時直接使用 API_KEY

MODEL_NAME = "gemini-2.5-flash-preview-04-17" # 使用者指定的模型

# 新定義的 Pydantic 模型，用於工具函數的圖片輸入參數
class ToolImageInput(BaseModel):
    file_path: str

async def generate_text_from_google(prompt: str, image_paths: list[str]) -> dict[str, str]:
    """
    使用 Google Generative AI 模型根據提供的文字提示和多個圖片檔案路徑生成文字。
    對於每個圖片，都會獨立調用 client.aio.models.generate_content() 進行非同步操作。

    Args:
        prompt: 要傳送給模型的通用文字提示 (將用於所有圖片)。
        image_paths: 一個包含多個圖片檔案路徑 (str) 的列表。

    Returns:
        一個字典，鍵是原始輸入的圖片檔案路徑，值是模型對該圖片生成的回應文字。
        如果某個圖片處理或API調用發生錯誤，對應的值將是錯誤訊息字串。
    """
    results = {}
    try:
        client = genai.Client(api_key=API_KEY)

        for original_image_path_str in image_paths:
            normalized_path_for_opening = None
            try:
                normalized_path_for_opening = _normalize_path(original_image_path_str)
                pil_image = PillowImage.open(normalized_path_for_opening)
                content_parts = [prompt, pil_image]
                
                # 使用 client.aio.models.generate_content() 進行非同步操作
                response = await client.aio.models.generate_content(
                    model=MODEL_NAME,
                    contents=content_parts
                )
                results[original_image_path_str] = response.text # 使用原始路徑作為鍵
            except FileNotFoundError:
                error_msg = f"Error: Image file not found at {normalized_path_for_opening if normalized_path_for_opening else original_image_path_str}"
                print(error_msg)
                results[original_image_path_str] = error_msg
            except Exception as e:
                error_msg = f"Error processing image {normalized_path_for_opening if normalized_path_for_opening else original_image_path_str} or calling API: {type(e).__name__} - {str(e)}"
                print(error_msg)
                results[original_image_path_str] = error_msg
        
        return results

    except Exception as e:
        # 捕獲 client 初始化或其他未預期的頂層錯誤
        print(f"General error in generate_text_from_google (model: {MODEL_NAME}): {type(e).__name__} - {e}")
        error_details = str(e)
        # 為所有請求的圖片路徑填充一個通用錯誤，因為無法進行個別處理
        for original_image_path_str in image_paths:
            if original_image_path_str not in results: # 避免覆蓋已有的個別錯誤
                 results[original_image_path_str] = f"General error during API call setup (model: {MODEL_NAME}): {type(e).__name__} - {error_details}"
        return results 