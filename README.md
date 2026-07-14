## Changing the VLANet data for VLA* agents on a given host
```
gedit ~/.vla_stars.jsonl
python3 -m host.vlanet_utility # pushes changes to the VLANet
```

The `~/.vla_stars.jsonl` file contains info to be displayed on the VLANet for various accessible agents on the host.
```
{
    "name": ... # the name of the agent, intended to be just a name...
    "status": ... # something that describes the status of the agent
    "message": ... # an introductory message to introduce the user to the agent, give usage advice, etc.
}
```

## Broadcasting VLA*s on LAN
```
./activation/host/broadcast_manifest.sh  # Makes all agents listed in ~/.vla_stars.jsonl available in the LAN (run this when it goes down...)
```

To connect to a VLA* agent through this mechanism, you must get on the Wifi, and use an Activator (either Android or Desktop).

## Creating VLA* agents
Currently there are two "create" scripts for two types of VLA*s:
```
python3 -m create_scripts.create_vla_star <name>
python3 -m create_scripts.create_game_role <name>
```

The generic `create_vla_star` creates a sort of "gatekeeper" for a particular game (the game set on `olimn.com` actually).

The `create_game_role` submodule currently creates a very particular agent for the game currently set above.
