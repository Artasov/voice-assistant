import threading

import keyboard
import speech_recognition as sr
import queue
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import association
from services.skills_controller import *
from services.voice import *

# Параметры
min_probability_threshold = 0.1
dictation_mode = False

# Очередь для аудиоданных
q = queue.Queue()


def type_text(text, delay):
    keyboard.write(text, delay)


class VoiceAssistant:
    def __init__(self):
        self.vectorizer = CountVectorizer()
        self.clf = LogisticRegression()
        self.dictation_mode = False
        self.setup()

    def setup(self):
        vectors = self.vectorizer.fit_transform(list(association.data_set.keys()))
        self.clf.fit(vectors, list(association.data_set.values()))
        del association.data_set

    def start_dictation(self):
        self.dictation_mode = True
        print('Диктовка включена')

    def stop_dictation(self):
        self.dictation_mode = False
        print('Диктовка выключена')

    def process_command(self, command):
        if command in {'диктую', 'диктуя'}:
            if not self.dictation_mode:
                self.start_dictation()
            return
        if command in {'стоп', 'stop'}:
            if self.dictation_mode:
                self.stop_dictation()
            return

        if self.dictation_mode:
            type_text(command + ' ', 0.01)
            return

        # Обработка команды с триггером
        trigger = None
        for t in association.TRIGGERS:
            if t in command:
                trigger = t
                break

        if trigger is None:
            return

        command = command.replace(trigger, '')

        text_vector = self.vectorizer.transform([command]).toarray()[0]
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

    def listen_and_process(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)  # настройка уровня шума
            print('Голосовой ассистент запущен...')
            while True:
                print('Ожидание аудио...')
                try:
                    audio_data = recognizer.listen(source, timeout=5)  # установка таймаута в 5 секунд
                    print('Аудио получено, идет распознавание...')
                    command = recognizer.recognize_google(audio_data, language='ru-RU').lower()
                    print('Распознано:', command)
                    self.process_command(command)
                except sr.WaitTimeoutError:
                    print("Таймаут ожидания аудио")
                except sr.UnknownValueError:
                    print("Google Web Speech API не смог распознать аудио")
                except sr.RequestError as e:
                    print("Не удалось запросить результаты у Google Web Speech API; {0}".format(e))

    def run(self):
        threading.Thread(target=self.listen_and_process).start()



if __name__ == '__main__':
    assistant = VoiceAssistant()
    assistant.run()
