from PIL import Image as PillowImage
from pydantic import BaseModel
import os
import asyncio
from pathlib import Path
import uuid # For unique IDs in filenames
# import urllib.parse # For URL decoding path components - Moved to path_utils
# import platform # To check OS - Moved to path_utils
# import re # Import re for regex matching - Moved to path_utils
from utils.path_utils import _normalize_path

# 從 google_genai 工具導入必要的函數
from .google_genai import generate_text_from_google

class SubAreaBounds(BaseModel):
    x: int
    y: int
    width: int
    height: int

async def get_subarea_description(
    image_path: str, 
    bounds_list: list[SubAreaBounds], 
    prompt: str,
    current_working_dir: str
) -> dict[str, str]:
    """
    Crops multiple sub-areas from an image, saves them to uniquely named files (containing bounds info)
    in a temporary directory, and then calls the genai function to get descriptions for all sub-areas.

    Args:
        image_path: Path to the original image file.
        bounds_list: A list of SubAreaBounds objects, each defining a sub-area to crop.
        prompt: The common prompt to use for generating descriptions for all sub-areas.
        current_working_dir: The current working directory, used to create a 'tmp/subareas' folder.

    Returns:
        A dictionary where keys are the file paths of the saved sub-area images 
        and values are their corresponding descriptions from the GenAI model or an error message.
    """
    results = {}
    sub_image_paths_for_genai = []
    
    # 標準化 current_working_dir 和 image_path
    normalized_cwd = _normalize_path(current_working_dir)
    normalized_original_image_path = _normalize_path(image_path)

    subareas_tmp_dir = normalized_cwd / "tmp" / "subareas"
    try:
        subareas_tmp_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        error_msg = f"Error creating subarea directory {subareas_tmp_dir}: {str(e)}"
        print(error_msg)
        for bounds_item in bounds_list:
            key = f"subarea_x{bounds_item.x}_y{bounds_item.y}_w{bounds_item.width}_h{bounds_item.height}_ERROR.png"
            results[key] = error_msg
        return results

    try:
        original_image = PillowImage.open(normalized_original_image_path)
    except FileNotFoundError:
        error_msg = f"Error: Original image not found at {normalized_original_image_path}"
        print(error_msg)
        for bounds_item in bounds_list:
            key = f"subarea_x{bounds_item.x}_y{bounds_item.y}_w{bounds_item.width}_h{bounds_item.height}_ORIG_IMG_NOT_FOUND.png"
            results[key] = error_msg
        return results
    except Exception as e:
        error_msg = f"Error opening original image {normalized_original_image_path}: {str(e)}"
        print(error_msg)
        for bounds_item in bounds_list:
            key = f"subarea_x{bounds_item.x}_y{bounds_item.y}_w{bounds_item.width}_h{bounds_item.height}_ORIG_IMG_ERROR.png"
            results[key] = error_msg
        return results

    for bounds_item in bounds_list:
        unique_id = uuid.uuid4().hex[:6]
        # 檔名中包含原始邊界值，saved_image_path 本身是標準化路徑
        filename = f"subarea_x{bounds_item.x}_y{bounds_item.y}_w{bounds_item.width}_h{bounds_item.height}_{unique_id}.png"
        saved_image_path = subareas_tmp_dir / filename # This is already a Path object
        
        try:
            crop_box = (bounds_item.x, bounds_item.y, bounds_item.x + bounds_item.width, bounds_item.y + bounds_item.height)
            cropped_image = original_image.crop(crop_box)
            cropped_image.save(saved_image_path) # Path object can be passed to save
            sub_image_paths_for_genai.append(str(saved_image_path)) # Pass string representation
            results[str(saved_image_path)] = "Pending GenAI description..."

        except Exception as e:
            error_msg = f"Error processing/saving sub-area for bounds {bounds_item}: {str(e)}"
            print(error_msg)
            results[str(saved_image_path)] = error_msg
    
    if not sub_image_paths_for_genai:
        if not results:
             print("No sub-images were successfully processed to send to GenAI.")
        return results

    try:
        genai_results = await generate_text_from_google(prompt=prompt, image_paths=sub_image_paths_for_genai)
        for path, description in genai_results.items():
            # genai_results 鍵是原始傳入的路徑 (已經是標準化的 str(saved_image_path))
            # 所以可以直接用來更新 results 字典
            results[path] = description
            
    except Exception as e:
        error_msg = f"Critical error calling batch generate_text_from_google: {str(e)}"
        print(error_msg)
        for path in sub_image_paths_for_genai:
            if results.get(path) == "Pending GenAI description...":
                results[path] = error_msg
                
    return results 