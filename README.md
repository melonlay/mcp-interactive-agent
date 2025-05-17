# Interactive GUI MCP Server Tools

本專案提供了一個 MCP (Model Context Protocol) 伺服器，其中包含一系列用於互動式 GUI 操作和分析的工具。

## 工具說明

以下是目前可用的工具及其使用方法：

### 1. `say_greeting`

*   **用途**: 一個簡單的問候工具，用於測試 MCP 伺服器的基本連接和工具呼叫。
*   **參數**:
    *   `message` (str): 要傳送的問候訊息。如果訊息是 "hello"，它會回覆 "hello"；否則回覆 "hi"。
*   **返回**: 
    *   (str): 問候回覆。
*   **範例呼叫 (假設透過 MCP 客戶端)**:
    ```
    client.tools.say_greeting(message="hello")
    # 預期返回: "hello"
    ```

### 2. `capture_screen`

*   **用途**: 截取整個主螢幕的畫面，將圖片儲存到指定的暫存目錄，並返回圖片的路徑及尺寸。
*   **參數**:
    *   `current_working_dir` (str): 目前的工作目錄路徑。工具會在該路徑下建立一個 `tmp` 資料夾來儲存截圖 (例如 `current_working_dir/tmp/screenshot.png`)。
*   **返回** (一個包含以下欄位的物件/字典):
    *   `file_path` (str): 儲存的截圖檔案的完整路徑。
    *   `width` (int): 截圖的寬度 (像素)。
    *   `height` (int): 截圖的高度 (像素)。
*   **範例呼叫**:
    ```
    client.tools.capture_screen(current_working_dir="/path/to/your/workspace")
    # 預期返回類似: {"file_path": "/path/to/your/workspace/tmp/screenshot.png", "width": 1920, "height": 1080}
    ```

### 3. `generate_text_from_google`

*   **用途**: 使用 Google Generative AI (Gemini 模型) 根據提供的文字提示和多個本地圖片檔案路徑生成描述。
*   **參數**:
    *   `prompt` (str): 要傳送給 AI 模型的通用文字提示 (將用於所有圖片)。
    *   `image_paths` (List[str]): 一個包含多個本地圖片檔案完整路徑的列表。
*   **返回**:
    *   (Dict[str, str]): 一個字典，鍵是原始輸入的圖片檔案路徑，值是模型對該圖片生成的回應文字。如果某個圖片處理或 API 調用發生錯誤，對應的值將是錯誤訊息字串。
*   **範例呼叫**:
    ```python
    image_paths_list = ["/path/to/your/image1.png", "/path/to/your/image2.jpg"]
    client.tools.generate_text_from_google(prompt="詳細描述這張圖片中的主要物件。", image_paths=image_paths_list)
    # 預期返回類似: 
    # {
    #   "/path/to/your/image1.png": "圖片1的文字描述...",
    #   "/path/to/your/image2.jpg": "圖片2的文字描述..."
    # }
    ```

### 4. `get_subarea_description`

*   **用途**: 從指定的原始圖片檔案中裁剪一個或多個子區域，將它們儲存為臨時檔案，然後使用 Google Generative AI 對每個子區域進行描述。
*   **參數**:
    *   `image_path` (str): 原始圖片檔案的完整路徑。
    *   `bounds_list` (List[SubAreaBounds]): 一個 SubAreaBounds 物件的列表，每個物件定義要裁剪的一個子區域。
        *   **SubAreaBounds 物件結構**:
            *   `x` (int): 子區域左上角的 X 座標。
            *   `y` (int): 子區域左上角的 Y 座標。
            *   `width` (int): 子區域的寬度。
            *   `height` (int): 子區域的高度。
    *   `prompt` (str): 針對所有裁剪出的子區域的通用文字提示，用以指導描述生成。
    *   `current_working_dir` (str): 目前的工作目錄路徑。工具會在該路徑下建立 `tmp/subareas` 資料夾來儲存裁剪後的子圖片。
*   **返回**:
    *   (Dict[str, str]): 一個字典，鍵是儲存的子區域圖片檔案的路徑，值是 AI 模型對該子區域生成的文字描述或錯誤訊息。
