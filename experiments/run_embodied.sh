
#!/usr/bin/env bash

trap 'echo "Phase interrupted, continuing..."; return 0 2>/dev/null || true' INT

# =====================================
# Configuration
# =====================================

VLA_Star_dir="/home/olin/VLA_Star"
cd $VLA_Star_dir

ARGV1="$1"

PHASE1_VENV=".venv"
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

    if [ ! -f "$VENV_PATH/bin/activate" ]; then
        echo "🔧 Creating virtual environment at $VENV_PATH"

        python3 -m venv "$VENV_PATH" || {
            echo "❌ Failed to create venv"
            return 1
        }

        source "$VENV_PATH/bin/activate"

        local REQS="${PHASE_REQUIREMENTS[$VENV_PATH]}"

        if [ -z "$REQS" ]; then
            echo "❌ No requirements defined for venv '$VENV_PATH'"
            return 1
        fi

        echo "📦 Installing requirements for '$VENV_PATH': $REQS"
        pip install --upgrade pip || return 1
        pip install $REQS || return 1
    else
        source "$VENV_PATH/bin/activate"
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
sudo apt install portaudio19-dev

echo $OPENAI_API_KEY
export AGENT_LABEL="phase1_bot"
run_phase "Phase 1" "$PHASE1_VENV" "$PHASE1_SCRIPT"


export AGENT_LABEL="phase2_bot"

activate_venv "$PHASE2_VENV" 
gnome-terminal -- bash -c "source $PHASE2_VENV/bin/activate; export MEDIUM=REALTIME; echo Phase 2 chat terminal; python3 chat.py; exec bash"
run_phase "Phase 2" "$PHASE2_VENV" "$PHASE2_SCRIPT"