# ETS2 Autopilot (WIP)

## About

A program to automate driving in SCS Software's Euro Truck Simulator 2.

This mainly relies on the HUD GPS with an active route to determine the road ahead, to save effort and computation that's normally required to infer the lanes from the main view. This also allows the program to negogiate more complex situations like turns and intersections, and ideally navigate from end-to-end with no interventions.

## Development Status

- [x] obtain a mask/outline of the route from the GPS
  - uses a simple binary thresholding of the GPS HUD from the bottom right corner (and thus won't work on right-hand drive trucks, where the GPS is on the opposite corner)
  - it also gets confused by icons that show up on the map, e.g. highway labels, town names, company logos and most importantly the player icon
    - because of this we use a Steam workshop mod to hide the player icon: [Player Map icon gone by Wolfpig](https://steamcommunity.com/sharedfiles/filedetails/?id=1210820173)
    - later on we will remove this handicap and adapt the image processing to handle the player icon being in the way
- [x] infer centreline of the route
  - our algorithm gets tripped up by a lot of edge cases (mainly crossovers and roundabouts)
- [x] obtain telemetry data from the game via SCS Telemetry
  - implemented in [ets2_telemetry](ets2_telemetry) with only necessary values fetch, but we may eventually grab the full set of data available.
- [x] calculate steering angle required
  - currently implements a Pure Pursuit Controller with a fixed look-ahead distance
  - we are experimenting with different control systems to 
- [ ] calculate max speed through route ahead
- [x] send input (steering/throttle/brake) to the game
  - uses keyboard throttle + mouse steering (at default 0.40/0.00 sensitivity) to control the truck

## Requirements

- Windows 10 (untested on Win11)
- Euro Truck Simulator 2 (in a 1920x1080 window and with a left-hand drive truck)
- Python 3.11.4

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
   (Add documentation to explain the package;)

## Contributing

TBD

## Known bugs

TBD

## License

TBD
