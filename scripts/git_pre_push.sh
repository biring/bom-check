# *** Git pre-push script ***
#
# This script is called by the Git pre-push hook file located at:
#     .git/hooks/pre-push
#
# The pre-push hook file must contain the following (or equivalent):
# --------------------------------------------------------------------------------
#      #!/usr/bin/env bash
#
#      # Get repo root (via Git, not relative to .git/hooks)
#      REPO_ROOT="$(git rev-parse --show-toplevel)"
#      cd "$REPO_ROOT" || { echo "❌ PUSH ABORTED! Failed to change to repo root: $REPO_ROOT"; exit 1; }
#
#      # Path to the tracked pre-push script
#      SCRIPT_PATH="$REPO_ROOT/scripts/git_pre_push.sh"
#
#      # Check if the pre-push script exists
#      if [ ! -f "$SCRIPT_PATH" ]; then
#          echo "❌ PUSH ABORTED! Missing pre-push script: $SCRIPT_PATH"
#          exit 1
#      fi
#
#      # Execute the pre-push script
#      bash "$SCRIPT_PATH"
# --------------------------------------------------------------------------------

echo "🔍 Running pre-push checks..."

# Navigate to the root of the repository (assuming this script is in ./scripts/)
# Step 1: Get the directory of this script
SCRIPT_DIR="$(dirname "$0")"
# Step 2: Move one directory up (repo root)
REPO_ROOT="$SCRIPT_DIR/.."
# Step 3: Change to the repo root directory
cd "$REPO_ROOT" || { echo "❌ PUSH ABORTED! Failed to change to repo root"; exit 1; }

# Run unit tests
echo "🧪 Running unit tests..."
python scripts/run_unit_test.py
if [ $? -ne 0 ]; then
    echo "❌ PUSH ABORTED! Unit tests failed."
    exit 1
else
    echo "✅ Unit test passes. "
fi

# Run build executable
echo "🔨 Building executable..."
python scripts/build_exe.py
if [ $? -ne 0 ]; then
    echo "❌ PUSH ABORTED! Build FAILED."
    exit 1
else
    echo "✅ Build successful."
fi

echo "✅ All pre-push checks passed."
exit 0
