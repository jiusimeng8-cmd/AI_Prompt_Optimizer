"""High-confidence selected-text capture for global hotkey workflows.

The resolver is intentionally conservative. UI Automation / Accessibility is
treated as trusted because it can expose real selection ranges. Clipboard copy
is only used for a small whitelist of ordinary apps where empty-selection copy
does not commonly copy the current line/block.
"""

from __future__ import annotations

from dataclasses import dataclass
import ctypes
import time
from typing import Callable

import pyperclip


LogFn = Callable[[str, str], None]


@dataclass(frozen=True)
class CaptureResult:
    text: str
    method: str
    confidence: str
    source_app: str
    blocked_reason: str = ""

    @property
    def ok(self) -> bool:
        return bool(self.text.strip()) and self.confidence == "high" and not self.blocked_reason


class SelectionResolver:
    """Resolve the current real text selection without guessing by default."""

    # Keep this small. Electron, browsers, terminals and code editors are not
    # safe for clipboard fallback because no-selection copy can copy a line/block.
    CLIPBOARD_FALLBACK_ALLOWLIST = {
        "notepad.exe",
        "wordpad.exe",
        "write.exe",
    }

    HIGH_RISK_NAMES = (
        "code.exe",
        "cursor.exe",
        "trae.exe",
        "windsurf.exe",
        "opencode",
        "electron",
        "chrome.exe",
        "msedge.exe",
        "firefox.exe",
        "wezterm",
        "windows terminal",
        "powershell",
        "cmd.exe",
    )

    def __init__(self, log: LogFn | None = None):
        self._log = log or (lambda _event, _message="": None)
        self._user32 = ctypes.windll.user32

    def capture(self, target_hwnd: int) -> CaptureResult:
        source_app = self._describe_target(target_hwnd)

        uia_text = self._try_uia_selection()
        if uia_text:
            self._log("CAPTURE_OK", f"method=uia app={source_app} text={repr(uia_text[:50])}")
            return CaptureResult(uia_text, "uia", "high", source_app)

        process_name = self._get_process_name(target_hwnd).lower()
        if not self._allow_clipboard_fallback(process_name, source_app):
            reason = f"native selection unavailable; clipboard fallback disabled for {source_app}"
            self._log("CAPTURE_BLOCKED", reason)
            return CaptureResult("", "none", "none", source_app, reason)

        return self._try_clipboard_fallback(source_app)

    def _try_uia_selection(self) -> str:
        try:
            import uiautomation as auto
        except Exception as exc:
            self._log("UIA_UNAVAILABLE", repr(exc))
            return ""

        try:
            controls = []
            focused = auto.GetFocusedControl()
            if focused:
                controls.extend(self._control_and_ancestors(focused, limit=10))

            cursor_control = auto.ControlFromCursor()
            if cursor_control:
                controls.extend(self._control_and_ancestors(cursor_control, limit=10))

            seen = set()
            for control in controls:
                key = getattr(control, "NativeWindowHandle", 0) or id(control)
                if key in seen:
                    continue
                seen.add(key)

                text = self._selection_from_control(control, auto)
                if text:
                    return text
        except Exception as exc:
            self._log("UIA_ERROR", repr(exc))
        return ""

    def _control_and_ancestors(self, control, limit: int):
        current = control
        for _ in range(limit):
            if not current:
                break
            yield current
            try:
                current = current.GetParentControl()
            except Exception:
                break

    def _selection_from_control(self, control, auto) -> str:
        for pattern_id in (auto.PatternId.TextPattern, auto.PatternId.TextPattern2):
            try:
                pattern = control.GetPattern(pattern_id)
            except Exception:
                pattern = None
            if not pattern:
                continue

            try:
                ranges = pattern.GetSelection()
            except Exception:
                ranges = None
            if not ranges:
                continue

            parts = []
            for text_range in ranges:
                try:
                    value = text_range.GetText(65535)
                except Exception:
                    value = ""
                value = (value or "").strip()
                if value:
                    parts.append(value)
            if parts:
                return "\n".join(parts).strip()
        return ""

    def _try_clipboard_fallback(self, source_app: str) -> CaptureResult:
        original_clipboard = None
        try:
            original_clipboard = pyperclip.paste()
        except Exception:
            original_clipboard = None

        marker = f"_MK{int(time.time() * 1000) % 10000000}_"
        selected_text = ""
        try:
            pyperclip.copy(marker)
            time.sleep(0.03)
            self._send_copy_shortcut()

            start = time.time()
            while time.time() - start < 0.25:
                time.sleep(0.03)
                try:
                    result = pyperclip.paste()
                except Exception:
                    result = ""
                if result and result.strip() and result != marker and "_MK" not in result:
                    selected_text = result.strip()
                    break
        finally:
            try:
                pyperclip.copy(original_clipboard or "")
            except Exception:
                pass

        if not selected_text:
            reason = f"clipboard fallback found no explicit selection for {source_app}"
            self._log("CAPTURE_BLOCKED", reason)
            return CaptureResult("", "clipboard", "none", source_app, reason)

        self._log("CAPTURE_OK", f"method=clipboard app={source_app} text={repr(selected_text[:50])}")
        return CaptureResult(selected_text, "clipboard", "high", source_app)

    def _send_copy_shortcut(self):
        # Ctrl+C is acceptable only in whitelist fallback mode.
        self._user32.keybd_event(0x11, 0, 0, 0)  # Ctrl down
        time.sleep(0.02)
        self._user32.keybd_event(0x43, 0, 0, 0)  # C down
        time.sleep(0.02)
        self._user32.keybd_event(0x43, 0, 2, 0)  # C up
        time.sleep(0.02)
        self._user32.keybd_event(0x11, 0, 2, 0)  # Ctrl up

    def _allow_clipboard_fallback(self, process_name: str, source_app: str) -> bool:
        lowered = f"{process_name} {source_app}".lower()
        if any(name in lowered for name in self.HIGH_RISK_NAMES):
            return False
        return process_name in self.CLIPBOARD_FALLBACK_ALLOWLIST

    def _describe_target(self, hwnd: int) -> str:
        title = ""
        try:
            title_len = self._user32.GetWindowTextLengthW(hwnd)
            if title_len > 0:
                buf = ctypes.create_unicode_buffer(title_len + 1)
                self._user32.GetWindowTextW(hwnd, buf, title_len + 1)
                title = buf.value
        except Exception:
            pass
        process_name = self._get_process_name(hwnd)
        return f"{process_name} | {title}".strip(" |")

    def _get_process_name(self, hwnd: int) -> str:
        try:
            import win32process
            import win32api

            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            handle = win32api.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
            path = win32process.GetModuleFileNameEx(handle, 0)
            win32api.CloseHandle(handle)
            return path.rsplit("\\", 1)[-1]
        except Exception:
            return "unknown"
