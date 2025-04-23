# Aurora Beat Detector

This is a simple beat detector built with [aubio](https://github.com/aubio/aubio).
It will detect the beat and BPM on the default audio input.
When the BPM changes, this update is sent to [Aurora Core](https://github.com/gewis/aurora-core) over HTTP(S).

## Prerequisites
- Python 3.11
- A working instance of [Aurora Core](https://github.com/gewis/aurora-core). Within this instance, create a new
integration dedicated for this beat detector. The integration should have access to all endpoints regarding the
real time beat detector (setting the BPM and stopping). Without the correct access rights, the program might crash
due to an HTTP 403!

## Installation
- Create a virtual environment `python -m venv venv`.
- Activate the virtual environment `.\venv\Scripts\activate.bat` or `.\venv\Scripts\activate`.
- Install requirements `pip install -r requirements.txt`. Note that the first time installating `aubio` might fail.
A retry (or manually installing numpy first) should resolve this issue. 

## Usage

```
WLEDAudioSyncRTBeat-{OS} beat|list [-h] -s SERVER_URL -k API_KEY [-b BUFSIZE] [-v] [-d DEVICE]

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        HTTP(S) root address of the Aurora Core instance
  -k API_KEY, --api-key API_KEY
                        API Key of the integration user to authenticate as
  -b BUFSIZE, --bufsize BUFSIZE
                        Size of audio buffer for beat detection (default: 512)
  -v, --verbose         Print BPM on beat / dB
  -d DEVICE, --device DEVICE
                        Input device index (use list command to see available devices)

```

### `-s`/`--server`
The HTTP(S) address pointing to the Aurora core. For local installations, this is probably `http://localhost:3000`.

### `-k`/`api-key`
The API Key used to authenticate with Aurora.

### `-b`/`--bufsize`
Select the size of the buffer used for beat detection.
A larger buffer is more accurate, but also more sluggish.
Refer to the [aubio](https://github.com/aubio/aubio) documentation of the tempo module for more details.
Example: `-b 128`

### `-v`/`--verbose`
Output a handy beat indicator and the current BPM / dB to stdout.

### `-d`/`--device`
Specify the index of input device to be used.
If not provided, the default system input is used.  
Run `WLEDAudioSyncRTBeat list` to get all available devices.


## Example

```
$ WLEDAudioSyncRTBeat beat -s http://localhost:3000 -k ABCD -v
```
This will send all BPM changes to a local installation of Aurora.

## Credits

Thanks to: https://github.com/zak-45/WLEDAudioSyncRTBeat and https://github.com/DrLuke/aubio-beat-osc.
