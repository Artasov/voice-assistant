from copy import copy

import keyboard
import pyautogui
from sklearn.feature_extraction.text import CountVectorizer  # pip install scikit-learn
from sklearn.linear_model import LogisticRegression
import sounddevice as sd  # pip install sounddevice
import vosk  # pip install vosk
from loguru import logger
import json
import queue

import association
from services.skills_controller import *
from services.voice import *

q = queue.Queue()

model = vosk.Model('models/vosk-model-small-ru-0.22')

device = sd.default.device  # <--- по умолчанию
# или -> sd.default.device = 1, 3, python -m sounddevice просмотр
samplerate = int(sd.query_devices(device[0], 'input')['default_samplerate'])  # получаем частоту микрофона

min_probability_threshold = 0.1

dictation_mode = False


def type_text(text, delay):
    keyboard.write(text, delay)


def callback(indata, frames, time, status):
    """add samples to queue from stream"""
    q.put(bytes(indata))


class VoiceAssistant:
    def __init__(self):
        self.models = {
            'ru': vosk.Model('models/vosk-model-small-ru-0.22'),
            'en': vosk.Model('models/vosk-model-small-en-us-0.15')
        }
        self.recognizers = {lang: vosk.KaldiRecognizer(model, samplerate) for lang, model in self.models.items()}
        self.vectorizer = CountVectorizer()
        self.clf = LogisticRegression()
        self.dictation_mode = False
        self.setup()

    def setup(self):
        vectors = self.vectorizer.fit_transform(list(association.data_set.keys()))
        self.clf.fit(vectors, list(association.data_set.values()))
        del association.data_set

    def start_dictation(self):
        play_mp3('sounds/success.mp3')
        self.dictation_mode = True
        logger.info('Диктовка включена.')

    def stop_dictation(self):
        self.dictation_mode = False
        logger.info('Диктовка выключена.')

    def process_command(self, command):
        command_words = command.split()
        trigger_word_index = None

        for i, word in enumerate(command_words):
            if word in {'диктую', 'диктуя', 'диктует'}:
                trigger_word_index = i
                if not self.dictation_mode:
                    self.start_dictation()
                    return

                break
            elif word in {'стоп', 'stop'}:
                if i > 0:
                    text_before_stop = ' '.join(command_words[:i])
                    type_text(text_before_stop + ' ', 0.01)
                if self.dictation_mode:
                    self.stop_dictation()
                return

        if self.dictation_mode:
            type_text(command + ' ', 0.01)
            return

        if trigger_word_index is not None and trigger_word_index < len(command_words) - 1:
            additional_text = ' '.join(command_words[trigger_word_index + 1:])
            type_text(additional_text + ' ', 0.01)

        trigger = None
        for t in association.TRIGGERS:
            if t in command:
                trigger = t
                break

        if trigger is None:
            return

        command = command.replace(trigger, '')

        text_vector: int = self.vectorizer.transform([command]).toarray()[0]
        predicted_probabilities = self.clf.predict_proba([text_vector])[0]
        max_probability_index = predicted_probabilities.argmax()
        max_probability = predicted_probabilities[max_probability_index]

        if max_probability < min_probability_threshold:
            play_vocalize_text('Я нихуя не поняла')
            return

        answer = self.clf.classes_[max_probability_index]
        func_name = answer.split()[0]
        play_vocalize_text(answer.replace(func_name, ''))

        exec(func_name + '()')

    def run(self):
        with sd.RawInputStream(samplerate=samplerate, blocksize=16000, device=device[0], dtype='int16',
                               channels=1, callback=callback) as stream:
            logger.info('Голосовой ассистент запущен...')
            while True:
                data = q.get()
                if self.recognizers['ru'].AcceptWaveform(data):
                    result = json.loads(self.recognizers['ru'].Result())
                    command = result.get('text', '').strip()
                    if command:
                        logger.info(f'{result=}')
                        self.process_command(command)


if __name__ == '__main__':
    logger.add("./logs/" + str(os.path.basename(__file__)).replace('.py', '') + "/{time:YYYY-MM-DD}.log",
               rotation="1 day",
               retention="180 days")
    logger.info(f"Starting... {os.path.basename(__file__)}")
    assistant = VoiceAssistant()
    assistant.run()
