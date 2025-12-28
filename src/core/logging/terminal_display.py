"""
Unified Terminal Output Management System
Reference solve_agents display design, providing unified terminal visualization for all modules
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import sys
import time


class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


@dataclass
class TokenUsage:
    """Token usage statistics"""

    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class AgentInfo:
    """Agent information"""

    name: str
    status: AgentStatus = AgentStatus.PENDING
    message: str = ""
    start_time: float | None = None
    end_time: float | None = None


class TerminalDisplay:
    """
    Unified terminal display manager
    Provides visualization of workflow progress, Agent status, Token consumption, etc.
    """

    def __init__(
        self,
        module_name: str,
        agents: list[str] | None = None,
        show_tokens: bool = True,
        show_time: bool = True,
    ):
        """
        Initialize terminal display manager

        Args:
            module_name: Module name
            agents: Agent name list
            show_tokens: Whether to show token statistics
            show_time: Whether to show time information
        """
        self.module_name = module_name
        self.show_tokens = show_tokens
        self.show_time = show_time
        self.start_time = time.time()

        # Agent status tracking
        self.agents: dict[str, AgentInfo] = {}
        if agents:
            for agent in agents:
                self.agents[agent] = AgentInfo(name=agent)

        # Token statistics
        self.token_usage: dict[str, TokenUsage] = {}
        self.total_tokens = TokenUsage()

        # Log buffer
        self.log_buffer: list[str] = []
        self.max_log_lines = 10

    def _get_status_symbol(self, status: AgentStatus) -> str:
        """Get status symbol"""
        symbols = {
            AgentStatus.PENDING: "○",
            AgentStatus.RUNNING: "●",
            AgentStatus.DONE: "✓",
            AgentStatus.ERROR: "✗",
        }
        return symbols.get(status, "?")

    def _get_status_color(self, status: AgentStatus) -> str:
        """Get status color ANSI code"""
        colors = {
            AgentStatus.PENDING: "\033[90m",  # Gray
            AgentStatus.RUNNING: "\033[33m",  # Yellow
            AgentStatus.DONE: "\033[32m",  # Green
            AgentStatus.ERROR: "\033[31m",  # Red
        }
        return colors.get(status, "\033[0m")

    def _reset_color(self) -> str:
        """Reset color"""
        return "\033[0m"

    def set_agent_status(self, agent_name: str, status: str, message: str = ""):
        """
        Set Agent status

        Args:
            agent_name: Agent name
            status: Status (pending, running, done, error)
            message: Status message
        """
        status_enum = AgentStatus(status) if isinstance(status, str) else status

        if agent_name not in self.agents:
            self.agents[agent_name] = AgentInfo(name=agent_name)

        agent = self.agents[agent_name]
        old_status = agent.status
        agent.status = status_enum
        agent.message = message

        if status_enum == AgentStatus.RUNNING and agent.start_time is None:
            agent.start_time = time.time()
        elif status_enum in (AgentStatus.DONE, AgentStatus.ERROR):
            agent.end_time = time.time()

        self._refresh_display()

    def add_token_usage(self, model: str, input_tokens: int, output_tokens: int, cost: float = 0.0):
        """
        Add token usage record

        Args:
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count
            cost: Cost (USD)
        """
        if model not in self.token_usage:
            self.token_usage[model] = TokenUsage(model=model)

        usage = self.token_usage[model]
        usage.input_tokens += input_tokens
        usage.output_tokens += output_tokens
        usage.cost += cost

        # Update total
        self.total_tokens.input_tokens += input_tokens
        self.total_tokens.output_tokens += output_tokens
        self.total_tokens.cost += cost

        self._refresh_display()

    def log(self, message: str):
        """Add log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        self.log_buffer.append(log_line)

        # Maintain log buffer size
        if len(self.log_buffer) > self.max_log_lines:
            self.log_buffer = self.log_buffer[-self.max_log_lines :]

        self._refresh_display()

    def _refresh_display(self):
        """Refresh terminal display"""
        # Clear screen and move to top
        print("\033[2J\033[H", end="")

        # Title
        elapsed = time.time() - self.start_time
        print("\033[1;34m╔══════════════════════════════════════════════════════════════╗\033[0m")
        print(f"\033[1;34m║\033[0m  \033[1m{self.module_name:^56}\033[0m  \033[1;34m║\033[0m")
        if self.show_time:
            time_str = f"Running: {elapsed:.1f}s"
            print(f"\033[1;34m║\033[0m  {time_str:^56}  \033[1;34m║\033[0m")
        print("\033[1;34m╠══════════════════════════════════════════════════════════════╣\033[0m")

        # Agent status
        if self.agents:
            print(f"\033[1;34m║\033[0m  \033[1mAgent Status\033[0m{'':43}  \033[1;34m║\033[0m")
            for agent in self.agents.values():
                symbol = self._get_status_symbol(agent.status)
                color = self._get_status_color(agent.status)
                reset = self._reset_color()

                status_str = f"{color}{symbol} {agent.name}{reset}"
                if agent.message:
                    status_str += f" - {agent.message[:30]}"

                # Calculate display time
                if agent.start_time and agent.end_time:
                    duration = agent.end_time - agent.start_time
                    status_str += f" ({duration:.1f}s)"
                elif agent.start_time:
                    duration = time.time() - agent.start_time
                    status_str += f" ({duration:.1f}s...)"

                # Need to handle ANSI escape sequence length when printing
                print(f"\033[1;34m║\033[0m    {status_str:56}  \033[1;34m║\033[0m")

            print(
                "\033[1;34m╠══════════════════════════════════════════════════════════════╣\033[0m"
            )

        # Token statistics
        if self.show_tokens and self.token_usage:
            print(f"\033[1;34m║\033[0m  \033[1mToken Usage\033[0m{'':44}  \033[1;34m║\033[0m")
            for model, usage in self.token_usage.items():
                model_short = model[:20] + "..." if len(model) > 20 else model
                tokens_str = f"{model_short}: {usage.total_tokens:,} tokens"
                if usage.cost > 0:
                    tokens_str += f" (${usage.cost:.4f})"
                print(f"\033[1;34m║\033[0m    {tokens_str:54}  \033[1;34m║\033[0m")

            # Total
            total_str = f"Total: {self.total_tokens.total_tokens:,} tokens"
            if self.total_tokens.cost > 0:
                total_str += f" (${self.total_tokens.cost:.4f})"
            print(f"\033[1;34m║\033[0m    \033[1m{total_str:54}\033[0m  \033[1;34m║\033[0m")

            print(
                "\033[1;34m╠══════════════════════════════════════════════════════════════╣\033[0m"
            )

        # Logs
        if self.log_buffer:
            print(f"\033[1;34m║\033[0m  \033[1mRecent Logs\033[0m{'':44}  \033[1;34m║\033[0m")
            for log_line in self.log_buffer[-5:]:  # Only show last 5
                log_short = log_line[:52] + "..." if len(log_line) > 52 else log_line
                print(f"\033[1;34m║\033[0m    \033[90m{log_short:54}\033[0m  \033[1;34m║\033[0m")
            print(
                "\033[1;34m╠══════════════════════════════════════════════════════════════╣\033[0m"
            )

        # Bottom
        print("\033[1;34m╚══════════════════════════════════════════════════════════════╝\033[0m")

        sys.stdout.flush()

    def complete(self, message: str = "Complete"):
        """Mark task as complete"""
        elapsed = time.time() - self.start_time
        self.log(f"✓ {message} ({elapsed:.1f}s)")
        self._refresh_display()

    def error(self, message: str):
        """Mark task as error"""
        self.log(f"✗ Error: {message}")
        self._refresh_display()


