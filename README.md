# LinusTrinus

TrinusVR screen streaming server for Linux

## Available modes
#### Devices
- Mouse
- Steamvr
#### Screen capture
- ffmpeg

## Dependencies

* Python3 / Pypy3
* ffmpeg
* xwininfo (to capture vr window)
* TrinusVR android client (tested on 2.2.1)
* Docker (for compiling driver)
* Steam
* SteamVR (launched at least once prior to that)

## Installing driver
* Run `make` in this directory 

or ...

* Run `./docker_make.sh` in `driver` subdirectory

## Running

1. Start the TrinusVR Android client and configure it.
2. Press the start button in the TrinusVR Android client.
3. Open SteamVR
4. Run LinuxTrinus: `python3 main.py`

## Notes to current driver implementation
Simply put, it doesnt handle exiting from SteamVR properly. 
You need to kill it manually, so this repository provides `kill_vr.sh` script to help with that.

## Thanks
* [Archlinux OpenVR Package maintainers](https://github.com/archlinux/svntogit-community/tree/packages/openvr/trunk) - for PKGBUILD used to make Dockerfile openvr compilation
* [MyrikLD](https://github.com/MyrikLD/LinusTrinus) & [ben-romer](https://github.com/ben-romer/LinusTrinus) - for good starting point on making this possible
* [r57zone](https://github.com/r57zone/OpenVR-OpenTrack) - for good example
* [TrinusVR team](https://www.trinusvirtualreality.com/) - for android client
