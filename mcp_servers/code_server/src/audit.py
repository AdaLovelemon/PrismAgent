import re
import os
from typing import Tuple

# Definition of dangerous keywords
DANGEROUS_COMMANDS = [
    r"\brm\b\s+-[rf]{1,2}",        # rm -rf
    r"\bdel\b\s+/s",               # del /s (Windows)
    r"\bformat\b\s+[a-zA-Z]:",     # format C:
    r"\bmkfs\b",                   # disk formatting
    r"\bdd\b\s+if=",               # disk imaging
    r"\bshutdown\b",               # system shutdown
    r"\breboot\b",                 # system reboot
    r"\bchmod\b\s+777",            # unsafe permissions
    r"\bchown\b",                  # ownership changes
    r"\bsudo\b",                   # elevation
]

DANGEROUS_PYTHON_PATTERNS = [
    r"import\s+os",               # os module access
    r"import\s+subprocess",       # subprocess access
    r"import\s+shutil",           # high-level file ops
    r"eval\(",                     # arbitrary code evaluation
    r"exec\(",                     # arbitrary code execution
    r"os\.remove",                 # file deletion
    r"os\.rmdir",                  # directory deletion
    r"shutil\.rmtree",             # recursive deletion
    r"__import__",                 # dynamic imports
    r"open\(\s*['\"]/etc/",        # accessing system configs
    r"open\(\s*['\"]C:\\Windows",  # accessing windows system dirs
]

CLEAN_CODE_MESSAGE = "Audit Passed."

def audit_command(command: str) -> Tuple[bool, str]:
    """Audit terminal commands."""
    for pattern in DANGEROUS_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"Security Breach: Command '{command}' contains forbidden patterns ({pattern})."
    return True, CLEAN_CODE_MESSAGE

def audit_python_code(code: str) -> Tuple[bool, str]:
    """Audit Python code."""
    for pattern in DANGEROUS_PYTHON_PATTERNS:
        if re.search(pattern, code):
            return False, f"Security Breach: Python code contains suspicious patterns ({pattern})."
    return True, CLEAN_CODE_MESSAGE

def audit_path_access(path: str) -> Tuple[bool, str]:
    """Audit the security of path access."""
    abs_path = os.path.abspath(path).lower()
    
    # Restrict access to highly sensitive system paths (Windows/Linux)
    forbidden_roots = [
        "c:\\windows",
        "c:\\users",
        "/etc",
        "/var",
        "/root",
        "/bin",
        "/sbin"
    ]
    
    for root in forbidden_roots:
        if abs_path.startswith(root):
             return False, f"Security Breach: Access to system directory '{root}' is restricted."
             
    return True, CLEAN_CODE_MESSAGE
