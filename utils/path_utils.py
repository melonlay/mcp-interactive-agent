import urllib.parse
import platform
from pathlib import Path
import re

def _normalize_path(path_str: str) -> Path:
    """Converts a potentially mixed-format path string to a standardized Path object."""
    unquoted_path = urllib.parse.unquote(path_str)

    if platform.system() == "Windows":
        # If starts with /D: or /d: (or /c: etc.), remove the leading slash
        # e.g., "/d:/foo/bar" becomes "d:/foo/bar"
        if re.match(r"^/[a-zA-Z]:", unquoted_path):
            unquoted_path = unquoted_path[1:]
        
        # If it's like "d:foo" (missing backslash after colon), add it
        # e.g., "d:foo\\bar" becomes "d:\\foo\\bar"
        if re.match(r"^[a-zA-Z]:[^\\\\/]", unquoted_path): # Match if no slash or backslash after colon
            unquoted_path = unquoted_path[:2] + "\\\\" + unquoted_path[2:]
        
    path_obj = Path(unquoted_path)
    
    try:
        # For a CWD, we don't want resolve to fail if the dir doesn't exist yet, 
        # as mkdir will create it. But we want to standardize slashes and get an absolute path.
        # absolute() is better here as resolve() might require path existence.
        abs_path = path_obj.absolute()
    except Exception:
        # Fallback if absolute() fails for some reason (highly unlikely for valid CWD format)
        abs_path = path_obj # Use as is, hoping for the best
    
    # Further ensure it's resolved to clean up '..' etc., but allow non-existence for CWDs
    # Path.resolve() without strict=True will still try to make it absolute and clean.
    try:
        resolved_path = abs_path.resolve()
    except Exception: # Fallback if resolve fails
        resolved_path = abs_path

    return resolved_path 