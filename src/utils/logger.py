from colorama import Fore, Style, init
from datetime import datetime
import os
import threading
import queue
import atexit
import sys

init(autoreset=True)


class _Logger:

    def __init__(self, log_dir="logs", buffer_size=2000, batch_size=50, no_color=False, debug=False):
        self.log_dir = log_dir
        self.batch_size = batch_size
        self.no_color = no_color or not sys.stdout.isatty()
        os.makedirs(self.log_dir, exist_ok=True)

        self.pid = os.getpid()
        self.debug_enabled = debug

        self.q = queue.Queue(maxsize=buffer_size)
        self._stop = threading.Event()

        self._current_date = None
        self._file = None

        self._worker = threading.Thread(target=self._writer, daemon=True)
        self._worker.start()

        atexit.register(self._shutdown)

    # ---------- time ----------
    def _now(self):
        return datetime.now()

    def _ts(self, now):
        return now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def _file_path(self, now):
        date_str = now.strftime("%Y%m%d")
        return os.path.join(self.log_dir, f"app_{date_str}.log")

    # ---------- file management ----------
    def _ensure_file(self, now):
        date_str = now.strftime("%Y%m%d")
        if self._current_date != date_str:
            if self._file:
                try:
                    self._file.close()
                except Exception:
                    pass
            self._current_date = date_str
            try:
                self._file = open(self._file_path(now), "a", encoding="utf-8", buffering=1)
            except Exception:
                self._file = None

    # ---------- async writer ----------
    def _writer(self):
        buffer = []
        last_flush = self._now()

        while not self._stop.is_set() or not self.q.empty():
            try:
                line = self.q.get(timeout=0.5)
                buffer.append(line)
                self.q.task_done()
            except queue.Empty:
                pass

            now = self._now()

            # flush if:
            # 1. buffer big
            # 2. stopping
            # 3. 1 second passed (NEW)
            if (
                buffer
                and (
                    len(buffer) >= self.batch_size
                    or self._stop.is_set()
                    or (now - last_flush).total_seconds() >= 1
                )
            ):
                self._ensure_file(now)
                if self._file:
                    try:
                        self._file.writelines(buffer)
                        self._file.flush()
                    except Exception:
                        pass
                buffer.clear()
                last_flush = now

    def _shutdown(self):
        self._stop.set()
        self._worker.join(timeout=3)
        if self._file:
            try:
                self._file.close()
            except Exception:
                pass

    def _enqueue(self, level, msg, now):
        if level == "DBG" and not self.debug_enabled:
            return
        line = f"{self._ts(now)} [{self.pid}] [{level}] {msg}\n"
        try:
            self.q.put_nowait(line)
        except queue.Full:
            pass

    # ---------- runtime setter -----------

    def set_debug(self, enabled: bool):
        self.debug_enabled = bool(enabled)

    # ---------- console ----------
    def _print(self, color, symbol, msg, now):
        ts = self._ts(now)
        if self.no_color:
            print(f"{ts} [{self.pid}] [{symbol}] {msg}")
        else:
            print(
                Style.BRIGHT
                + Fore.LIGHTBLACK_EX
                + ts
                + Fore.RESET
                + f" [{self.pid}] ["
                + color
                + symbol
                + Fore.RESET
                + "] "
                + Style.RESET_ALL
                + msg
            )
    # ---------- public ----------
    def info(self, msg):
        now = self._now()
        self._print(Fore.GREEN, "+", msg, now)
        self._enqueue("INF", msg, now)

    def warn(self, msg):
        now = self._now()
        self._print(Fore.YELLOW, "!", msg, now)
        self._enqueue("WRN", msg, now)

    def debug(self, msg):
        if not self.debug_enabled:
            return
        now = self._now()
        self._print(Fore.MAGENTA, "*", msg, now)
        self._enqueue("DBG", msg, now)

    def error(self, msg):
        now = self._now()
        self._print(Fore.RED, "-", msg, now)
        self._enqueue("ERR", msg, now)


logger = _Logger()
