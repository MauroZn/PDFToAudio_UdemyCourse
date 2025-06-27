import requests
import fitz
import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
import threading
import time

# ElevenLabs API config
API_KEY = "sk_6723b3d5042916e186f3fe3f349506fb3c1476ab5221f738"
VOICE_ID = "9BWtsMINqrJLrRacOk9x"
MODEL_ID = "eleven_multilingual_v2"
OUTPUT_FORMAT = "mp3_44100_128"

API_BASE = "https://api.elevenlabs.io"
ENDPOINT = f"/v1/text-to-speech/{VOICE_ID}"
params = f"?output_format={OUTPUT_FORMAT}"
API_URL = API_BASE + ENDPOINT + params

doc = None
audio_file = "output.mp3"
pygame.mixer.init()
playback_thread = None
is_playing = False

def import_file():
    global doc
    file_path = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        doc = fitz.open(file_path)
        print(f"Loaded file: {file_path}")

def text_to_speech():
    global doc, audio_file
    if doc is None:
        print("No document loaded. Please upload a PDF first.")
        return

    text = ""
    for page in doc:
        text += page.get_text()

    if not text.strip():
        print("No text found in the PDF.")
        return

    response = requests.post(
        API_URL,
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": text,
            "model_id": MODEL_ID
        },
    )

    if response.ok:
        with open(audio_file, "wb") as f:
            f.write(response.content)
        print("Audio generated and saved as output.mp3")

        playButton.config(state=tk.NORMAL)
        stopButton.config(state=tk.NORMAL)
        downloadButton.config(state=tk.NORMAL)

        update_duration()
    else:
        print("Error:", response.status_code, response.text)

def update_duration():
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    pygame.mixer.music.pause()  # Just to get length
    length = pygame.mixer.Sound(audio_file).get_length()
    progressBar.config(to=int(length))
    progressBar.set(0)
    pygame.mixer.music.stop()

def play_audio():
    global is_playing, playback_thread
    if os.path.exists(audio_file):
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        is_playing = True

        playback_thread = threading.Thread(target=update_progress_bar)
        playback_thread.daemon = True
        playback_thread.start()
    else:
        print("Audio file not found.")

def stop_audio():
    global is_playing
    pygame.mixer.music.stop()
    is_playing = False
    progressBar.set(0)

def update_progress_bar():
    while is_playing and pygame.mixer.music.get_busy():
        pos = pygame.mixer.music.get_pos() / 1000  # convert to seconds
        progressBar.set(pos)
        time.sleep(0.5)

def download_audio_file():
    if os.path.exists(audio_file):
        save_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])
        if save_path:
            with open(audio_file, "rb") as src, open(save_path, "wb") as dst:
                dst.write(src.read())
            print(f"Audio saved as {save_path}")
    else:
        print("No audio to download.")



if __name__ == "__main__":
    window = tk.Tk()
    window.title("PDF Text To Speech")
    window.minsize(600, 320)

    top_frame = tk.Frame(window)
    top_frame.pack(pady=10)

    uploadButton = tk.Button(top_frame, text="Upload PDF", command=import_file)
    uploadButton.pack(side=tk.TOP, padx=5, pady=5)

    convertButton = tk.Button(top_frame, text="Convert to Speech", command=text_to_speech)
    convertButton.pack(side=tk.BOTTOM, padx=5, pady=5)

    center_frame = tk.Frame(window)
    center_frame.pack(pady=10)

    playButton = tk.Button(center_frame, text="▶", width=2, font=("Arial", 12), command=play_audio, state=tk.DISABLED)
    playButton.pack(side=tk.LEFT, padx=5)

    stopButton = tk.Button(center_frame, text="⏹", width=2, font=("Arial", 12), command=stop_audio, state=tk.DISABLED)
    stopButton.pack(side=tk.LEFT, padx=5)

    progressBar = ttk.Scale(window, from_=0, to=100, orient="horizontal", length=400)
    progressBar.pack()

    downloadButton = tk.Button(window, text="Download Audio", command=download_audio_file, state=tk.DISABLED)
    downloadButton.pack(padx=20, pady=10)

    window.mainloop()
