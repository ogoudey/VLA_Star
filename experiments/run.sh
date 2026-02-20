
#!/usr/bin/env bash

trap 'echo "Phase interrupted, continuing..."; return 0 2>/dev/null || true' INT

# =====================================
# Configuration
# =====================================

VLA_Star_dir="/home/olin/Robotics/Projects/VLA_Star"
cd $VLA_Star_dir

HUMAN="$1"

PHASE1_VENV=".venv"
PHASE2_VENV=".venv"

# Declare associative array (dictionary)
declare -A PHASE_REQUIREMENTS

PHASE_REQUIREMENTS[.venv]="openai-agents"

PHASE1_SCRIPT="phase1"
PHASE2_SCRIPT="phase2"

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
echo "Hello and welcome to the experiments."
echo "======================================"
echo ""

# =====================================
# Run Phases
# =====================================
gnome-terminal -- bash -c "echo Phase 1 chat terminal; python3 chat.py; exec bash"
run_phase "Phase 1" "$PHASE1_VENV" "$PHASE1_SCRIPT"

gnome-terminal -- bash -c "echo Phase 2 chat terminal; python3 chat.py; exec bash" # source asr_venv/bin/activate; export MEDIUM=AUDIO; 
run_phase "Phase 2" "$PHASE2_VENV" "$PHASE2_SCRIPT"

gnome-terminal -- bash -c "echo Phase 2 chat terminal; source .asr_venv/bin/activate; export MEDIUM=REALTIME; python3 chat.py; exec bash"
/Unity/Hub/Editor/6000.2.2f1/Editor/Unity -projectPath ~/AcroGen/acrophobia_v1 -executeMethod CommandLinePlay.PlayGame
run_phase "Phase 3" "$PHASE3_VENV" "$PHASE3_SCRIPT"


# =====================================
# Outro
# =====================================

echo "======================================"
echo "All phases completed successfully."
echo "Thank you for participating!"
echo "======================================"