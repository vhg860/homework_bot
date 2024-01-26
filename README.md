# Проект Telegram Bot for Homework Status Checking on Yandex.Practicum 

## Описание проекта 
 
В данном проекте создан Telegram-бот, который взаимодействует с API сервиса Практикум.Домашка и предоставляет информацию о статусе домашней работы: находится ли она в ревью, проверена ли, и если проверена, то принял ли её ревьюер или отправил на доработку.
 
## Возможности бота: 
 
1. Раз в 10 минут опрашивает API сервиса Практикум.Домашка для проверки статуса отправленной на ревью домашней работы;
2. При обновлении статуса анализирует ответ API и отправляет уведомление в Telegram;
3. Логирует свою работу и сообщает о важных проблемах через сообщение в Telegram.

## Технологии:
Python 3.9

## Запуск проекта в dev-режиме:

1. Установите и активируйте виртуальное окружение.
2. Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
3. В папке с файлом homework.py выполните команду:
```
python homework.py
```
### Автор 
[Дмитрий](https://github.com/vhg860)
