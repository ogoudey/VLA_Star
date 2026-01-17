## Recording VLA Training Datasets with Kinova

### Unity
- Make sure all gear is turned on. VIVE Wireless is on. SteamVR is on. Headset plugged in to the battery. Controller on. Recommended to put the controller on the tall blue rolly chair.
- Open Kinova_Teleop Unity project and Kinova_Teleop scene.
- Press Play.

### Ubuntu
- Make sure Kinova is on, plugged in via Ethernet, and the network settings are configured (IPv4 > Manual > Address 192.168.1.12 > Netmask 255.255.255.0.
- Run `conda activate lerobot`
- Open `VLA_Star/` (In `KinovaVLA`) and run `python3 main.py`, which should be configured to make the Kinova recording interaction.

### And Repeat
0. Put controller back on chair (safe position).
1. Press Play (^P) on Unity
2. `python3 main.py` on Ubuntu

### Note
- If running `KinovaVLA` on a new machine, run `hostname -I` and provide the correct IP address to the Unity computer.
- If running Unity on a new machine (unlikely), run `ipconfig` and provide the IP to `KinovaVLA/lerobot/src/lerobot/teleoperators/unity/unity.py`'s "VR Computer"
#### Controls
- **D-pad**: (big circle on the controller) Quit/No
- **Select**: (the button above the D-pad) Go/Yes
- The status display on the Unity GUI walks the demonstrator through the process.

