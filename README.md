# ETS2 Autopilot (WIP)

## About

A program to automate driving in SCS Software's Euro Truck Simulator 2.

This mainly relies on the HUD GPS with an active route to determine the road ahead, to save effort and computation that's normally required to infer the lanes from the main view. This also allows the program to negogiate more complex situations like turns and intersections, with the goal to navigate from end-to-end with no interventions.

## Development Status

- [x] obtain a mask/outline of the route from the GPS
  - uses a simple binary thresholding of the GPS HUD from the bottom right corner (and thus won't work on right-hand drive trucks, where the GPS is on the opposite corner)
  - it also gets confused by icons that show up on the map, e.g. highway labels, town names, company logos and most importantly the player icon
    - because of this we made a Steam workshop mod to hide the player icon: [Minimal GPS Truck Icon](https://steamcommunity.com/sharedfiles/filedetails/?id=3023064996)
    - later on we will remove this handicap and adapt the image processing to handle the player icon being in the way
- [x] infer centreline of the route
  - our algorithm gets tripped up by a lot of edge cases (mainly crossovers and roundabouts)
- [x] obtain telemetry data from the game via SCS Telemetry
  - implemented in [ets2_telemetry](ets2_telemetry) with only necessary values fetched, but we may eventually grab the full set of data available.
- [x] calculate steering angle required
  - currently implements a Pure Pursuit Controller with a fixed look-ahead distance
  - we are experimenting with different control systems to find one best suited for this application.
- [ ] calculate max speed through the route ahead
- [x] send input (steering/throttle/brake) to the game
  - uses keyboard throttle + mouse steering (at default 0.40/0.00 sensitivity) to control the truck

## Requirements

- Windows 10 (untested on Win11)
- Euro Truck Simulator 2 (in a 1920x1080 window and with a left-hand drive truck)
- Python 3.11.4

## Getting Started
### Preparing Euro Truck Simulator 2
1. Install [RenCloud's SCS Telemetry plugin](https://github.com/RenCloud/scs-sdk-plugin#installation).
2. (For Windows users) Find the `controls.sii` file corresponding to your save file, located in
   - `C:\Users\{YOURUSERNAME}\Documents\Euro Truck Simulator 2\profiles\{some hexcode}\controls.sii` or
   - `C:\Users\{YOURUSERNAME}\Documents\Euro Truck Simulator 2\steam_profiles\{some hexcode}\controls.sii`

   and edit the following lines:

```
config_lines[0]: "device keyboard `di8.keyboard`"
config_lines[1]: "device mouse `fusion.mouse`"
```

to

```
config_lines[0]: "device keyboard `sys.keyboard`"
config_lines[1]: "device mouse `sys.mouse`"
```
3. Install our icon mod - [Minimal GPS Truck Icon](https://steamcommunity.com/sharedfiles/filedetails/?id=3023064996) - from the Steam Workshop and enable it in-game.
4. In the game, go to Options->Controls and set the control device to Keyboard + Mouse Steering.
5. Set the Steering sensitivity to `0.40` and Steering non-linearity to `0.00`
6. In Options->Graphics, disable Fullscreen mode and set the screen resolution to 1920x1080.
7. Make sure your truck is left-hand drive (so the GPS will show in the bottom-right corner)

### Installing the program
1. Clone the project to your local desktop.
2. Install Python 3.11.4 - [releases available here.](https://www.python.org/downloads/release/python-3114/)
   - Optionally setup a virtual environment with `venv` or a package manager of your preference.
3. Install the required Python packages with:

```
pip install -r requirements.txt
```

### Running the program

1. Launch Euro Truck Simulator 2.
2. Run `main.py` (inside your virtual environment if needed) to start the program.

The program will open three preview windows to show the 1. screenshot area 2. masked route line and 3. warped perspective with centreline overlay. It will auto-steer via mouse input when the following conditions are fulfilled:
- the game is in focus
- the game is unpaused
- the GPS (in-game called the Route Advisor Navigation Page) is visible at the most zoomed-in level
  - press F5 to change the zoom
- there is a destination set (i.e. a red line is visible in the GPS display).
- the truck icon in the GPS display is on top of the red navigation line

To stop the auto-steer, you can break one of these conditions, e.g. alt-tab out of the game, pause the game or hide the GPS by changing the Route Advisor to another page. The last method is the only way to manually steer the truck while the program is running.

## Contributing

Any contributions are welcome. We use [Black](https://github.com/psf/black) to autoformat our code.

### Roadmap

See [Development Status](README.md#Development-Status)

## Known bugs

- The autopilot cannot negogiate self-crossovers visible on the GPS, e.g. left-turns on cloverleaf interchanges and bridges over highways. You will have to disable the autopilot temporarily (see [Running the program](README.md#Running-the-program)).

For more info see [Development Status](README.md#Development-Status)

## License

This project is licensed under the MIT License.
