import os
import aiohttp
from aiogram import Dispatcher, Bot, types
from aiogram.filters import Command
from aiogram.types import Message, ContentType, Sticker, User, StickerSet
from aiogram import F
from convert import convert_ogg_to_flac, convert_video_note_to_flac

API_TOKEN: str = os.getenv('hu_do_bot')

bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher()


# Этот хэндлер будет срабатывать на команду "/start"
async def process_start_command(message: Message):
    await message.answer(f'Привет!\nЭтот бот для тебя, {message.from_user.first_name}! '
                         f'\U00002763\nНапиши мне что-нибудь')


# Этот хэндлер будет срабатывать на команду "/help"
async def process_help_command(message: Message):
    await message.answer('На текстовое сообщение я отвечу тем же текстом.\nЕсли перешлёшь мне голосовое или кружочек'
                         ' - я переведу их в текст 👍')


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"
async def send_echo(message: Message):
    if message.text is not None:
        await message.answer(text=f'Все говорят {message.text}.\nА ты купи слона \U0001F418')
        sticker_set: StickerSet = await bot.get_sticker_set(name='WildElephant')
        print(f'Ответ на текст')
        await message.answer_sticker(sticker_set.stickers[11].file_id)
    else:
        await message.answer(text=f'{message.from_user.first_name}, тут наши полномочия - всё...\nокончены 😢'
                                  f'\nЯ для этого не предназначен 🙄')
        sticker_set: StickerSet = await bot.get_sticker_set(name='WildElephant')
        print(f'Ответ на текст')
        await message.answer_sticker(sticker_set.stickers[-8].file_id)


# Этот хэндлер будет срабатывать на отправку боту фото
async def send_photo_echo(message: Message):
    print('Ответ на фото')
    sticker_set: StickerSet = await bot.get_sticker_set(name='WildElephant')
    await message.answer(text=f'Красивое 🤩')
    await message.answer_sticker(sticker_set.stickers[7].file_id)


async def send_animation_echo(message: Message):
    print('Ответ на гифку')
    sticker_set: StickerSet = await bot.get_sticker_set(name='WildElephant')
    await message.answer(text=f'Мне нравится твоя гифка 😊')
    await message.answer_sticker(sticker_set.stickers[-4].file_id)


async def send_sticker_echo(message: Message):
    await message.answer(text=f'Все говорят {message.sticker.emoji}.\nА ты купи слона \U0001F418')
    sticker_set: StickerSet = await bot.get_sticker_set(name='WildElephant')
    print(f'Ответ на стикер \n')
    await message.answer_sticker(sticker_set.stickers[11].file_id)


async def speach_recognition(message: Message):
    if message.voice:
        # Получаем информацию о файле голосового сообщения
        voice_file = message.voice.file_id
        voice_path = f'voice_{message.message_id}.ogg'  # Задайте путь и имя файла для сохранения

        # Загружаем файл голосового сообщения
        file_info = await bot.get_file(voice_file)

        # Получаем содержимое файла
        voice_data = await bot.download_file(file_info.file_path)

        # Сохраняем содержимое файла на диск
        with open(voice_path, 'wb') as f:
            f.write(voice_data.read())

        print(f"Голосовое сообщение сохранено как {voice_path}")
        await message.answer('Секундочку...')
        text = convert_ogg_to_flac(voice_path)
        await message.answer(text)


async def video_to_text(message: Message):
    await message.answer('Это видео')
    if message.video_note:
        # Получаем информацию о файле видео-заметки
        file_info = await bot.get_file(message.video_note.file_id)

        # Формируем URL-адрес для скачивания видео-заметки
        video_note_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"

        async with aiohttp.ClientSession() as session:
            async with session.get(video_note_url) as response:
                response.raise_for_status()

                # Сохраняем видео-заметку на диск
                video_note_path = f'video_note_{message.video_note.file_unique_id}.mp4'
                with open(video_note_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)

        print("Видео-заметка сохранена как video_note.mp4")
        await message.answer('Секундочку...')
        text = convert_video_note_to_flac(video_note_path)
        await message.answer(text)
        os.remove(video_note_path)
        os.remove('audio.flac')


# Регистрация хендлеров
dp.message.register(process_start_command, Command(commands='start'))
dp.message.register(process_help_command, Command(commands='help'))
dp.message.register(send_photo_echo, F.photo)
dp.message.register(send_sticker_echo, F.sticker)
dp.message.register(speach_recognition, F.voice)
dp.message.register(video_to_text, F.video_note)
dp.message.register(send_animation_echo, F.animation)
dp.message.register(send_echo)

if __name__ == '__main__':
    dp.run_polling(bot)
