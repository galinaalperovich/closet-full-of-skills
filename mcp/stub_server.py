"""Minimal MCP stdio server: serves tool definitions from a JSON file, returns a stub result on call.
Usage: python3 stub_server.py <server_name> <tools.json>   (tools.json = list of {name, description, inputSchema})"""
import json, sys
name, path = sys.argv[1], sys.argv[2]
tools = json.load(open(path))
def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n"); sys.stdout.flush()
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try: req = json.loads(line)
    except Exception: continue
    m, rid = req.get("method"), req.get("id")
    if rid is None: continue  # notifications
    if m == "initialize":
        pv = (req.get("params") or {}).get("protocolVersion", "2025-06-18")
        send({"jsonrpc": "2.0", "id": rid, "result": {"protocolVersion": pv, "capabilities": {"tools": {}}, "serverInfo": {"name": name, "version": "0.0.1"}}})
    elif m == "tools/list":
        send({"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}})
    elif m == "tools/call":
        send({"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": "Done."}]}})
    elif m == "ping":
        send({"jsonrpc": "2.0", "id": rid, "result": {}})
    else:
        send({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "method not found"}})
