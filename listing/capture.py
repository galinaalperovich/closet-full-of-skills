"""Capture what Claude Code and Codex actually send to the model in each skills setup (no model is called).

A local stand-in server takes the place of the model API. Each harness is run exactly as in the study (same command,
flags and test folder), its first model request is saved, and a canned reply ends the run. Nothing reaches Anthropic
or OpenAI, and request headers (which carry credentials) are never stored.

    python3 listing/capture.py OUTDIR [claude] [codex]

Writes OUTDIR/<harness>__<setup>__<target>.json (the request bodies; they contain the harness system prompt and local
paths, so they stay out of the public repo). listing/analyze_listing.py turns them into a summary.
"""
import json, os, shutil, subprocess, sys, tempfile, threading, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODEX = os.environ.get("CODEX_BIN", "/Applications/Codex.app/Contents/Resources/codex-cli/bin/codex")
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
WHICH = set(sys.argv[2:]) or {"claude", "codex"}
prompts = json.load(open(os.path.join(S, "prompts.json")))
FIRST = {k.split(":")[1]: v[0] for k, v in prompts.items()}
TARGETS = [t for t in FIRST if os.path.isdir(os.path.join(S, "envs", "alone", t))]
CUR = {"label": None, "n": 0}

SSE = [("message_start", {"type": "message_start", "message": {"id": "msg_capture", "type": "message", "role": "assistant", "model": "capture",
        "content": [], "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 1}}}),
       ("content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}),
       ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "ok"}}),
       ("content_block_stop", {"type": "content_block_stop", "index": 0}),
       ("message_delta", {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 1}}),
       ("message_stop", {"type": "message_stop"})]

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self): self.send_response(404); self.end_headers()
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        try: req = json.loads(body)
        except Exception: req = None
        if self.path.endswith("/count_tokens"):
            return self._json(200, {"input_tokens": 100})
        if req is not None and CUR["label"]:
            CUR["n"] += 1
            json.dump({"path": self.path, "body": req}, open(os.path.join(OUT, f'{CUR["label"]}__req{CUR["n"]}.json'), "w"))
        if self.path.endswith("/messages"):
            if req and req.get("stream"):
                self.send_response(200); self.send_header("Content-Type", "text/event-stream"); self.end_headers()
                for ev, d in SSE: self.wfile.write(f"event: {ev}\ndata: {json.dumps(d)}\n\n".encode())
                return
            return self._json(200, {"id": "msg_capture", "type": "message", "role": "assistant", "model": "capture", "content": [{"type": "text", "text": "ok"}],
                                    "stop_reason": "end_turn", "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 1}})
        return self._json(400, {"error": {"type": "invalid_request_error", "message": "capture only"}})
    def _json(self, code, obj):
        b = json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

srv = ThreadingHTTPServer(("127.0.0.1", 0), H); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

ONLY = set(filter(None, os.environ.get("ONLY", "").split(",")))   # e.g. ONLY=crowd1000 for a quick test
def jobs():
    for t in TARGETS: yield "alone", t, os.path.join(S, "envs", "alone", t)
    for c in ("pack20", "crowd200", "crowd1000"): yield c, "pdf", os.path.join(S, "envs", c)

def run_claude(setup, t, cwd):
    tmp = tempfile.mkdtemp(prefix="cap_"); dst = os.path.join(tmp, os.path.basename(cwd)); shutil.copytree(cwd, dst, symlinks=True)
    env = dict(os.environ, ANTHROPIC_BASE_URL=f"http://127.0.0.1:{PORT}", ANTHROPIC_API_KEY="sk-ant-capture-dummy")
    if os.environ.get("CONFIG_DIR"): env["CLAUDE_CONFIG_DIR"] = os.environ["CONFIG_DIR"]   # a separate Claude Code state (usage record)
    cmd = ["claude", "-p", FIRST[t], "--model", os.environ.get("MODEL", "haiku"), "--output-format", "stream-json", "--verbose", "--setting-sources", "project",
           "--strict-mcp-config", "--no-session-persistence", "--max-turns", "3", "--disallowedTools", "Bash"]
    pr = subprocess.run(cmd, cwd=dst, env=env, capture_output=True, text=True, timeout=180, stdin=subprocess.DEVNULL)
    shutil.rmtree(tmp, ignore_errors=True)
    return pr.returncode

def run_codex(setup, t, cwd):
    cmd = [CODEX, "exec", "--json", "--ephemeral", "--skip-git-repo-check", "-s", "read-only", "-c", 'model_reasoning_effort="medium"',
           "-c", 'model_provider="capture"', "-c", 'model_providers.capture.name="capture"',
           "-c", f'model_providers.capture.base_url="http://127.0.0.1:{PORT}/v1"', "-c", 'model_providers.capture.wire_api="responses"',
           "-c", "model_providers.capture.request_max_retries=0", "-c", "model_providers.capture.stream_max_retries=0", FIRST[t]]
    pr = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    return pr.returncode

for h, fn in (("claude", run_claude), ("codex", run_codex)):
    if h not in WHICH: continue
    for setup, t, cwd in jobs():
        if ONLY and setup not in ONLY: continue
        CUR.update(label=f"{h}{os.environ.get('TAG', '')}__{setup}__{t}", n=0)
        rc = fn(setup, t, cwd)
        print(h, setup, t, "requests:", CUR["n"], "rc:", rc, flush=True)
CUR["label"] = None; srv.shutdown()
