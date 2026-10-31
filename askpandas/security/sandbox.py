import ast
import builtins
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from ..visualization.charts import (
    create_bar_chart,
    create_box_plot,
    create_correlation_heatmap,
    create_histogram,
    create_line_chart,
    create_scatter_plot,
    save_plot,
)


class SafeExecutor:
    def __init__(self) -> None:
        """Initialize the safe code execution environment."""
        # Allowed modules and functions
        self.allowed_modules = {
            "pandas": pd,
            "numpy": np,
            "matplotlib.pyplot": plt,
            "seaborn": sns,
            "pd": pd,
            "np": np,
            "plt": plt,
            "sns": sns,
            "save_plot": save_plot,
            # Chart helpers advertised in the engine prompts
            "create_bar_chart": create_bar_chart,
            "create_line_chart": create_line_chart,
            "create_scatter_plot": create_scatter_plot,
            "create_histogram": create_histogram,
            "create_correlation_heatmap": create_correlation_heatmap,
            "create_box_plot": create_box_plot,
        }
        # Error message of the most recent execute() call, or None if it succeeded
        self.last_error: str | None = None

        # Allowed built-in functions
        self.allowed_builtins = {
            "len",
            "range",
            "enumerate",
            "zip",
            "list",
            "dict",
            "tuple",
            "set",
            "str",
            "int",
            "float",
            "bool",
            "sum",
            "max",
            "min",
            "sorted",
            "abs",
            "round",
            "print",
            "type",
            "isinstance",
            "any",
            "all",
            "filter",
            "map",
            "reversed",
            "slice",
            "divmod",
            "pow",
            "ord",
            "chr",
            "bin",
            "hex",
            "oct",
            "format",
            "repr",
            "ascii",
            "hash",
            "hasattr",
            "callable",
            "issubclass",
            "next",
            "iter",
        }

        # Dangerous operations that are explicitly blocked
        self.blocked_operations = {
            "import",
            "from",
            "del",
            "global",
            "nonlocal",
            "assert",
            "raise",
            "yield",
            "lambda",
            "class",
            "def",
        }

    def execute(self, code: str, local_vars: dict[str, Any]) -> str:
        """Validate and run ``code``; return everything it printed.

        Errors are not raised: the returned string describes them, and
        :attr:`last_error` holds the message (``None`` after a successful run).
        Variables the code creates are written back into ``local_vars``.
        """
        self.last_error = None
        # Parse and validate AST
        try:
            tree = ast.parse(code)
            self._validate_ast(tree)
        except SyntaxError as e:
            self.last_error = f"Syntax error in generated code: {e}"
            return self.last_error
        except ValueError as e:
            self.last_error = f"Code validation failed: {e}"
            return self.last_error

        # Prepare execution environment. A single namespace is used for globals and
        # locals so that comprehensions/generator expressions can see df0, df1, ...
        # (with separate dicts they raise NameError on Python < 3.12).
        namespace = {
            "__builtins__": {
                name: getattr(builtins, name)
                for name in self.allowed_builtins
                if hasattr(builtins, name)
            },
            **self.allowed_modules,
            **local_vars,
        }

        # Capture output
        output_buffer = StringIO()
        error_buffer = StringIO()

        try:
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                exec(code, namespace)

            output = output_buffer.getvalue()
            errors = error_buffer.getvalue()
            # Expose variables created by the code to the caller
            for key, value in namespace.items():
                if key != "__builtins__" and key not in self.allowed_modules:
                    local_vars[key] = value

            if output and errors:
                return f"{output}\n[stderr]\n{errors}"
            return output or errors or "Code executed successfully (no output)"
        except Exception as e:
            self.last_error = f"Execution failed: {e}"
            return self.last_error

    def _validate_ast(self, tree: ast.AST) -> None:
        """Validate AST for security."""
        dangerous_nodes = [
            ast.Import,
            ast.ImportFrom,
            ast.AsyncFunctionDef,
            ast.ClassDef,
        ]

        for node in ast.walk(tree):
            # Check for dangerous node types
            if any(isinstance(node, dangerous) for dangerous in dangerous_nodes):
                raise ValueError(f"Dangerous operation not allowed: {type(node).__name__}")

            # Block dunder attribute access (e.g. ().__class__.__subclasses__()),
            # the classic way to escape restricted-builtins sandboxes
            if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                raise ValueError(f"Access to dunder attribute '{node.attr}' is not allowed")
            if isinstance(node, ast.Name) and node.id.startswith("__"):
                raise ValueError(f"Access to dunder name '{node.id}' is not allowed")

            # Check function definitions
            if isinstance(node, ast.FunctionDef):
                raise ValueError("Function definitions are not allowed in safe mode")

            # Check function calls
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                func_name = node.func.id
                if (
                    func_name not in self.allowed_builtins
                    and func_name not in self.allowed_modules
                    and func_name not in self.blocked_operations
                ):
                    raise ValueError(f"Function call not allowed: {func_name}")

            # Check for file operations
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in ("open", "file")
            ):
                raise ValueError("File operations are not allowed in safe mode")

            # Check for network operations
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in ("requests", "urllib", "socket")
            ):
                raise ValueError("Network operations are not allowed in safe mode")

    def get_execution_stats(self) -> dict[str, Any]:
        """Get statistics about the execution environment."""
        return {
            "allowed_modules": list(self.allowed_modules.keys()),
            "allowed_builtins": list(self.allowed_builtins),
            "blocked_operations": list(self.blocked_operations),
            "sandbox_mode": "strict",
        }
