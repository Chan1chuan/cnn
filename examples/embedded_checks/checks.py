"""Small hardware-free examples for testing embedded assumptions."""

from __future__ import annotations

import re


class FrameDecoder:
    """Decode synthetic 2-byte little-endian length + payload frames.

    Every frame has a nonzero length up to max_payload. An invalid header
    rejects the rest of that input and resets the decoder.
    """

    def __init__(self, max_payload: int = 1024) -> None:
        if not 1 <= max_payload <= 65535:
            raise ValueError("invalid payload limit")
        self.max_payload = max_payload
        self._buffer = bytearray()
        self._remaining: int | None = None

    def feed(self, chunk: bytes) -> list[bytes]:
        view = memoryview(chunk)
        result = []
        while view:
            target = 2 if self._remaining is None else self._remaining
            count = min(len(view), target - len(self._buffer))
            self._buffer.extend(view[:count])
            view = view[count:]
            if len(self._buffer) != target:
                continue
            if self._remaining is None:
                length = int.from_bytes(self._buffer, "little")
                self._buffer.clear()
                if not 1 <= length <= self.max_payload:
                    raise ValueError("invalid frame length")
                self._remaining = length
            else:
                result.append(bytes(self._buffer))
                self._buffer.clear()
                self._remaining = None
        return result

    def finish(self) -> None:
        """Raise if a finite stream ended partway through a frame."""
        if self._buffer or self._remaining is not None:
            raise ValueError("truncated frame")


def elapsed_ticks(start: int, end: int, *, bits: int = 24, down: bool = True) -> int:
    """Return a counter delta assuming less than one full counter period elapsed."""
    if not 1 <= bits <= 64:
        raise ValueError("invalid counter width")
    modulus = 1 << bits
    if not (0 <= start < modulus and 0 <= end < modulus):
        raise ValueError("counter value outside width")
    return ((start - end) if down else (end - start)) % modulus


def saved_register_bytes(spec: str) -> int:
    """Count bytes for a contiguous list of single- or double-width FP registers.

    This is arithmetic for the register save only, not a stack bound.
    """
    numbers = []
    kind = None
    for item in spec.split(","):
        part = re.fullmatch(r"([sd])(\d+)(?:-([sd])(\d+))?", item.strip())
        if part is None:
            raise ValueError("invalid register list")
        start_kind, start, end_kind, end = part.groups()
        kind = kind or start_kind
        if start_kind != kind or end_kind not in (None, kind):
            raise ValueError("mixed register widths")
        lo, hi = int(start), int(end if end is not None else start)
        limit = 31 if kind == "s" else 15
        if not 0 <= lo <= hi <= limit:
            raise ValueError("register outside range")
        numbers.extend(range(lo, hi + 1))
    if numbers != list(range(numbers[0], numbers[-1] + 1)):
        raise ValueError("list must be contiguous and ordered")
    return len(numbers) * (4 if kind == "s" else 8)
