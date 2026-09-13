from enum import Enum
from typing import Optional


class Color(Enum):
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


def colorize(text: str, color: Color, bold: bool = False) -> str:
    """
    Colorize text with ANSI codes.

    Args:
        text: Text to colorize
        color: Color enum value
        bold: Make text bold

    Returns:
        Colorized text string
    """
    prefix = Color.BOLD.value if bold else ""
    return f"{prefix}{color.value}{text}{Color.RESET.value}"


def success(text: str, bold: bool = False) -> str:
    """Green text for success messages."""
    return colorize(text, Color.GREEN, bold)


def error(text: str, bold: bool = False) -> str:
    """Red text for error messages."""
    return colorize(text, Color.RED, bold)


def warning(text: str, bold: bool = False) -> str:
    """Yellow text for warning messages."""
    return colorize(text, Color.YELLOW, bold)


def info(text: str, bold: bool = False) -> str:
    """Cyan text for info messages."""
    return colorize(text, Color.CYAN, bold)


def command(text: str) -> str:
    """Blue text for commands."""
    return colorize(text, Color.BLUE, bold=True)


def dim(text: str) -> str:
    """Dimmed text for secondary info."""
    return f"{Color.DIM.value}{text}{Color.RESET.value}"
