#!/usr/bin/env bash

# ========== symlink to UnityProject/Assets/Scripts ========== #




# ========= the usual ========== #
OS_TYPE=$(uname -s)
if [ -f "/data/data/com.termux/files/usr/bin/termux-info" ]; then
    ENVIRONMENT="termux"
else
    ENVIRONMENT="linux"
fi
if command -v apt >/dev/null; then
    PACKAGE_MANAGER="apt"
elif command -v pkg >/dev/null; then
    PACKAGE_MANAGER="pkg"  # Termux
fi
ARCH=$(uname -m)
echo "OS: $OS_TYPE Environment: $ENVIRONMENT Architecture: $ARCH"

trap 'echo "Phase interrupted, continuing..."; return 0 2>/dev/null || true' INT

# =====================================
# Configuration
# =====================================

echo "VLA* path: $VLA_STAR_PATH"
if [ -n "$VLA_STAR_PATH" ]; then
    VLA_Star_dir="$VLA_STAR_PATH"
else
    echo "Choosing default VLA_Star path"
    VLA_Star_dir="$HOME/VLA_Star"
fi

cd $VLA_Star_dir

# If $OPENAI_API_KEY is not set, read it from the local file

# This should really be a phase requirement. Nontrivial to figure out what keys are needed.

if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f "$VLA_Star_dir/private/api_keys/openai_api_key" ]; then
        OPENAI_API_KEY=$(<"$VLA_Star_dir/private/api_keys/openai_api_key")
        export OPENAI_API_KEY
    else
        echo "Error: OPENAI_API_KEY not set and no $VLA_Star_dir/private/api_keys/openai_api_key file found." >&2
        exit 1
    fi
fi

HUMAN="$1"

PHASE1_VENV=".realtime_venv"
PHASE2_VENV=".realtime_venv"

# Declare associative array (dictionary)
declare -A PHASE_REQUIREMENTS

PHASE_REQUIREMENTS[.venv]="openai-agents"
PHASE_REQUIREMENTS[.realtime_venv]="openai-agents openai scipy pydub numpy pyaudio websockets"

PHASE1_SCRIPT="embodiment_phase"
PHASE2_SCRIPT="embodiment_phase"

# =====================================
# Helper Functions
# =====================================

activate_venv() {
    local VENV_PATH="$1"
    shift
    local REQUIREMENTS=("$@")

    if [ ! -f "$VLA_Star_dir/$VENV_PATH/bin/activate" ]; then
        echo "🔧 Creating virtual environment at $VLA_Star_dir/$VENV_PATH"

        python3 -m venv "$VLA_Star_dir/$VENV_PATH" || {
            echo "❌ Failed to create venv"
            return 1
        }

        source "$VLA_Star_dir/$VENV_PATH/bin/activate"

        local REQS="${PHASE_REQUIREMENTS[$VENV_PATH]}"

        if [ -z "$REQS" ]; then
            echo "❌ No requirements defined for venv '$VENV_PATH'"
            return 1
        fi

        echo "📦 Installing requirements for '$VENV_PATH': $REQS"
        pip install --upgrade pip || return 1
        pip install $REQS || return 1
    else
        source "$VLA_Star_dir/$VENV_PATH/bin/activate"
    fi
}

run_phase() {
    local PHASE_NAME="$1"
    local VENV_PATH="$2"
    local SCRIPT="$3"

    echo "======================================"
    echo "Starting $PHASE_NAME"
    echo "======================================"

    activate_venv "$VENV_PATH" 
    echo $(pwd)
    ls
    python3 -m "experiments.$SCRIPT" "$HUMAN"
    deactivate || true

    echo "Finished $PHASE_NAME"
    echo ""
}

# =====================================
# Intro
# =====================================

echo "======================================"
echo "        Starting embodied VLA*"
echo "======================================"
echo ""

echo "Installing apt packages"
sudo apt install portaudio19-dev ffmpeg

AGENT_LABEL="${1:-phase1_bot}"
export AGENT_LABEL=$AGENT_LABEL
echo "VLA* name: $AGENT_LABEL"
activate_venv "$PHASE1_VENV"
nohup -- bash -c "source $PHASE1_VENV/bin/activate; export MEDIUM=REALTIME; echo Phase 1 chat terminal; python3 chat.py; exec bash" &
TERMINAL_PID=$!
run_phase "Phase 1" "$PHASE1_VENV" "$PHASE1_SCRIPT"
kill "$TERMINAL_PID"
