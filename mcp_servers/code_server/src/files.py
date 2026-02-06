import os
from .audit import audit_path_access

def read_file_content(path: str) -> str:
    """Reads file content."""
    is_safe, message = audit_path_access(path)
    if not is_safe:
        return message
        
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"

def write_file_content(path: str, content: str) -> str:
    """Writes file content, automatically creating the directory if it does not exist."""
    is_safe, message = audit_path_access(path)
    if not is_safe:
        return message

    try:
        abs_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {abs_path}"
    except Exception as e:
        return f"Error writing to file {path}: {str(e)}"

def list_directory(path: str = ".") -> str:
    """Lists directory contents."""
    is_safe, message = audit_path_access(path)
    if not is_safe:
        return message

    try:
        items = os.listdir(path)
        return "\n".join(items) if items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory {path}: {str(e)}"
