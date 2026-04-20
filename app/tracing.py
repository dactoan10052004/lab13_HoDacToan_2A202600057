from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import get_client as _get_langfuse_client

    def get_langfuse_client():
        return _get_langfuse_client()

    class _LangfuseContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            _get_langfuse_client().update_current_trace(**kwargs)

        def update_current_observation(self, **kwargs: Any) -> None:
            # drop usage_details — already stored in metadata; update_current_span only
            kwargs.pop("usage_details", None)
            if kwargs:
                _get_langfuse_client().update_current_span(**kwargs)

    langfuse_context = _LangfuseContext()

except Exception:  # pragma: no cover
    def get_langfuse_client():  # type: ignore[misc]
        return _NullClient()

    class _NullSpan:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def start_as_current_span(self, **kwargs): return _NullSpan()

    class _NullClient:
        def start_as_current_span(self, **kwargs): return _NullSpan()
        def flush(self): pass

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
