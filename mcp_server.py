import base64
from mcp.server.fastmcp import FastMCP, Image
from tools.say_greeting import say_greeting
from tools.capture_screen import capture_screen
from tools.google_genai import generate_text_from_google
from tools.subarea_tool import get_subarea_description
from tools.input_controller import control_input

# Initialize FastMCP server
mcp = FastMCP("interactive-gui-mcp")

mcp.tool()(say_greeting)
mcp.tool()(capture_screen)
mcp.tool()(generate_text_from_google)
mcp.tool()(get_subarea_description)
mcp.tool()(control_input)

if __name__ == "__main__":
    mcp.run(transport='stdio')