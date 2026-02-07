import platform
import os
from colorama import init, Fore, Back, Style

# Set autoreset to True to avoid manual reset
init(autoreset=True)

def print_colored(*values, color="RESET", background="RESET", sep=" ", end="\n", file=None, flush=False):
    # Assert valid color choices
    if not color:
        color = "RESET"
    if not background:
        background = "RESET"

    # Use getattr to dynamically get the color attributes from colorama
    print(getattr(Fore, color.upper(), Fore.RESET) + getattr(Back, background.upper(), Back.RESET) + sep.join(map(str, values)),
          sep=sep, end=end, file=file, flush=flush)


def log_in_markdown(text, md_path, color="RESET", background="RESET"):
    # For markdown, we can use HTML tags to set color and background
    color_style = f"color:{color.lower()};" if color != "RESET" else ""
    background_style = f"background-color:{background.lower()};" if background != "RESET" else ""
    style = color_style + background_style
    text_md = f"<span style='{style}'>{text}</span>"
    with open(md_path, 'a', encoding='utf-8') as f:
        f.write(f"{text_md}<br>\n")


def print_system(text, md_path=None):
    # Predefine color collocation
    color, background = "CYAN", "RESET"

    # Preprocess text
    if "\n" in text:
        text_to_print = f"[System]\n" + "-" * 70 + f"\n{text}\n" + "-" * 70 + "\n"
    else:
        text_to_print = f"[System] {text}\n"
    print_colored(text_to_print, color=color, background=background)
    if md_path:
        log_in_markdown(text_to_print, md_path, color=color, background=background)


def print_warning(text, warn=None, md_path=None):
    # Predefine color collocation
    color, background = "YELLOW", "RESET"

    # Preprocess text
    if not warn:
        warn = "Warning"

    if "\n" in text:
        text_to_print = f"[{warn}]\n" + "-" * 70 + f"\n{text}\n" + "-" * 70 + "\n"
    else:
        text_to_print = f"[{warn}] {text}\n"
    print_colored(text_to_print, color=color, background=background)
    if md_path:
        log_in_markdown(text_to_print, md_path, color=color, background=background)


def print_error(text, error_name="", md_path=None):
    # Predefine color collocation
    color, background = "RED", "RESET"

    # Preprocess text
    if "\n" in text:
        text_to_print = f"[Error]{error_name}\n" + "-" * 70 + f"\n{text}\n" + "-" * 70 + "\n"
    else:
        text_to_print = f"[Error]{error_name} {text}\n"
    print_colored(text_to_print, color=color, background=background)
    if md_path:
        log_in_markdown(text_to_print, md_path, color=color, background=background)


def print_agent(text, md_path=None):
    # Predefine color collocation
    color, background = "RESET", "RESET"

    # Preprocess text
    if "\n" in text:
        text_to_print = f"[Agent]\n" + "-" * 70 + f"\n{text}\n" + "-" * 70 + "\n"
    else:
        text_to_print = f"[Agent] {text}\n"
    print_colored(text_to_print, color=color, background=background)
    if md_path:
        log_in_markdown(text_to_print, md_path, color=color, background=background)


def print_tokentracker(text, report_name, md_path=None):
    # Predefine color collocation
    color, background = "GREEN", "RESET"

    # Preprocess text
    if "\n" in text:
        text_to_print = f"[TokenTracker]({report_name})\n" + "-" * 70 + f"\n{text}\n" + "-" * 70 + "\n"
    else:
        text_to_print = f"[TokenTracker]({report_name}) {text}\n"
    print_colored(text_to_print, color=color, background=background)
    if md_path:
        log_in_markdown(text_to_print, md_path, color=color, background=background)


def print_user(text, md_path=None):
    # Predefine color collocation
    color, background = "BLUE", "RESET"

    # Preprocess text
    if "\n" in text:
        text_to_print = f"[User]\n" + "-" * 70 + f"\n{text}\n" + "-" * 70 + "\n"
    else:
        text_to_print = f"[User] {text}\n"
    print_colored(text_to_print, color=color, background=background)
    if md_path:
        log_in_markdown(text_to_print, md_path, color=color, background=background)


def print_mcptool(text, tool_name, md_path=None):
    # Predefine color collocation
    color, background = "MAGENTA", "RESET"

    # Preprocess text
    if "\n" in text:
        text_to_print = f"[MCP Tool]({tool_name})\n" + "-" * 70 + f"\n{text}\n" + "-" * 70 + "\n"
    else:
        text_to_print = f"[MCP Tool]({tool_name}) {text}\n"
    print_colored(text_to_print, color=color, background=background)
    if md_path:
        log_in_markdown(text_to_print, md_path, color=color, background=background)


def print_terminal(project_dir: str, command, result):
    print_colored(f"[MCP Tool](run_terminal_command)" + "\n" + "-"*70, color="MAGENTA", background="RESET")
    background = "RESET"

    # Powershell style
    if platform.system() == "Windows":
        print(Fore.CYAN + getattr(Back, background, "RESET") + f"PS {os.path.abspath(project_dir)}> ", end="")
        print_colored(f"{command}", color="YELLOW", background=background)
        print_colored(f"{result}", color="RESET", background=background)
    
    # Bash style
    else:
        # Convert Windows path to bash style (e.g., C:\Users\user\proj -> /c/Users/user/proj)
        abs_path = os.path.abspath(project_dir).replace("\\", "/")
        if len(abs_path) > 2 and abs_path[1] == ":" and abs_path[2] == "/":
            drive_letter = abs_path[0].lower()
            abs_path = f"/{drive_letter}{abs_path[2:]}"
        print(Fore.GREEN + getattr(Back, background, "RESET") + f"agent@{platform.node()}" + Fore.RESET + getattr(Back, background, "RESET") + ":", end="")
        print(Fore.BLUE + getattr(Back, background, "RESET") + abs_path + Fore.RESET + getattr(Back, background, "RESET") + "$ ", end="")
        print_colored(f"{command}", color="RESET", background=background)
        print_colored(f"{result}", color="RESET", background=background)
    
    # Print a separator line after terminal output
    print_colored("-"*70 + "\n", color="MAGENTA", background="RESET")

def print_security_audit(text, md_path=None):
    # Predefine color collocation
    color, background = "YELLOW", "RESET"

    # Preprocess text
    text_to_print = "!"*70 + f"\n[Security Audit] {text}\n" + "!"*70 + "\n"
    print_colored(text_to_print, color=color, background=background)
    if md_path:
        log_in_markdown(text_to_print, md_path, color=color, background=background)


def input_user(prompt_text, color="BLUE", background="RESET"):
    # Print prompt in specified color
    prompt_colored = getattr(Fore, color.upper(), Fore.RESET) + getattr(Back, background.upper(), Back.RESET) + prompt_text
    return input(prompt_colored)
