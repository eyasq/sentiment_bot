import os
import sys
import whisper


model = whisper.load_model("turbo")
result=model.transcribe("test_audio/recording.mp3", language="ar")

print(result["text"])

