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

        self.q = queue.Queue(maxsize=16)
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
            if self._active:
                return str(self.current_path)
            
            try:
                # Create new Path object for current recording
                self.current_path = utils.next_recording_path(self.out_dir)

                # Creater writer (SoundFile) object
                self._writer = sf.SoundFile(file=str(self.current_path), mode='w',
                                    samplerate=self.sr, channels=self.channels,
                                    subtype="PCM_16")

                # Empty Queue (non-blocking)
                while not self.q.empty():
                    self.q.get_nowait()

                # Create input-stream object
                self.stream = sd.InputStream(samplerate=self.sr, channels=self.channels, 
                                            dtype=self.dtype, callback=self._callback)
                self.stream.start()

                self._active = True
                
                # Start drain-thread to write data from queue into audio file
                self._drain_thread = threading.Thread(target=self._drain, daemon=True)
                self._drain_thread.start()

                return str(self.current_path)

            except Exception as e:
                # Clean up on error case
                self._active = False
                if self.stream:
                    try:
                        self.stream.close()
                    except Exception:
                        pass
                if self._writer:
                    try:
                        self._writer.close()
                    except Exception:
                        pass
                raise e

    def _drain(self):
        """
        Continuously write buffered audio data to disk while recording.
        This method runs in a background thread until `stop()` is called.
        """
        if self._writer is None:
            return
        writer = self._writer

        while self._active:
            try:
                chunk = self.q.get(timeout=0.5)
                writer.write(chunk)
            except Exception:
                pass
            
        # Flush remaining chunks after stop signal
        while True:
            try:
                chunk = self.q.get_nowait()
            except queue.Empty:
                break
            try:
                writer.write(chunk)
            except Exception:
                pass

    def stop(self) -> str:
        """
        Stop the recording and close the stream and file writer.

        Returns:
            str: Path to the saved WAV file.
        """
        with self._lock:
            if not self._active:
                return str(self.current_path)

            self._active = False

            # Wait briefly until drain thread finishes writing remaining chunks
            if getattr(self, "_drain_thread", None) and self._drain_thread.is_alive():
                self._drain_thread.join(timeout=0.5)

            # Stop and close stream
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            # Flush and Close writer
            if self._writer:
                self._writer.flush()
                self._writer.close()
                self._writer = None

            return str(self.current_path)