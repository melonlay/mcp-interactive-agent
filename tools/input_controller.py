import pyautogui
import time
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal

# --- PyAutoGUI 設定 (可以根據需要調整) ---
pyautogui.FAILSAFE = True # 滑鼠移到左上角觸發 FailSafeException
pyautogui.PAUSE = 0.1     # 每個 pyautogui 函數呼叫後的預設暫停時間

# --- Pydantic 模型定義指令結構 ---
class Command(BaseModel):
    action: Literal[
        "click", "double_click", "right_click", "middle_click", 
        "type", "press", "hotkey",
        "move_to", "drag_to", 
        "scroll", 
        "wait"
    ]
    x: Optional[int] = None
    y: Optional[int] = None
    text: Optional[str] = None
    keys: Optional[Union[str, List[str]]] = None # 單個鍵或多個鍵列表
    duration: Optional[float] = Field(default=0.2, description="Duration in seconds for mouse movements/drags")
    button: Optional[Literal["left", "middle", "right"]] = "left"
    clicks: Optional[int] = 1
    scroll_amount: Optional[int] = None # 正數向上，負數向下
    wait_time: Optional[float] = Field(default=1.0, description="Duration in seconds for wait action")
    comment: Optional[str] = None # 用於使用者註釋，不影響執行

class InputControlResult(BaseModel):
    status: Literal["success", "error"]
    message: str
    last_executed_command_index: Optional[int] = None

async def control_input(commands: List[Command]) -> InputControlResult:
    """
    Executes a series of keyboard and mouse control commands.

    Args:
        commands: A list of command objects to execute in sequence.

    Returns:
        An InputControlResult object indicating success or failure.
    """
    for i, cmd in enumerate(commands):
        try:
            if cmd.comment:
                print(f"Executing command {i} ({cmd.action}): {cmd.comment}")
            else:
                print(f"Executing command {i}: {cmd.action}")

            if cmd.action == "click":
                if cmd.x is not None and cmd.y is not None:
                    pyautogui.click(x=cmd.x, y=cmd.y, clicks=cmd.clicks, button=cmd.button, duration=cmd.duration)
                else:
                    pyautogui.click(clicks=cmd.clicks, button=cmd.button, duration=cmd.duration) # 點擊目前位置
            elif cmd.action == "double_click":
                 if cmd.x is not None and cmd.y is not None:
                    pyautogui.doubleClick(x=cmd.x, y=cmd.y, button=cmd.button, duration=cmd.duration)
                 else:
                    pyautogui.doubleClick(button=cmd.button, duration=cmd.duration)
            elif cmd.action == "right_click":
                if cmd.x is not None and cmd.y is not None:
                    pyautogui.rightClick(x=cmd.x, y=cmd.y, duration=cmd.duration)
                else:
                    pyautogui.rightClick(duration=cmd.duration)
            elif cmd.action == "middle_click":
                if cmd.x is not None and cmd.y is not None:
                    pyautogui.middleClick(x=cmd.x, y=cmd.y, duration=cmd.duration)
                else:
                    pyautogui.middleClick(duration=cmd.duration)
            elif cmd.action == "type":
                if cmd.text is not None:
                    pyautogui.typewrite(cmd.text, interval=0.01) # interval 可調整打字速度
                else:
                    return InputControlResult(status="error", message=f"Command {i} ('type') missing 'text' parameter.", last_executed_command_index=i)
            elif cmd.action == "press":
                if cmd.keys is not None:
                    if isinstance(cmd.keys, list):
                        for key in cmd.keys: # pyautogui.press 不直接支援列表，需逐個按
                            pyautogui.press(key)
                    else:
                        pyautogui.press(cmd.keys)
                else:
                    return InputControlResult(status="error", message=f"Command {i} ('press') missing 'keys' parameter.", last_executed_command_index=i)
            elif cmd.action == "hotkey":
                if cmd.keys is not None and isinstance(cmd.keys, list):
                    pyautogui.hotkey(*cmd.keys) # hotkey 接受多個參數
                elif cmd.keys is not None and isinstance(cmd.keys, str):
                     pyautogui.hotkey(cmd.keys) # 也可接受單個字串代表的組合鍵，如 'ctrl+c'
                else:
                    return InputControlResult(status="error", message=f"Command {i} ('hotkey') missing 'keys' parameter or keys not a list/str.", last_executed_command_index=i)
            elif cmd.action == "move_to":
                if cmd.x is not None and cmd.y is not None:
                    pyautogui.moveTo(cmd.x, cmd.y, duration=cmd.duration)
                else:
                    return InputControlResult(status="error", message=f"Command {i} ('move_to') missing 'x' or 'y' parameters.", last_executed_command_index=i)
            elif cmd.action == "drag_to":
                if cmd.x is not None and cmd.y is not None:
                    pyautogui.dragTo(cmd.x, cmd.y, duration=cmd.duration, button=cmd.button)
                else:
                    return InputControlResult(status="error", message=f"Command {i} ('drag_to') missing 'x' or 'y' parameters.", last_executed_command_index=i)
            elif cmd.action == "scroll":
                if cmd.scroll_amount is not None:
                    pyautogui.scroll(cmd.scroll_amount)
                else:
                    return InputControlResult(status="error", message=f"Command {i} ('scroll') missing 'scroll_amount' parameter.", last_executed_command_index=i)
            elif cmd.action == "wait":
                time.sleep(cmd.wait_time)
            else:
                return InputControlResult(status="error", message=f"Unknown action type '{cmd.action}' at command {i}.", last_executed_command_index=i)

        except pyautogui.FailSafeException:
            return InputControlResult(status="error", message="FailSafeException: Mouse moved to a corner (likely top-left). Operation aborted.", last_executed_command_index=i)
        except Exception as e:
            return InputControlResult(status="error", message=f"Error executing command {i} ({cmd.action}): {str(e)}", last_executed_command_index=i)
        
    return InputControlResult(status="success", message="All commands executed successfully.")

# 範例 (供本地測試，不會被 MCP 直接呼叫):
async def main_test():
    sample_commands = [
        Command(action="move_to", x=100, y=100, duration=0.5, comment="Move to top-left area"),
        Command(action="click", comment="Click there"),
        Command(action="type", text="Hello, PyAutoGUI!", comment="Type some text"),
        Command(action="press", keys="enter", comment="Press Enter"),
        Command(action="wait", wait_time=2, comment="Wait for 2 seconds"),
        Command(action="move_to", x=500, y=500, duration=0.5),
        Command(action="drag_to", x=700, y=700, duration=1, button="left", comment="Drag something"),
        Command(action="scroll", scroll_amount=-100, comment="Scroll down"), # 10 clicks down
        Command(action="hotkey", keys=["ctrl", "a"])
    ]
    result = await control_input(commands=sample_commands)
    print(f"Test Result: Status: {result.status}, Message: {result.message}")

if __name__ == "__main__":
    # 注意：直接執行此檔案會嘗試控制您的滑鼠和鍵盤！
    # import asyncio
    # asyncio.run(main_test())
    print("This script defines the 'control_input' tool for an MCP server.")
    print("To test locally (BE CAREFUL), uncomment the asyncio.run(main_test()) lines.") 