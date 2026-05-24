# =============== Orient ================== #

echo "VLA* path env variable: $VLA_STAR_PATH"
if [ -n "$VLA_STAR_PATH" ]; then
    VLA_Star_dir="$VLA_STAR_PATH"
else
    echo "Choosing default VLA_Star path"
    VLA_Star_dir="$HOME/VLA_Star"
fi

cd $VLA_Star_dir

# ============ Get API Keys ================ #
# For OpenAI and Olimn

if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f "$VLA_Star_dir/private/api_keys/openai_api_key" ]; then
        echo "Getting OPENAI_API_KEY FROM $VLA_Star_dir/private/api_keys/openai_api_key"
        OPENAI_API_KEY=$(<"$VLA_Star_dir/private/api_keys/openai_api_key")
        export OPENAI_API_KEY
    else
        echo "Error: OPENAI_API_KEY not set and no $VLA_Star_dir/private/api_keys/openai_api_key file found." >&2
        exit 1
    fi
    else
        echo "Using \$OPENAI_API_KEY"
fi

if [ -z "$OLIMN_API_KEY" ]; then
    if [ -f "$VLA_Star_dir/private/api_keys/olimn_api_key" ]; then
        echo "Getting OLIMN_API_KEY FROM $VLA_Star_dir/private/api_keys/olimn_api_key"
        OLIMN_API_KEY=$(<"$VLA_Star_dir/private/api_keys/olimn_api_key")
        export OLIMN_API_KEY
    else
        echo "Error: OLIMN_API_KEY not set and no $VLA_Star_dir/private/api_keys/olimn_api_key file found." >&2
        exit 1
    fi
    else
        echo "Using \$OLIMN_API_KEY"
fi

# ============ Open Virtual Environment ================ #
# Makes a virtual environment in VLA*/.venv

declare -A PHASE_REQUIREMENTS
PHASE_REQUIREMENTS[.venv]="openai-agents setproctitle pickle"

VENV_PATH=".venv"

if [ ! -f "$VLA_Star_dir/$VENV_PATH/bin/activate" ]; then
    echo "🔧 Creating virtual environment at $VLA_Star_dir/$VENV_PATH"

    python3 -m venv "$VLA_Star_dir/$VENV_PATH" || {
        echo "❌ Failed to create venv"
        return 1
    }

    source "$VLA_Star_dir/$VENV_PATH/bin/activate"

    REQS="${PHASE_REQUIREMENTS[$VENV_PATH]}"

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

# ============ Instantiate ================ #
# Runs Fred (or any agent). This script is fit to these arguments.


NAME="${1:-Fred}"
CHAT_PORT="${2:-5001}"


DISPLAY=:1 gnome-terminal -- bash -c "source $VENV_PATH/bin/activate; export OPENAI_API_KEY=$OPENAI_API_KEY; python3 -m extraneous.modules.chat $CHAT_PORT; exec bash" &

python3 -m "instantiate_scripts.instantiate_minimal_vla_star_given_a_name" "$NAME" "$CHAT_PORT"
deactivate || true

echo "Finished running $NAME"


# ============ (Re-up Host's Advertisement over LAN) ================ #

./host/declare_this_host.sh
