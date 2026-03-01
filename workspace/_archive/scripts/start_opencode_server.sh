#!/bin/bash
# 启动 OpenCode ACP 服务器

OPENCODE_BIN="$HOME/.opencode/bin/opencode"
PORT=4096
HOST="127.0.0.1"

echo "Starting OpenCode ACP server on $HOST:$PORT..."
echo "Press Ctrl+C to stop"

"$OPENCODE_BIN" acp --port "$PORT" --hostname "$HOST"
