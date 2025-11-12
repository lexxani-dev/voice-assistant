# audio_io/recorder.py

import queue
import threading
import datetime
import pathlib

from audio_io import utils

import sounddevice as sd
import soundfile as sf
import numpy as np

class Recorder:
    """Handles microphone recording and saving audio to WAV files."""

    def __init__(self, sr: int = 16000, channels: int = 1, dtype: str = 'int16', out_dir: str = "recordings"):
        """
        Initialize the recorder.

        Args:
            sr (int): Sampling rate in Hz.
            channels (int): Number of audio channels (1 = mono, 2 = stereo).
            dtype (str): Sample data type, e.g., 'int16'.
            out_dir (str): Directory where recordings will be saved.
        """
        self.sr = sr
        self.channels = channels
        self.dtype = dtype
        self.out_dir = utils.ensure_dir(out_dir) # creates a Path object

        self.q = queue.Queue()
        self.q.maxsize(16)
        self._lock = threading.Lock()
        self._active = False
        self._writer = None
        self.stream = None
        self.current_path = None

    def _callback(self, indata, frames, time_info, status):
        """
        Internal callback executed by sounddevice for each incoming audio block.

        Args:
            indata (numpy.ndarray): The recorded audio data block.
            frames (int): Number of frames in this block.
            time_info (dict): Timing information.
            status (sounddevice.CallbackFlags): Indicates under/overflow or other warnings.
        """
        if status:
            print(status)
        if self.q.full():
            return
        self.q.put_nowait(indata.copy())

    def start(self) -> str:
        """
        Start recording audio from the default input device.

        Returns:
            str: Path to the output WAV file being written.
        """
        with self._lock:
            if self._active == True:
                return str(self.current_path)
            
            # Create new Path object for current recording
            self.current_path = utils.next_recording_path(self.out_dir)

            # Creater writer (SoundFile) object
            self.writer = sf.SoundFile(file=str(self.current_path), mode='w',
                                  samplerate=self.sr, channels=self.channels,
                                  subtype="PCM_16")

            # Empty Queue (non-blocking)
            while not self.q.empty():
                self.q.get_nowait

            # Create input-stream object
            self.stream = sd.InputStream(samplerate=self.sr, channels=self.channels, 
                                         dtype=self.dtype)


    def _drain(self):
        """
        Continuously write buffered audio data to disk while recording.

        This method runs in a background thread until `stop()` is called.
        """
        pass

    def stop(self) -> str:
        """
        Stop the recording and close the stream and file writer.

        Returns:
            str: Path to the saved WAV file.
        """
        pass