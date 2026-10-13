"""fit_agent_context keeps the node's /conversation/start body under the server's 1 MiB limit."""

import json

from clients.jarvis_command_center_client import MAX_AGENT_CONTEXT_BYTES, fit_agent_context


def test_small_context_is_returned_unchanged():
    ctx = {"home_assistant": {"light_controls": {"a": 1}, "devices": [1, 2]}}
    assert fit_agent_context(ctx) is ctx


def test_drops_the_largest_unused_entry_and_keeps_prompt_keys():
    ctx = {
        "home_assistant": {
            "light_controls": {"living": ["light.a"]},
            "device_controls": {"switch": {"x": "switch.x"}},
            "devices": [{"id": i, "entities": ["e" * 40] * 5} for i in range(3000)],  # well over the limit
        },
        "weather": {"temperature": 21},
    }
    assert len(json.dumps(ctx)) > MAX_AGENT_CONTEXT_BYTES
    out = fit_agent_context(ctx)
    assert "devices" not in out["home_assistant"]
    assert out["home_assistant"]["light_controls"] == {"living": ["light.a"]}
    assert out["home_assistant"]["device_controls"] == {"switch": {"x": "switch.x"}}
    assert out["weather"] == {"temperature": 21}
    assert len(json.dumps(out)) <= MAX_AGENT_CONTEXT_BYTES
    assert "devices" in ctx["home_assistant"]  # the caller's own copy (used by the entity resolver) is untouched


def test_never_raises_on_odd_input():
    assert fit_agent_context({"x": object()}, limit=1) is not None
