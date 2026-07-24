## Start Scripts
When and why start an agent -- and Who... is starting an agent?

Most agents can be started without anything to do with `start_scripts`. One could, for example, open a browser and go to any familiar frontier website. Those agents, however, are unlocalized and have __no__ spatial extension -- they are __universal__ agents. Agents which are at a place have a Host. A subset of these agents fall in the VLA* architecture, and `start_scripts` are the ways to start (and produce) them.

`start.py` is the python entry point to start a VLA* by using its name. One could use this script on the machine that the VLA* resides. There is another way to start a VLA* and that is with an Activator -- a program that implements an interface to reach a `start_script`. One type of Activator ssh-s into a Host and calls `./activation/targets/activate_vla_star_v1.sh`. This activates the python environment and starts a VLA*.

### Producing a VLA*
Since VLA*s are produced by specifying variables, so far it is one-to-one producer-to-VLA*-type, that is, there are only as many types of VLA*s as there are producers

### Syncing with the VLANet
Another purpose of this project is to make these agents universal. Due to security, it doesn't make sense for all agent `activation` to be universally accessible (would mean dispersing computer passwords). `start.py` will update the VLANet with the status and instructions for interaction with the agent that's been started. This promotes transparency, safety, and communication around agent use. `private_start.py` will keep the fact the agents status private, ignoring the VLANet.