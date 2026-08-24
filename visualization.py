class TerminalColors:
    """Maps zone color names to ANSI terminal escape codes."""

    CODES = {
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "gray": "\033[90m",
        "black": "\033[30m",
        "darkred": "\033[31m",
        "crimson": "\033[38;5;160m",
        "orange": "\033[38;5;208m",
        "brown": "\033[38;5;94m",
        "gold": "\033[38;5;220m",
        "lime": "\033[92m",
        "green": "\033[32m",
        "cyan": "\033[36m",
        "purple": "\033[35m",
        "violet": "\033[38;5;141m",
        "magenta": "\033[95m",
        "maroon": "\033[38;5;52m",
    }
    RESET = "\033[0m"

    def colorize(self, text: str, color: str | None) -> str:
        """Wrap text in the ANSI code for the given color, if known."""
        code = self.CODES.get(color or "", "")
        if code == "":
            return text
        return f"{code}{text}{self.RESET}"
