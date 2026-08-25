"""
How a translation run is paced.

The CLI and the server pace their runs the same way, so the numbers live here
rather than being spelled out on both sides. The server layers its own spend
and resource limits on top in `server/settings.py`; those are its alone, because
they bound what a *visitor* may spend on the owner's key, and the CLI has no
visitors.

Every setting here is read from `env_file` on **every access**, so editing
`settings.env` retunes the next run without a restart. That is what the
module-level `__getattr__` below is for: `pacing.GEMINI_MODEL` still reads like a
constant at all fifteen call sites, but there is no constant behind it any more
— which also means a name assigned here would shadow the live value silently,
so don't.
"""

from . import env_file

# The pacing settings, and what each is worth when `settings.env` says nothing.
#
# GEMINI_MODEL defaults to the model `settings.env` ships with, so an unset
# value behaves like the documented setup rather than quietly picking a
# costlier one.
#
# REQUESTS_PER_MINUTE is one dial doing two jobs: it caps the rolling-window
# rate limiter and sizes the worker pool. A pool larger than the per-minute
# allowance would only park threads inside the limiter, so the two are never
# worth setting apart.
_PACING = {
    "GEMINI_MODEL": "gemini-3.5-flash-lite",
    "REQUESTS_PER_MINUTE": 4,
    "TOKENS_PER_MINUTE": 250000,
    "TOKENS_PER_REQUEST": 15000,
}


def __getattr__(name: str):
    """Read a pacing setting now, rather than having read it at import."""
    if name not in _PACING:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    default = _PACING[name]
    if isinstance(default, str):
        return env_file.text(name, default)

    value = env_file.integer(name, default)

    # Floored at 1 because MINUTES_BETWEEN_TRANSLATIONS uses 0 to mean "off",
    # which makes 0 an easy guess for "no limit" here too. It would instead size
    # the worker pool at zero, and that only raises from the run thread, long
    # after the setting was read.
    return max(1, value) if name == "REQUESTS_PER_MINUTE" else value
