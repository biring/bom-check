"""
Datatypes for coercion module.

This module provides internal data containers for recording text transformations, aggregating coercion results, and applying regex-based substitution rules.

Key Responsibilities:
	- Record before and after values for individual text transformations
	- Store original and coerced values with ordered transformation details
	- Render transformation changes as immutable report lines
	- Compile and apply regex-based substitution rules
	- Raise validation errors for invalid regular expression patterns

Example Usage:
	# Preferred usage via public package interface:
	Not applicable. This is an internal module and should be accessed via a façade when exposed.

	# Direct module usage (acceptable in unit tests or internal scripts only):
	from src.coerce import _types
	result = _types.Result(attr_name="manufacturer", original_value="Acme  Corporation", coerced_value="ACME", changes=[])

Dependencies:
	- Python version: >= 3.10
	- Standard Library: dataclasses, re, typing

Notes:
	- Intended for internal use within the coercion package
	- Regular expression patterns are compiled during initialization
	- Rendered changes are omitted when the original and coerced values are equal

License:
	- Internal Use Only
"""
__all__ = []  # Internal-only; not part of public API. Star import from this module gets nothing.

import re
from dataclasses import dataclass, field
from typing import Union, Callable, Match


@dataclass(frozen=True)
class Log:
    """
    Record a single text transformation.

    Preserves the before value, after value, and explanation for one transformation step.

    Invariants:
        - Each instance represents one atomic transformation.
        - Field values cannot be reassigned after initialization.

    Attributes:
        before (str): Input text before a rule is applied.
        after (str): Output text after a rule is applied.
        description (str): Human-readable explanation of the transformation.
    """
    # Keep the pre-transformation value so callers can audit exactly what changed.
    before: str

    # Keep the post-transformation value alongside before to make each log entry self-contained.
    after: str

    # Store the rule explanation with the values so renderers do not need to infer intent later.
    description: str


@dataclass
class Result:
    """
    Hold the outcome of one or more coercion rules.

    Stores the attribute name, original value, final coerced value, and ordered transformation log.

    Invariants:
        - changes preserves the order in which transformations were recorded.
        - original_value represents the value before coercion.
        - coerced_value represents the value after coercion.

    Attributes:
        attr_name (str): Name of the field being coerced.
        original_value (str): Original input value.
        coerced_value (str): Final coerced value.
        changes (list[Log]): Ordered list of applied transformation entries.
    """
    # Keep the attribute name with the values so rendered messages identify the affected field.
    attr_name: str = ""

    # Preserve the original value so render_changes can decide whether an effective change occurred.
    original_value: str = ""

    # Preserve the final value separately because individual log entries may describe intermediate transformations.
    coerced_value: str = ""

    # Use default_factory to avoid sharing mutable log lists across Result instances.
    changes: list[Log] = field(default_factory=list)

    def render_changes(self) -> tuple[str, ...]:
        """
        Render human-readable change lines for reporting.

        Emits one formatted line per logged transformation only when original_value and coerced_value differ. Returns an empty tuple when no effective change exists.

        Returns:
            tuple[str, ...]: One formatted line per logged transformation, or an empty tuple when no effective change exists.
        """
        # Accumulate strings in insertion order so the returned tuple preserves the transformation sequence.
        formatted_logs: list[str] = []

        # Suppress logs when the final value equals the original value because callers treat no effective change as no reportable change.
        if self.original_value != self.coerced_value:
            # Keep the message format centralized so each transformation line uses the same wording.
            msg_template = "{a!r} changed from {b!r} to {c!r}. {d}"

            # Render each stored change independently because a single result can contain multiple transformation steps.
            for entry in self.changes:
                # Use the entry-specific before and after values so intermediate transformations remain visible.
                formatted_logs.append(
                    msg_template.format(a=self.attr_name, b=entry.before, c=entry.after, d=entry.description)
                )

        # Return an immutable tuple so callers cannot mutate the rendered representation after creation.
        return tuple(formatted_logs)


@dataclass(frozen=True)
class Rule:
    """
    Represent a single regex-based coercion rule.

    Owns the source regex pattern, replacement, description, and compiled regex used for substitution.

    Invariants:
        - pattern is compiled during initialization.
        - _compiled_pattern stores the compiled regex after successful initialization.
        - Field values cannot be reassigned after initialization except through the initialization-time object.__setattr__ call in __post_init__.

    Attributes:
        pattern (str): Regular expression pattern to match.
        replacement (str | Callable[[Match[str]], str]): Replacement text or callable used by re.Pattern.sub.
        description (str): Description of the transformation for logs.
        _compiled_pattern (re.Pattern | None): Compiled regex assigned during initialization.
    """
    # Store the original pattern so error messages and diagnostics can report the authored regex.
    pattern: str

    # Accept either static replacement text or a callable because re.Pattern.sub supports both forms.
    replacement: Union[str, Callable[[Match[str]], str]]

    # Keep a human-readable explanation with the rule so callers can log why a substitution occurred.
    description: str

    # Initialize as None because the compiled pattern is derived after dataclass field initialization.
    _compiled_pattern: re.Pattern | None = field(init=False, repr=False, default=None)

    def __post_init__(self):
        """
        Compile the regex pattern and store it.

        Converts re.error into ValueError so invalid rules fail during initialization with rule-specific context.

        Raises:
            ValueError: If the regex pattern cannot be compiled.
        """
        try:
            # Compile at initialization so invalid regex patterns fail before the rule is used for substitution.
            compiled = re.compile(self.pattern)
        except re.error as exc:
            # Preserve the original regex exception as the cause while exposing the failing authored pattern.
            raise ValueError(
                f"Rule pattern failed to compile: {self.pattern!r}. Reason: {exc}. "
                "Verify the regex syntax or escape special characters."
            ) from exc

        # Bypass frozen dataclass assignment only for this derived initialization field.
        object.__setattr__(self, "_compiled_pattern", compiled)

    def sub(self, text: str) -> str:
        """
        Apply this rule's substitution to text.

        Uses the compiled regex created during initialization and applies the stored replacement.

        Args:
            text (str): Input text to transform.

        Returns:
            str: Text after applying the regex substitution.
        """
        # Rely on the class invariant established by __post_init__: _compiled_pattern is compiled before substitution.
        return self._compiled_pattern.sub(self.replacement, text)
