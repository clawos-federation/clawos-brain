#!/bin/bash
# OpenCode 快速启动脚本

OPENCODE_BIN="$HOME/.opencode/bin/opencode"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示菜单
show_menu() {
    echo -e "${BLUE}=== OpenCode 快速启动 ===${NC}"
    echo ""
    echo "常用 Agents:"
    echo "  1) reflex      - 快速格式化、linting"
    echo "  2) oracle      - 架构设计、代码审查"
    echo "  3) sisyphus    - 主编排器（复杂任务）"
    echo "  4) researcher  - 深度调研"
    echo "  5) chief       - 主编（探索+协调）"
    echo ""
    echo "其他选项:"
    echo "  w) web         - 启动 Web 界面"
    echo "  l) list        - 列出所有模型"
    echo "  a) agents      - 列出所有 agents"
    echo "  c) categories  - 列出所有类别"
    echo "  h) help        - 显示帮助"
    echo "  q) quit        - 退出"
    echo ""
}

# 启动 agent
start_agent() {
    local agent=$1
    echo -e "${GREEN}启动 OpenCode (agent: $agent)${NC}"
    "$OPENCODE_BIN" --agent "$agent"
}

# 列出 agents
list_agents() {
    echo -e "${BLUE}=== 可用的 Agents ===${NC}"
    python3 opencode_wrapper.py --list-agents
}

# 列出类别
list_categories() {
    echo -e "${BLUE}=== 可用的类别 ===${NC}"
    python3 opencode_wrapper.py --list-categories
}

# 主循环
main() {
    if [ $# -eq 0 ]; then
        # 无参数，显示菜单
        while true; do
            show_menu
            read -p "请选择 [1-5/w/l/a/c/h/q]: " choice

            case $choice in
                1) start_agent reflex ;;
                2) start_agent oracle ;;
                3) start_agent sisyphus ;;
                4) start_agent researcher ;;
                5) start_agent chief ;;
                w) echo -e "${GREEN}启动 Web 界面...${NC}"; "$OPENCODE_BIN" web ;;
                l) "$OPENCODE_BIN" models ;;
                a) list_agents ;;
                c) list_categories ;;
                h) "$OPENCODE_BIN" --help ;;
                q) echo -e "${YELLOW}退出${NC}"; exit 0 ;;
                *) echo -e "${YELLOW}无效选择，请重试${NC}" ;;
            esac

            echo ""
            read -p "按 Enter 继续..."
            clear
        done
    else
        # 有参数，直接执行
        case $1 in
            reflex|oracle|sisyphus|researcher|chief)
                start_agent "$1"
                ;;
            web)
                "$OPENCODE_BIN" web
                ;;
            list|models)
                "$OPENCODE_BIN" models
                ;;
            agents)
                list_agents
                ;;
            categories)
                list_categories
                ;;
            help|--help|-h)
                "$OPENCODE_BIN" --help
                ;;
            *)
                echo -e "${YELLOW}用法: $0 [agent|web|list|agents|categories|help]${NC}"
                exit 1
                ;;
        esac
    fi
}

main "$@"
