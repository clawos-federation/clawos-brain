#!/bin/bash
# OpenClaw Skills Dependencies Installer
# 自动安装14个缺失依赖的skills

set -e

echo "🔍 OpenClaw Skills Dependencies Installer"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查环境变量
env_exists() {
    [ -n "${!1}" ]
}

echo "📋 检查缺失的依赖..."
echo ""

# 1. sag (ElevenLabs TTS)
echo "1️⃣ sag - ElevenLabs TTS"
if command_exists sag; then
    echo -e "  ${GREEN}✓ sag 已安装${NC}"
else
    echo -e "  ${YELLOW}⚠ sag 未安装${NC}"
    echo "  安装: brew install steipete/tap/sag"
    echo "  配置: export ELEVENLABS_API_KEY='your-key'"
fi
echo ""

# 2. notion
echo "2️⃣ notion - Notion API"
if [ -f ~/.config/notion/api_key ]; then
    echo -e "  ${GREEN}✓ notion API key 已配置${NC}"
else
    echo -e "  ${YELLOW}⚠ notion API key 未配置${NC}"
    echo "  配置: mkdir -p ~/.config/notion && echo 'ntn_your_key' > ~/.config/notion/api_key"
fi
echo ""

# 3. slack
echo "3️⃣ slack - Slack integration"
if [ -f ~/.config/slack/api_key ]; then
    echo -e "  ${GREEN}✓ slack API key 已配置${NC}"
else
    echo -e "  ${YELLOW}⚠ slack API key 未配置${NC}"
    echo "  配置: export SLACK_BOT_TOKEN='xoxb-your-token'"
fi
echo ""

# 4. spotify-player
echo "4️⃣ spotify-player - Spotify CLI"
if command_exists spotify_player || command_exists spogo; then
    echo -e "  ${GREEN}✓ spotify player 已安装${NC}"
else
    echo -e "  ${YELLOW}⚠ spotify player 未安装${NC}"
    echo "  安装: cargo install spotify_player 或 brew install spogo"
fi
echo ""

# 5. trello
echo "5️⃣ trello - Trello API"
if [ -f ~/.config/trello/api_key ]; then
    echo -e "  ${GREEN}✓ trello API key 已配置${NC}"
else
    echo -e "  ${YELLOW}⚠ trello API key 未配置${NC}"
    echo "  配置: export TRELLO_API_KEY='your-key' && export TRELLO_API_TOKEN='your-token'"
fi
echo ""

# 6. bluebubbles
echo "6️⃣ bluebubbles - iMessage via BlueBubbles"
if env_exists BLUEBUBBLES_SERVER_URL; then
    echo -e "  ${GREEN}✓ bluebubbles 已配置${NC}"
else
    echo -e "  ${YELLOW}⚠ bluebubbles 未配置${NC}"
    echo "  配置: export BLUEBUBBLES_SERVER_URL='http://your-server' && export BLUEBUBBLES_PASSWORD='your-password'"
fi
echo ""

# 7. goplaces
echo "7️⃣ goplaces - Google Places API"
if command_exists goplaces; then
    echo -e "  ${GREEN}✓ goplaces 已安装${NC}"
else
    echo -e "  ${YELLOW}⚠ goplaces 未安装${NC}"
    echo "  安装: go install github.com/tmc/goplaces@latest"
    echo "  配置: export GOOGLE_PLACES_API_KEY='your-key'"
fi
echo ""

# 8. model-usage
echo "8️⃣ model-usage - CodexBar cost tracking"
if command_exists codexbar; then
    echo -e "  ${GREEN}✓ codexbar 已安装${NC}"
else
    echo -e "  ${YELLOW}⚠ codexbar 未安装${NC}"
    echo "  安装: brew install codexbar 或 npm install -g codexbar"
fi
echo ""

# 9. nano-banana-pro
echo "9️⃣ nano-banana-pro - Gemini Image Generation"
if env_exists GOOGLE_API_KEY; then
    echo -e "  ${GREEN}✓ Google API key 已配置${NC}"
else
    echo -e "  ${YELLOW}⚠ Google API key 未配置${NC}"
    echo "  配置: export GOOGLE_API_KEY='your-key'"
fi
echo ""

# 10. openai-image-gen
echo "🔟 openai-image-gen - OpenAI Images API"
if env_exists OPENAI_API_KEY; then
    echo -e "  ${GREEN}✓ OpenAI API key 已配置${NC}"
else
    echo -e "  ${YELLOW}⚠ OpenAI API key 未配置${NC}"
    echo "  配置: export OPENAI_API_KEY='your-key'"
fi
echo ""

# 11. openai-whisper-api
echo "1️⃣1️⃣ openai-whisper-api - OpenAI Whisper API"
if env_exists OPENAI_API_KEY; then
    echo -e "  ${GREEN}✓ OpenAI API key 已配置 (与 image-gen 共用)${NC}"
else
    echo -e "  ${YELLOW}⚠ OpenAI API key 未配置${NC}"
fi
echo ""

# 12. session-logs
echo "1️⃣2️⃣ session-logs - Session log analysis"
if command_exists jq; then
    echo -e "  ${GREEN}✓ jq 已安装${NC}"
else
    echo -e "  ${YELLOW}⚠ jq 未安装${NC}"
    echo "  安装: brew install jq"
fi
echo ""

# 13. sherpa-onnx-tts
echo "1️⃣3️⃣ sherpa-onnx-tts - Local TTS"
if command_exists sherpa-onnx-offline-tts; then
    echo -e "  ${GREEN}✓ sherpa-onnx-tts 已安装${NC}"
else
    echo -e "  ${YELLOW}⚠ sherpa-onnx-tts 未安装${NC}"
    echo "  安装: 参考 https://github.com/k2-fsa/sherpa-onnx"
fi
echo ""

# 14. voice-call
echo "1️⃣4️⃣ voice-call - Voice call plugin"
if env_exists TWILIO_ACCOUNT_SID; then
    echo -e "  ${GREEN}✓ Twilio credentials 已配置${NC}"
else
    echo -e "  ${YELLOW}⚠ Twilio credentials 未配置${NC}"
    echo "  配置: export TWILIO_ACCOUNT_SID='your-sid' && export TWILIO_AUTH_TOKEN='your-token'"
fi
echo ""

echo "=========================================="
echo "📊 依赖检查完成"
echo ""
echo "💡 建议:"
echo "  - 安装高频使用的工具（如 sag, jq）"
echo "  - 配置常用 API keys（如 Notion, OpenAI）"
echo "  - 其他工具按需安装"
echo ""
