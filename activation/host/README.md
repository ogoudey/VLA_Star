## Host
The manifest is a list of VLA*s produced and stored on this host, by their name. It is located in `~/.vla_stars.jsonl`.

To broadcast the manifest across the local area network (ssh-reachable), run `./broadcast_manifest.sh`. This enables other agents to see which agents are available on this host.

Note that this is different from __syncing__ the manifest with the VLANet. For this, see `/start_scripts/README.md`.