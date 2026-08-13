class TerminalColors:
    """Maps zone color names to ANSI terminal escape codes."""

    CODES = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "gray": "\033[90m",
    }
    RESET = "\033[0m"

    def colorize(self, text: str, color: str | None) -> str:
        """Wrap text in the ANSI code for the given color, if known."""
        code = self.CODES.get(color or "", "")
        if code == "":
            return text
        return f"{code}{text}{self.RESET}"