*   **範例呼叫**:
    ```python
    bounds_to_describe = [
        {"x": 10, "y": 10, "width": 100, "height": 100},
        {"x": 150, "y": 150, "width": 200, "height": 50}
    ]
    client.tools.get_subarea_description(
        image_path="/path/to/your/original_image.png", 
        bounds_list=bounds_to_describe, 
        prompt="這個區域有什麼特別的嗎？",
        current_working_dir="/path/to/your/workspace"
    )
    # 預期返回類似:
    # {
    #   "/path/to/your/workspace/tmp/subareas/subarea_x10_y10_w100_h100_xxxxxx.png": "第一個子區域的描述...",
    #   "/path/to/your/workspace/tmp/subareas/subarea_x150_y150_w200_h50_yyyyyy.png": "第二個子區域的描述..."
    # }
    ```

### 5. `control_input`

*   **用途**: 模擬執行一系列的鍵盤和滑鼠操作。
*   **參數**:
    *   `commands` (List[Command]): 一個指令物件的列表，每個物件定義一個操作。指令按順序執行。
        *   **Command 物件結構**:
            *   `action` (str): 必要。操作類型。可選值包括: 
                *   `"click"`, `"double_click"`, `"right_click"`, `"middle_click"` (滑鼠點擊)
                *   `"type"` (輸入文字)
                *   `"press"` (按下單個按鍵，如 "enter", "f1", "delete")
                *   `"hotkey"` (按下組合鍵，如 ["ctrl", "c"] 或 "ctrl+c")
                *   `"move_to"` (移動滑鼠到指定座標)
                *   `"drag_to"` (拖曳滑鼠到指定座標)
                *   `"scroll"` (滾動滑鼠滾輪)
                *   `"wait"` (等待指定秒數)
            *   `x` (int, 可選): 目標 X 座標。用於 `click`, `double_click`, `right_click`, `middle_click`, `move_to`, `drag_to`。
            *   `y` (int, 可選): 目標 Y 座標。用法同 `x`。
            *   `text` (str, 可選): 要輸入的文字。用於 `type`。
            *   `keys` (str or List[str], 可選): 要按下的鍵。單個鍵 (如 "enter") 或鍵列表 (如 ["ctrl", "alt", "delete"])。用於 `press`, `hotkey`。
            *   `duration` (float, 可選, 預設 0.2): 滑鼠移動或拖曳的持續時間 (秒)。用於 `click` (如果指定了 x,y), `double_click` (如果指定了 x,y), `right_click` (如果指定了 x,y), `middle_click` (如果指定了 x,y), `move_to`, `drag_to`。
            *   `button` (str, 可選, 預設 "left"): 滑鼠按鈕。可選 "left", "middle", "right"。用於 `click`, `double_click`, `right_click`, `middle_click`, `drag_to`。
            *   `clicks` (int, 可選, 預設 1): 點擊次數。用於 `click`。
            *   `scroll_amount` (int, 可選): 滾動的單位數。正數向上滾動，負數向下滾動。用於 `scroll`。
            *   `wait_time` (float, 可選, 預設 1.0): 等待的秒數。用於 `wait`。
            *   `comment` (str, 可選): 對此指令的註解，方便閱讀，不影響執行。
*   **返回** (一個包含以下欄位的物件/字典):
    *   `status` (str): "success" 或 "error"。
    *   `message` (str): 執行結果的訊息。如果出錯，包含錯誤詳情。
    *   `last_executed_command_index` (int, 可選): 如果執行出錯，指示是在哪個指令 (列表中的索引) 上發生了錯誤。
*   **範例呼叫**:
    ```python
    command_sequence = [
        {"action": "move_to", "x": 100, "y": 200, "duration": 0.5, "comment": "移動到記事本視窗"},
        {"action": "click"},
        {"action": "type", "text": "Hello, automated world!", "comment": "輸入文字"},
        {"action": "press", "keys": "enter"},
        {"action": "wait", "wait_time": 1.5}
    ]
    client.tools.control_input(commands=command_sequence)
    # 預期返回類似: {"status": "success", "message": "All commands executed successfully."}
    ```

## GUI 自動化進階工作流程原則

這個原則概述了如何組合使用多個工具來完成一個更複雜的任務，例如：自動定位網頁上的特定元素（如搜尋框或按鈕）、與其互動，並驗證操作的結果。這種方法強調迭代和驗證，以提高複雜 GUI 自動化任務的準確性和可靠性。

**流程概述 (由 AI 助手內部執行，遵循 `mcp-instruction.md` 中的詳細定義)：**

1.  **初始狀態捕獲 (`capture_screen`)**:
    *   獲取當前完整螢幕的截圖及其尺寸，作為後續分析的基準。

