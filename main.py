from audio_io.recorder import Recorder
from asr.transcriber import Transcriber
import time
import os


def main():
    """
    Main function to run the speak-to-text pipeline.
    """

    # --- 1. Initialize Components ---
    # This creates the "recordings" directory
    recorder = Recorder(out_dir="recordings")

    # This loads the "base" model. It will download it the first time.
    # This fulfills the "local processing" requirement from your project.
    transcriber = Transcriber(model_name="base")

    print("\n--- Voice Assistant Ready ---")
    print("Press ENTER to start recording. Press ENTER again to stop.")

    try:
        while True:
            # --- 2. Wait for user to start ---
            input("\nPress ENTER to start recording...")

            # --- 3. Start Recording ---
            filepath = recorder.start()
            print(f"Recording... speak now. Press ENTER to stop.")

            # --- 4. Wait for user to stop ---
            input()
            recorder.stop()
            print(f"Recording stopped. File saved to: {filepath}")

            # --- 5. Transcribe the Audio ---
            print("Transcribing audio...")
            text = transcriber.transcribe(filepath)

            # --- 6. Print the Result ---
            print("---------------------------------")
            print(f"RECOGNIZED TEXT: {text}")
            print("---------------------------------")

    except KeyboardInterrupt:
        print("\nExiting...")
        if recorder.recording:
            recorder.stop()


if __name__ == "__main__":
    # This file should be in the root of your project
    # (e.g., at the same level as the 'audio_io' and 'asr' folders)
    # to run it.
    main()
