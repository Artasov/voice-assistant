import os
import webbrowser
import sys
import subprocess

import requests

from services.voice import play_vocalize_text


def browser():
    webbrowser.open('https://www.youtube.com', new=2)


def game():
    '''Нужно разместить путь к exe файлу любого вашего приложения'''
    try:
        subprocess.Popen('C:/Program Files/paint.net/PaintDotNet.exe')
    except:
        play_vocalize_text('Путь к файлу не найден, проверьте, правильный ли он')


def offpc():
    # Эта команда отключает ПК под управлением Windows

    # os.system('shutdown \s')
    print('пк был бы выключен, но команде # в коде мешает;)))')


def weather():
    play_vocalize_text('Я не знаю погоду отстань')


def offBot():
    '''Отключает бота'''
    sys.exit()


def passive():
    '''Функция заглушка при простом диалоге с ботом'''
    pass
