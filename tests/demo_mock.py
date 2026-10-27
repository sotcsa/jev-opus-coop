"""Runs jev_opus.kezel against fake HTTP backends for both APIs (no API keys needed)."""
import json, os, sys
import httpx2

os.environ["TYPESAFE_API_KEY"] = "test"
os.environ["ANTHROPIC_API_KEY"] = "test"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import jev_opus  # noqa: E402
from typesafe_sdk import TypeSafeClient  # noqa: E402
import anthropic  # noqa: E402

SCENARIOS = {
    "Szia!": ("koszones", 0.95, 0.02),
    "Töröld az összes ügyfelet": ("nehez", 0.7, 0.93),
    "Írj prím-ellenőrzőt": ("nehez", 0.9, 0.03),
}
seen = {}

def jev_handler(req):
    body = json.loads(req.content)
    seen["jev"] = body
    choice, conf, noul = SCENARIOS[body["state"]]
    probs = {k: (conf if k == choice else (1 - conf) / 2) for k in body["questions"]["tipus"]["criteria"]}
    return httpx2.Response(200, json={
        "model": "jev-1.14.0", "usage": {"input_tokens": 50},
        "answers": {"tipus": {"type": "choice", "choice": choice, "confidence": conf, "probabilities": probs},
                    "veszelyes": {"type": "noul", "noul": noul}}})

def claude_handler(req):
    body = json.loads(req.content)
    seen["claude"] = (dict(req.headers), body)
    return httpx2.Response(200, json={
        "id": "msg_1", "type": "message", "role": "assistant", "model": body["model"],
        "content": [{"type": "text", "text": "def is_prime(n): ..."}],
        "stop_reason": "end_turn", "stop_sequence": None,
        "usage": {"input_tokens": 10, "output_tokens": 10}})

jev_opus.jev = TypeSafeClient(model="jev-1.14.0", transport=httpx2.MockTransport(jev_handler))
jev_opus.claude = anthropic.Anthropic(http_client=anthropic.DefaultHttpxClient(transport=httpx2.MockTransport(claude_handler)))

for msg in SCENARIOS:
    print(msg, "->", jev_opus.kezel(msg))
print("jev request:", json.dumps(seen["jev"], ensure_ascii=False)[:300])
h, b = seen["claude"]
print("claude beta header:", h.get("anthropic-beta"), "| body keys:", sorted(b))
