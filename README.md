# ETS2 Autopilot (WIP)
## About
A program to automate driving in SCS Software's Euro Truck Simulator 2.

This mainly relies on the HUD GPS with an active route to determine the road ahead, to save effort and computation that's normally required to infer the lanes from the main view. This also allows the program to negogiate more complex situations like turns and intersections, and ideally navigate from end-to-end with no interventions.

## Development Status
- [x] obtain a mask/outline of the route from the GPS
- [ ] infer centreline of the route
- [ ] obtain telemetry data from the game via SCS Telemetry
- [ ] calculate steering angle required
  - [ ] calculate max speed through route ahead
- [ ] send input (steering/throttle/brake) to the game

## Requirements

* Windows 10 (untested on Win11)
* Euro Truck Simulator 2 (in a 1920x1080 window and with a left-hand drive truck)
* Python 3.11.4

## Setup/Installation

1. Clone this project to your local desktop.
2. Install Python 3.11.4 - [releases available here.](https://www.python.org/downloads/release/python-3114/)
   - Optionally setup a virtual environment with `venv`
3. Install the required Python packages with:
```
pip install -r requirements.txt
```
4. Install [RenCloud's SCS Telemetry plugin](https://github.com/RenCloud/scs-sdk-plugin#installation).
5. (For Windows users) go to `C:\Users\{YOURUSERNAME}\Documents\Euro Truck Simulator 2\profiles\{some random hexcode}\controls.sii` or `C:\Users\{YOURUSERNAME}\Documents\Euro Truck Simulator 2\steam_profiles\{some random hexcode}\controls.sii` and edit the following lines:
```
config_lines[0]: "device keyboard `di8.keyboard`"
config_lines[1]: "device mouse `fusion.mouse`"
```
to 
```
config_lines[0]: "device keyboard `sys.keyboard`"
config_lines[1]: "device mouse `sys.mouse`"
```
6. Run `main.py` to start the program.

## Contributing
TBD

## Known bugs
TBD

## License
TBD
