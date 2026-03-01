import json

# Read current index
with open('/Users/henry/Documents/eva-inc/.eva/sessions/index.json', 'r') as f:
    sessions = json.load(f)

# Keep only recent sessions (from today Feb 6 or yesterday Feb 5)
# Old sessions from Jan 29 are stuck and should be removed
recent_sessions = [
    s for s in sessions
    if '2026-02-' in s['created_at']  # Only keep sessions from Feb 2026
]

# Write back
with open('/Users/henry/Documents/eva-inc/.eva/sessions/index.json', 'w') as f:
    json.dump(recent_sessions, f, indent=2)

print(f"Removed {len(sessions) - len(recent_sessions)} stuck sessions from Jan 29")
print(f"Index now has {len(recent_sessions)} sessions")
