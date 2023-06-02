import os
import time
from typing import Any, List, Tuple
import moviepy.editor as mp
import soundfile as sf
import speech_recognition as sr


def recognition(flac):
    r = sr.Recognizer()
    with sr.AudioFile(flac) as source:
        audio = r.record(source)  # Читаем содержимое аудиофайла
        try:
            # Распознаем текст с помощью Google Speech Recognition
            text = r.recognize_google(audio, language='ru-RU')
            print(f"Распознанный текст: {text}")
            return text
        except sr.UnknownValueError:
            text = "Не удалось распознать речь"
            print("Не удалось распознать речь")
            return text
        except sr.RequestError as e:
            text = f"Ошибка сервиса распознавания речи: {e}"
            print(f"Ошибка сервиса распознавания речи: {e}")
            return text


def convert_video_note_to_flac(video_path):
    print('Извлечение аудиодорожки и преобразование во FLAC')
    audio_path = 'audio.flac'

    video = mp.VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path, codec='flac')
    text = recognition(audio_path)
    print("Аудиодорожка извлечена и сохранена как audio.flac")
    video.close()
    return text


def convert_ogg_to_flac(ogg_file):
    flac_file = f'{ogg_file[:-4]}.flac'

    # Загружаем аудиофайл OGG
    ogg_data, sample_rate = sf.read(ogg_file)

    # Записываем аудиофайл FLAC
    sf.write(flac_file, ogg_data, sample_rate, format='FLAC')
    text = recognition(flac_file)
    os.remove(ogg_file)
    os.remove(flac_file)
    return text
