import os

import pyttsx3
from pydub import AudioSegment
from pydub.playback import play

en_voice_id = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0'
ru_voice_id = r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0'

engine = pyttsx3.init()
engine.setProperty('rate', 180)  # скорость речи
engine.setProperty('voice', ru_voice_id)


def play_mp3(path: str):
    if not os.path.exists(path):
        print("Файл не найден")
        return

    if not path.lower().endswith('.mp3'):
        print("Файл не в формате MP3")
        return

    # Загрузить MP3-файл
    audio = AudioSegment.from_mp3(path)

    # Воспроизвести аудио
    play(audio)


def play_vocalize_text(text):
    engine.say(text)
    engine.runAndWait()
