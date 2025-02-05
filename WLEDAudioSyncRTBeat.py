import pyaudio
import numpy as np
import aubio
import signal
import os
import time
import sys
import math

import argparse


parser = argparse.ArgumentParser()
sp = parser.add_subparsers(dest="command")

beat_parser = sp.add_parser("beat",
                            help="Start beat detection")
beat_parser.add_argument("-s", "--server",
                         help="OSC Server address (multiple can be provided) in format 'IP' 'PORT' 'PATH' 'MODE', "
                              "Mode PLAIN for plain BPM-Value,Mode HALF for half of BPM-Value, "
                              "Mode GMA3 for GrandMA3 Speed masters where 100 percent is for 240BPM. "
                              "  MODE is optional and default to PLAIN"
                              " e.g. 127.0.0.1 12000 /test GMA3",
                         nargs='*',
                         action="append"
                         )
beat_parser.add_argument("-b", "--bufsize",
                         help="Size of audio buffer for beat detection (default: 512)", default=512,
                         type=int)
beat_parser.add_argument("-v", "--verbose",
                         help="Print BPM on beat", action="store_true")
beat_parser.add_argument("-d", "--device",
                         help="Input device index (use list command to see available devices)",
                         default=None, type=int)

list_parser = sp.add_parser("list",
                            help="Print a list of all available audio devices")
args = parser.parse_args()


class BeatPrinter:
    def __init__(self):
        self.state: int = 0
        self.spinner = "¼▚▞▚"

    def print_bpm(self, bpm: float, dbs: float) -> None:
        print(f"{self.spinner[self.state]}\t{bpm:.1f} BPM\t{dbs:.1f} dB")
        self.state = (self.state + 1) % len(self.spinner)


class BeatDetector:
    def __init__(self, buf_size: int):
        self.buf_size: int = buf_size

        # Set up pyaudio and aubio beat detector
        self.audio: pyaudio.PyAudio = pyaudio.PyAudio()
        samplerate: int = 44100

        self.stream: pyaudio.Stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=samplerate,
            input=True,
            frames_per_buffer=self.buf_size,
            stream_callback=self._pyaudio_callback,
            input_device_index=args.device
        )

        fft_size: int = self.buf_size * 2  #

        # tempo detection
        self.tempo: aubio.tempo = aubio.tempo("default", fft_size, self.buf_size, samplerate)

        # print info
        self.spinner: BeatPrinter = BeatPrinter()

    # this one is called every time enough audio data (buf_size) has been read by the stream
    def _pyaudio_callback(self, in_data, frame_count, time_info, status):
        # Interpret a buffer as a 1-dimensional array (aubio do not work with raw data)
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        # true if beat present
        beat = self.tempo(audio_data)

        # if beat detected , calculate BPM and send to OSC
        if beat[0]:
            # volume level in db
            dbs = aubio.db_spl(aubio.fvec(audio_data))
            bpm = self.tempo.get_bpm()
            # recalculate half BPM
            bpmh = bpm / 2
            # recalculate BPM for GrandMA3
            bpmg = math.sqrt(bpm / 240) * 100

            if args.verbose:
                self.spinner.print_bpm(bpm, dbs)


        return None, pyaudio.paContinue  # Tell pyAudio to continue

    def __del__(self):
        self.stream.close()
        self.audio.terminate()
        print('--- Stopped ---')


# find all devices, print info
def list_devices():
    print("Listing all available input devices:\n")
    audio = pyaudio.PyAudio()
    info = audio.get_host_api_info_by_index(0)
    numberofdevices = info.get('deviceCount')

    for i in range(0, numberofdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print(f"[{i}] {audio.get_device_info_by_host_api_device_index(0, i).get('name')}")

    print("\nUse the number in the square brackets as device index")


# main
def main():

    if args.command == "list":
        list_devices()
        return

    if args.command == "beat":

        bd = BeatDetector(args.bufsize)

        # capture ctrl+c to stop gracefully process
        def signal_handler(none, frame):
            bd.stream.stop_stream()
            bd.stream.close()
            bd.audio.terminate()
            print(' ===> Ctrl + C')
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # Audio processing happens in separate thread, so put this thread to sleep
        if os.name == 'nt':  # Windows is not able to pause the main thread :(
            while True:
                time.sleep(1)
        else:
            signal.pause()
    else:
        print('Nothing to do. Use -h for help')


# main run
if __name__ == "__main__":
    main()