2.  **目標元素識別與迭代驗證 (`generate_text_from_google` 和 `get_subarea_description`)**:
    *   **初步全螢幕描述**: 使用 `generate_text_from_google` 分析完整螢幕截圖，獲取目標元素的文字描述和大致相對位置。
    *   **AI 估計初始探索邊界 (`exploratory_bounds`)**: AI 根據全螢幕描述自主估計一個可能包含目標元素的探索區域。
    *   **AI 迭代探索與定位 (`get_subarea_description`)**: AI 使用 `get_subarea_description` 針對 `exploratory_bounds` 進行查詢，逐步縮小範圍，直到目標被定位在一個合理的區域內。提示 AI 時，不應請求精確座標，而是詢問目標元素是否可見及其在子圖片中的相對位置。
    *   **AI 定義和確認焦點邊界 (`focused_bounds`)**: AI 根據先前步驟估計更緊密的 `focused_bounds`，並使用 `get_subarea_description` 進行多次驗證和提純，確保目標元素清晰可見、完整包含且盡可能排除無關元素。
    *   **AI 獲取最終座標**: 經過驗證的 `focused_bounds` 即為目標元素的最終全局座標。

3.  **計算互動點並執行操作 (`control_input`)**:
    *   根據最終的 `focused_bounds` 計算精確的互動點（預設為中心點，可根據 `get_subarea_description` 的內部相對位置描述進行調整）。
    *   使用 `control_input` 執行操作（如點擊、輸入）。

4.  **操作後狀態驗證 (關鍵的迭代步驟)**:
    *   **重新捕獲螢幕 (`capture_screen`)**: 獲取操作後的新 UI 狀態。
    *   **驗證變更 (`get_subarea_description` 或 `generate_text_from_google`)**: 針對先前互動的區域或相關影響區域，驗證 UI 是否如預期般發生了變化。

5.  **處理驗證結果 (成功/失敗)**:
    *   **成功**: 繼續下一個操作。
    *   **失敗**: 記錄原因，返回步驟 2 重新定位元素或調整策略。**核心原則：在未成功驗證前一個關鍵操作時，不應盲目繼續下一個操作。**

6.  **繼續後續操作並持續驗證**:
    *   對於每個關鍵的後續 GUI 操作，都應緊隨一個驗證迴圈。

7.  **最終結果分析**:
    *   完成所有互動後，捕獲最終螢幕狀態，使用 `generate_text_from_google` 或 `get_subarea_description` 分析是否達成了整體任務目標。

這個迭代定位和持續驗證的方法，雖然步驟更繁瑣，但能顯著提高複雜 GUI 自動化任務的準確性和可靠性。

## 注意事項

*   確保已在環境變數中設定 `genaikey` (注意是小寫的 "genaikey") 以便 `generate_text_from_google` 和 `get_subarea_description` 工具能夠正常運作。如果未設定，工具在初始化時會引發錯誤。
*   `capture_screen` 工具會在指定的 `current_working_dir` 下創建一個 `tmp` 資料夾來存放截圖。
*   `get_subarea_description` 工具會在 `current_working_dir/tmp/subareas` 下產生暫存的裁剪圖片檔案，並在完成後嘗試刪除它們。
*   **座標系統與 `bounds` 參數使用警告 (適用於 `get_subarea_description` 工具)**:
    *   當使用 `get_subarea_description` 並提供 `bounds_list` 中的邊界來指定子區域時，傳遞給底層 AI 模型進行分析的是**已被裁剪的子圖片**。該 AI 模型對這個子圖片如何從原始大圖中裁剪出來、原始大圖的尺寸、以及 `bounds` 參數中的具體座標值是**完全無知**的。
    *   因此，在這種情況下，您的 `prompt` **絕對不能**包含或引用 `bounds` 參數中的 `x, y, width, height` 值來描述該子圖片本身（例如，避免說「分析這個位于 x,y，寬高為 w,h 的子圖片」）。這樣做會嚴重誤導 AI，因為這些座標對只看到裁剪後圖像的 AI 模型沒有任何意義。
    *   **正確的提問方式**是：當 `bounds` 被用來傳遞子圖片時，`prompt` 應僅基於該子圖片本身的視覺內容進行提問，例如：「在這張提供的圖片中...」或「請提供目標元素相對於這張圖片左上角的座標...」。
    *   AI 助手 (客戶端) 在呼叫此工具時，負責根據 `mcp-instruction.md` 中的原則處理座標轉換。工具本身返回的描述是針對裁剪後的子圖片的。
*   **安全警告**: `control_input` 工具可以直接控制您的滑鼠和鍵盤。請謹慎使用，並確保在安全的環境下測試。建議在執行包含此工具的自動化腳本時有人監督。
