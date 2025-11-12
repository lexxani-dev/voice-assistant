import sounddevice as sd
import soundfile as sf
import numpy as np
import queue
import threading
import time
from pathlib import Path

# Import the helper functions from the utils.py file in the same directory
from .utils import ensure_dir, next_recording_path


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
        self.samplerate = sr
        self.channels = channels
        self.dtype = dtype
        self.out_dir = ensure_dir(Path(out_dir))  # Use ensure_dir from utils

        self.recording = False
        self.q = queue.Queue()
        self.stream = None
        self.file = None
        self.filepath = None
        self.drain_thread = None

    def _callback(self, indata, frames, time_info, status):
        """
        Internal callback executed by sounddevice for each incoming audio block.
        """
        if status:
            print(status)
        if self.recording:
            self.q.put(indata.copy())

    def _drain(self):
        """
        Continuously write buffered audio data to disk while recording.

        This method runs in a background thread until a `None` is put in the queue.
        """
        while True:
            try:
                data = self.q.get()
                if data is None:  # Sentinel value to stop the thread
                    break
                self.file.write(data)
            except Exception as e:
                print(f"Error in drain thread: {e}")

    def start(self) -> str:
        """
        Start recording audio from the default input device.

        Returns:
            str: Path to the output WAV file being written.
        """
        if self.recording:
            print("Already recording.")
            return ""

        self.filepath = next_recording_path(self.out_dir)  # Use util to get path

        # Open the sound file
        self.file = sf.SoundFile(
            self.filepath,
            mode='x',
            samplerate=self.samplerate,
            channels=self.channels,
            subtype='PCM_16'  # Common for int16
        )

        self.q.queue.clear()  # Clear any old data
        self.recording = True

        # Start the drain thread
        self.drain_thread = threading.Thread(target=self._drain)
        self.drain_thread.start()

        # Start the audio stream
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype=self.dtype,
            callback=self._callback
        )
        self.stream.start()

        return str(self.filepath)

    def stop(self) -> str:
        """
        Stop the recording and close the stream and file writer.

        Returns:
            str: Path to the saved WAV file.
        """
        if not self.recording:
            print("Not recording.")
            return ""

        print("Stopping recording...")
        self.recording = False

        # Stop the audio stream
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Stop the drain thread by sending the sentinel
        if self.drain_thread:
            self.q.put(None)
            self.drain_thread.join()  # Wait for thread to finish
            self.drain_thread = None

        # Close the file
        if self.file:
            self.file.close()
            self.file = None

        print(f"Recording saved to {self.filepath}")
        return str(self.filepath)