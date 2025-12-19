#!/bin/bash
# Hard Reset Script for Cursor
# This will clear Cursor's cache and state to fix persistent review bar issues

echo "🔄 Hard Resetting Cursor..."
echo ""

# Step 1: Remove worktree if it exists
echo "1. Removing worktree..."
cd /Users/gernotohner/dev/personal/fdtd 2>/dev/null || cd "$(dirname "$0")"
git worktree remove --force /Users/gernotohner/.cursor/worktrees/fdtd/yem 2>/dev/null && echo "   ✓ Worktree removed" || echo "   ℹ Worktree already removed or doesn't exist"

# Step 2: Kill Cursor processes
echo ""
echo "2. Stopping Cursor processes..."
pkill -9 "Cursor" 2>/dev/null && echo "   ✓ Cursor processes stopped" || echo "   ℹ No Cursor processes running"

# Step 3: Clear Cursor cache (Mac)
echo ""
echo "3. Clearing Cursor cache..."
CURSOR_CACHE="$HOME/Library/Application Support/Cursor/Cache"
CURSOR_STORAGE="$HOME/Library/Application Support/Cursor/User/workspaceStorage"
CURSOR_STATE="$HOME/Library/Application Support/Cursor/User/globalStorage"

if [ -d "$CURSOR_CACHE" ]; then
    rm -rf "$CURSOR_CACHE"/* 2>/dev/null
    echo "   ✓ Cache cleared"
else
    echo "   ℹ Cache directory not found"
fi

# Step 4: Clear workspace storage
if [ -d "$CURSOR_STORAGE" ]; then
    # Find and remove this project's workspace storage
    find "$CURSOR_STORAGE" -type d -name "*fdtd*" -exec rm -rf {} + 2>/dev/null
    echo "   ✓ Workspace storage cleared"
fi

# Step 5: Clear global state
if [ -d "$CURSOR_STATE" ]; then
    # Clear git-related state
    find "$CURSOR_STATE" -type f -name "*git*" -delete 2>/dev/null
    find "$CURSOR_STATE" -type f -name "*review*" -delete 2>/dev/null
    echo "   ✓ Global state cleared"
fi

echo ""
echo "✅ Reset complete!"
echo ""
echo "Next steps:"
echo "1. Wait 5 seconds for processes to fully stop"
echo "2. Open Cursor"
echo "3. Open the folder: /Users/gernotohner/dev/personal/fdtd"
echo "4. The review bar should be gone"
echo ""