class SimpleProgress:
    """
    Simple progress displayer (no screen clearing)
    Suitable for scenarios that don't need full TUI
    """

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.start_time = time.time()

    def log(self, message: str, level: str = "INFO"):
        """Output log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        elapsed = time.time() - self.start_time

        color = {
            "INFO": "\033[0m",
            "SUCCESS": "\033[32m",
            "WARNING": "\033[33m",
            "ERROR": "\033[31m",
        }.get(level, "\033[0m")

        reset = "\033[0m"
        print(f"[{timestamp}] [{self.module_name}] {color}{message}{reset} ({elapsed:.1f}s)")

    def progress(self, current: int, total: int, message: str = ""):
        """Display progress bar"""
        percentage = (current / total) * 100 if total > 0 else 0
        bar_length = 30
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)

        print(f"\r[{bar}] {percentage:5.1f}% ({current}/{total}) {message}", end="", flush=True)
        if current >= total:
            print()  # New line

    def complete(self, message: str = "Complete"):
        """Complete"""
        self.log(f"✓ {message}", "SUCCESS")

    def error(self, message: str):
        """Error"""
        self.log(f"✗ {message}", "ERROR")


# Convenience functions
def create_display(
    module_name: str, agents: list[str] | None = None, use_tui: bool = True
) -> TerminalDisplay | SimpleProgress:
    """
    Create terminal displayer

    Args:
        module_name: Module name
        agents: Agent list
        use_tui: Whether to use full TUI

    Returns:
        Displayer instance
    """
    if use_tui:
        return TerminalDisplay(module_name, agents)
    return SimpleProgress(module_name)
