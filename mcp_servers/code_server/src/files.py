import os
import sys
from .audit import audit_path_access

def _safe_log(msg):
    try:
        print(msg, file=sys.stderr, flush=True)
    except UnicodeEncodeError:
        try:
            encoding = sys.stderr.encoding or 'utf-8'
            encoded = msg.encode(encoding, errors='replace')
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr.buffer.write(encoded + b'\n')
                sys.stderr.buffer.flush()
            else:
                print(encoded.decode(encoding), file=sys.stderr, flush=True)
        except Exception:
            pass

def read_file_content(path: str, log_func=None) -> str:
    """Reads file content."""
    is_safe, message = audit_path_access(path)
    if not is_safe:
        return message
        
    try:
        # Use utf-8-sig to handle optional BOM (e.g. from .ps1 files)
        with open(path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            
        # Log read operation
        if log_func:
            preview_lines = content.splitlines()[:20]
            preview = "\n".join(preview_lines)
            if len(content.splitlines()) > 20:
                 preview += "\n... (remaining content truncated)"
            
            border = "=" * 60
            msg = f"{border}\nReading file: {path}\n{'-' * 60}\n{preview}\n{border}\n"
            log_func(msg)
        else:
            # Fallback to stderr if no log_func provided
            border = "=" * 60
            _safe_log(border)
            _safe_log(f"Reading file: {path}")
            _safe_log("-" * 60)
            
            preview_lines = content.splitlines()[:20]
            preview = "\n".join(preview_lines)
            if len(content.splitlines()) > 20:
                 preview += "\n... (remaining content truncated)"
            _safe_log(preview)
            
            _safe_log(border)
            _safe_log("")

        return content
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"

def write_file_content(path: str, content: str, log_func=None) -> str:
    """Writes file content, automatically creating the directory if it does not exist."""
    is_safe, message = audit_path_access(path)
    if not is_safe:
        return message

    try:
        abs_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        # Windows PowerShell Script Encoding Fix:
        # PowerShell 5.1 interprets UTF-8 files without BOM as ANSI (GBK).
        # We explicitly add BOM for .ps1 files to ensure they run correctly.
        encoding = 'utf-8-sig' if abs_path.lower().endswith('.ps1') else 'utf-8'
        
        with open(abs_path, 'w', encoding=encoding) as f:
            f.write(content)
            
        # Log write operation
        if log_func:
            border = "=" * 60
            msg = f"{border}\nWriting file: {abs_path}\n{'-' * 60}\n{content}\n{border}\n"
            log_func(msg)
        else:
            border = "=" * 60
            _safe_log(border)
            _safe_log(f"Writing file: {abs_path}")
            _safe_log("-" * 60)
            _safe_log(content)
            _safe_log(border)
            _safe_log("")

        return f"Successfully wrote to {abs_path}"
    except Exception as e:
        return f"Error writing to file {path}: {str(e)}"

def list_directory(path: str = ".", log_func=None) -> str:
    """Lists directory contents."""
    is_safe, message = audit_path_access(path)
    if not is_safe:
        return message

    try:
        items = os.listdir(path)
        result = "\n".join(items) if items else "Directory is empty."
        
        # Log list operation
        if log_func:
            border = "=" * 60
            msg = f"{border}\nListing directory: {path}\n{'-' * 60}\n{result}\n{border}\n"
            log_func(msg)
        else:
            border = "=" * 60
            _safe_log(border)
            _safe_log(f"Listing directory: {path}")
            _safe_log("-" * 60)
            _safe_log(result)
            _safe_log(border)
            _safe_log("")

        return result
    except Exception as e:
        return f"Error listing directory {path}: {str(e)}"
