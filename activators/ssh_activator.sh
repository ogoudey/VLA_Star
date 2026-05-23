#!/usr/bin/env bash

OS_TYPE=$(uname -s)

ENVIRONMENT="linux"

PACKAGE_MANAGER="apt"

ARCH=$(uname -m)

case "$ENVIRONMENT" in
    linux)
        echo "Running on Ubuntu/Debian"
        echo "Installing apt packages"
        apt install avahi-utils

        SERVICE="_bed._tcp"
        echo "Looking for _bed._tcp service..."
        while true; do
            FOUND=$(avahi-browse -rt "$SERVICE" 2>/dev/null | awk '
                /hostname = \[/ {
                    line = $0
                    sub(/.*\[/,"",line)
                    sub(/\].*/,"",line)
                    hostname=line
                }
                /txt = \[.*username=/ {
                    line = $0
                    sub(/.*username=/,"",line)
                    sub(/"].*/,"",line)
                    username=line
                }
                hostname && username { print username " " hostname; exit }
            ')

            if [ -n "$FOUND" ]; then
                NAME=$(echo "$FOUND" | awk '{print $1}')
                VLA_STAR_HOST=$(echo "$FOUND" | awk '{print $2}')
                echo "Found embodied VLA* at $NAME@$VLA_STAR_HOST"
                break
            fi

            sleep 1
        done
        ;;
    *)
        echo "Unknown OS"
        ;;
esac

#ssh "$NAME@$VLA_STAR_HOST" 'bash -l -c "echo $OPENAI_API_KEY"; ./VLA_Star/experiments/run_embodied.sh;'
ssh -t "$NAME@$VLA_STAR_HOST" \
"export OPENAI_API_KEY=$OPENAI_API_KEY; \
select VLA_STAR in \$(./VLA_Star/host/activator_targets/manifest_consultant.sh); do [ -n \"\$VLA_STAR\" ] && break; done; \
./VLA_Star/instantiate_scripts/instantiate_minimal_vla_star_given_a_name.sh \$VLA_STAR"
