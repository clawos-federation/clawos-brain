#!/bin/bash

# Codespaces Usage Monitor
# Monitors GitHub Codespaces usage and remaining quota

# Constants
MONTHLY_QUOTA_HOURS=120
QUOTA_MINUTES=$((MONTHLY_QUOTA_HOURS * 60))

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to format minutes to hours and minutes
format_duration() {
    local total_minutes=$1
    local hours=$((total_minutes / 60))
    local minutes=$((total_minutes % 60))
    echo "${hours}h ${minutes}m"
}

# Function to calculate percentage (returns integer)
calc_percentage() {
    local used=$1
    local total=$2
    if [ -z "$total" ] || [ "$total" -eq 0 ] 2>/dev/null; then
        echo "0"
    else
        echo $(( used * 100 / total ))
    fi
}

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}    GitHub Codespaces Usage Report${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get current user
CURRENT_USER=$(gh api user --jq '.login' 2>/dev/null || echo "unknown")
echo -e "Account: ${GREEN}${CURRENT_USER}${NC}"
echo ""

# Get codespaces list
echo -e "${YELLOW}Fetching usage data...${NC}"
CODESPACES=$(gh codespace list --json name,state,repository,owner 2>/dev/null || echo "[]")

# Count codespaces - use xargs to trim whitespace
ACTIVE_COUNT=$(echo "$CODESPACES" | jq '[.[] | select(.state == "Available")] | length' 2>/dev/null | xargs || echo "0")
TOTAL_COUNT=$(echo "$CODESPACES" | jq 'length' 2>/dev/null | xargs || echo "0")

# Ensure numeric values
ACTIVE_COUNT=${ACTIVE_COUNT:-0}
TOTAL_COUNT=${TOTAL_COUNT:-0}

echo ""
echo -e "${BLUE}--- Codespaces Status ---${NC}"
echo -e "Total Codespaces: ${TOTAL_COUNT}"
echo -e "Active (Available): ${GREEN}${ACTIVE_COUNT}${NC}"
echo ""

# List codespaces
if [ "$TOTAL_COUNT" -gt 0 ] 2>/dev/null; then
    echo -e "${BLUE}--- Codespaces List ---${NC}"
    echo "$CODESPACES" | jq -r '.[] | "  • \(.name) [\(.state)] - \(.repository)"' 2>/dev/null | head -20
    if [ "$TOTAL_COUNT" -gt 20 ] 2>/dev/null; then
        echo "  ... and $((TOTAL_COUNT - 20)) more"
    fi
    echo ""
fi

# Try to get actual usage from billing API
# Note: GitHub's billing API may require specific permissions
USED_MINUTES=0

# Attempt to get included minutes usage
USAGE_INFO=$(gh api /user/settings/billing/codespaces 2>/dev/null || echo "{}")
USED_MINUTES_RAW=$(echo "$USAGE_INFO" | jq -r '.minutes_used // 0' 2>/dev/null | xargs || echo "0")

# Ensure it's a valid number
if [[ "$USED_MINUTES_RAW" =~ ^[0-9]+$ ]]; then
    USED_MINUTES=$USED_MINUTES_RAW
fi

# If we couldn't get actual usage
if [ "$USED_MINUTES" -eq 0 ] 2>/dev/null; then
    echo -e "${YELLOW}Note: Unable to fetch exact usage from billing API.${NC}"
    echo -e "${YELLOW}       Check https://github.com/settings/billing for actual usage.${NC}"
    echo ""
fi

REMAINING_MINUTES=$((QUOTA_MINUTES - USED_MINUTES))
if [ "$REMAINING_MINUTES" -lt 0 ] 2>/dev/null; then
    REMAINING_MINUTES=0
fi

USED_PERCENT=$(calc_percentage "$USED_MINUTES" "$QUOTA_MINUTES")
REMAINING_PERCENT=$((100 - USED_PERCENT))

echo -e "${BLUE}--- Monthly Quota ---${NC}"
echo -e "Total Quota:     $(format_duration $QUOTA_MINUTES)"
echo -e "Used:            $(format_duration $USED_MINUTES) (${USED_PERCENT}%)"
echo -e "Remaining:       $(format_duration $REMAINING_MINUTES) (${REMAINING_PERCENT}%)"
echo ""

# Visual progress bar
BAR_WIDTH=40
if [ "$QUOTA_MINUTES" -gt 0 ] 2>/dev/null; then
    FILLED=$((USED_MINUTES * BAR_WIDTH / QUOTA_MINUTES))
else
    FILLED=0
fi
if [ "$FILLED" -gt "$BAR_WIDTH" ] 2>/dev/null; then
    FILLED=$BAR_WIDTH
fi
EMPTY=$((BAR_WIDTH - FILLED))

printf "Usage: ["
printf "%${FILLED}s" | tr ' ' '█'
printf "%${EMPTY}s" | tr ' ' '░'
printf "] ${USED_PERCENT}%%\n"
echo ""

# Warning if usage is high
if [ "$USED_PERCENT" -gt 80 ] 2>/dev/null; then
    echo -e "${RED}⚠ Warning: Usage exceeds 80% of monthly quota!${NC}"
elif [ "$USED_PERCENT" -gt 60 ] 2>/dev/null; then
    echo -e "${YELLOW}⚠ Notice: Usage exceeds 60% of monthly quota${NC}"
else
    echo -e "${GREEN}✓ Usage is within normal range${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "Tip: Run 'gh codespace delete --all' to clean up unused codespaces"
echo -e "Tip: Check usage at: https://github.com/settings/billing"
echo -e "${BLUE}========================================${NC}"
