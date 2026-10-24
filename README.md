# keepawake

Tiny helper that stops [autosuspend](https://github.com/languitar/autosuspend) from
putting a Linux machine to sleep while a piece of Python code is running.

On any machine that does not run autosuspend (no `/etc/autosuspend.conf`), including
Windows and macOS, it does nothing, so it is safe to use in shared code.

## Install

```bash
uv add "keepawake @ git+https://github.com/subrahmanyam-77/keepawake"
```

## Use

```python
from keepawake import keep_awake

with keep_awake:          # or: with keep_awake():
    run_long_simulation()

@keep_awake               # or: @keep_awake()
def overnight_sweep():
    ...
```

## How it works

While active, it creates a flag file `/tmp/keepawake/<pid>-<random>`.
An autosuspend `ExternalCommand` check treats the machine as busy while any flag
belongs to a running process; flags left behind by crashed processes are ignored.
