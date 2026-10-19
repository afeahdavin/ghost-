import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import pyttsx3
import subprocess
import keyboard
import os

print("Loading local Whisper model...")
model = whisper.load_model("base")

engine = pyttsx3.init()
engine.setProperty('rate', 180)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def record_and_ask():
    print("\n[Listening... speak now]")
    
    # Automatically find the correct sample rate for your mic
    fs = int(sd.query_devices(kind='input')['default_samplerate'])
    seconds = 5
    
    try:
        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
    except Exception as e:
        print(f"Microphone error: {e}")
        return
        
    print("[Processing audio locally...]")
    write('temp.wav', fs, recording)
    
    result = model.transcribe("temp.wav", fp16=False)
    user_text = result['text'].strip()
    print(f"You said: {user_text}")
    
    if not user_text or len(user_text) < 2:
        print("Didn't catch that.")
        return

    print("[Sending to Ghost...]")
    try:
        response = subprocess.run(
            ["opencode", "run", user_text], 
            capture_output=True, 
            text=True,
            cwd=r"C:\ghost"
        )
        
        ghost_reply = response.stdout.strip()
        print(f"Ghost: {ghost_reply}")
        
        if ghost_reply:
            speak(ghost_reply)
        
    except Exception as e:
        print(f"Error calling OpenCode: {e}")

print("Voice system ready. Press 'F8' to talk to Ghost. Press 'Esc' to quit.")
keyboard.add_hotkey('f8', record_and_ask)
keyboard.wait('esc')