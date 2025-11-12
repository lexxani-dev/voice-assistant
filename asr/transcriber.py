import whisper
import os


class Transcriber:
    """
    A simple wrapper for the OpenAI Whisper model.
    """

    def __init__(self, model_name: str = "base"):
        """
        Loads the Whisper model.

        Args:
            model_name (str): The name of the model to use
                              (e.g., "tiny", "base", "small", "medium").
                              "base" is a good starting point.
        """
        print(f"Loading Whisper model '{model_name}'...")
        self.model = whisper.load_model(model_name)
        print("Whisper model loaded.")

    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribes the given audio file.

        Args:
            audio_file_path (str): The path to the WAV file to transcribe.

        Returns:
            str: The recognized text.
        """
        if not os.path.exists(audio_file_path):
            return f"Error: Audio file not found at {audio_file_path}"

        try:
            result = self.model.transcribe(audio_file_path)
            return result["text"]
        except Exception as e:
            print(f"An error occurred during transcription: {e}")
            if "ffmpeg" in str(e).lower():
                print("\n---")
                print("ERROR: 'ffmpeg' not found.")
                print("Please install ffmpeg on your system to process audio.")
                print("Windows: winget install ffmpeg")
                print("Mac: brew install ffmpeg")
                print("Linux: sudo apt-get install ffmpeg")
                print("---\n")
            return ""