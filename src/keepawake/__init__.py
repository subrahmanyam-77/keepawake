"""keep_awake: stop autosuspend from putting this PC to sleep while code runs.

Safe to use everywhere: on any machine without autosuspend (Windows, macOS,
other Linux PCs, the lab machine) it silently does nothing.

All of these work:

    from keepawake import keep_awake

    with keep_awake:            # block, no parentheses
        run_sweep()

    with keep_awake():          # block, with parentheses
        run_sweep()

    @keep_awake                 # decorator, no parentheses
    def long_job(): ...

    @keep_awake()               # decorator, with parentheses
    def other_job(): ...
"""

import functools
import os
import sys
import threading
import uuid
from pathlib import Path

FLAG_DIR = Path("/tmp/keepawake")

# Only active on Linux machines that actually run autosuspend.
ENABLED = sys.platform.startswith("linux") and Path("/etc/autosuspend.conf").exists()


class _KeepAwake:
    def __init__(self):
        self._local = threading.local()   # per-thread stack of flags (nesting/threads safe)

    def _stack(self):
        if not hasattr(self._local, "flags"):
            self._local.flags = []
        return self._local.flags

    # --- context manager ---
    def __enter__(self):
        flag = None
        if ENABLED:
            try:
                FLAG_DIR.mkdir(exist_ok=True)
                # "<pid>-<random>": each use has its own flag; autosuspend
                # reads the pid part and ignores flags of dead processes.
                flag = FLAG_DIR / f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
                flag.touch()
            except OSError:
                flag = None   # couldn't set the flag: carry on, never crash the job
        self._stack().append(flag)
        return self

    def __exit__(self, *exc):
        flag = self._stack().pop()
        if flag is not None:
            flag.unlink(missing_ok=True)
        return False          # never swallow exceptions

    # --- keep_awake() and @keep_awake / @keep_awake() ---
    def __call__(self, func=None):
        if func is None:      # keep_awake() -> same object, usable as block or decorator
            return self

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper


keep_awake = _KeepAwake()
