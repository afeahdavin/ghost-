import sounddevice as sd
from scipy.io.wavfile import write, read

print("\n--- Available Microphones ---")
devices = sd.query_devices()
input_devices = []

for i, dev in enumerate(devices):
    if dev['max_input_channels'] > 0:
        print(f"[{i}] {dev['name']}")
        input_devices.append(i)

try:
    choice = int(input("\nType the number of the mic you want to test, then press Enter: "))
    if choice not in input_devices:
        print("Invalid choice. Defaulting to system default.")
        choice = None
except ValueError:
    print("Not a number. Defaulting to system default.")
    choice = None

fs = int(sd.query_devices(choice, 'input')['default_samplerate'])
seconds = 4

print(f"\nRecording for {seconds} seconds using device [{choice}]... SPEAK NOW!")
try:
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, device=choice)
    sd.wait() # Wait until recording is finished
    print("Recording finished. Saving...")
    write('test_mic.wav', fs, recording)
    
    print("Playing back recording... (Listen!)")
    # Read the file back and play it
    fs_read, data = read('test_mic.wav')
    sd.play(data, fs_read)
    sd.wait()
    print("Playback finished.")
    
    print("\nDid you hear yourself clearly?")
    print(f"If yes, the correct mic number is: {choice}")
    print("If it was silent or static, run the script again and try a different number.")
    
except Exception as e:
    print(f"\nError: {e}")