import requests
import vk_api
import func_stop
import threading
from time import sleep

from parse import parsee, get_art

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor



keyboard1 = VkKeyboard(inline=True)
keyboard1.add_button('Конкретная статья', color=VkKeyboardColor.SECONDARY)
keyboard1.add_button('Поиск и анализ статей по ключевому слову', color=VkKeyboardColor.POSITIVE)

keyboard_stop = VkKeyboard(inline=True)
keyboard_stop.add_button('Остановить', color=VkKeyboardColor.NEGATIVE)

keyboard_cancel = VkKeyboard(inline=True)
keyboard_cancel.add_button('Отмена', color=VkKeyboardColor.NEGATIVE)

def kbsender(id, text):
    vk.messages.send(user_id=id, message=text, random_id=0,keyboard=keyboard1.get_keyboard()) #клавиатура с выбором режима работы
def kbsender2(id,text):
    vk.messages.send(user_id=id, message=text, random_id=0, keyboard=keyboard_stop.get_keyboard())  #c кнопкой 'остановить'
def kbsender3(id,text):
    vk.messages.send(user_id=id, message=text, random_id=0, keyboard=keyboard_cancel.get_keyboard()) #c кнопкой 'отмена'
def sender(id,text):
    vk.messages.send(user_id=id, message=text, random_id=0)

def validurl(url):
    if not url.startswith('http'):
        url=f'https://{url}'
    try:
        response = requests.get(url,timeout=5,allow_redirects=True)
        return text[0:18]=='https://dzen.ru/a/' and response.status_code==200 and len(text)==34
    except requests.exceptions.RequestException:
        return False

def is_int(strinng):
    try:
        int(strinng)
        return True
    except ValueError:
        return False

def default_mesg(id):
    kbsender(id,'Проверка новостей - Выберите режим работы')


token='vk1.a.CXscrmc7oXKaXUefHN0XsW7sgrYDl0gKJTV8LKhZs5_PrjAtmAViAGeU_iNQsF84nUhHQzwABmYR0dFIZF9em6RlgvplHdOcV8BVDPSrUUXc4mOnJTOSGyJtb3mS4xzWfaUpTV_H47vKPz_kTh-6WivZKGu4S_aTRHJmk8BpqruHtDUH0m4bbYe1aY2kY8q8c5I-OGDuXOAL1PytOrEr4g'
session=vk_api.VkApi(token = token)
vk = session.get_api()
longpoll = VkBotLongPoll(session,'238962391')

state='' #4 меняющихся состояния: для одной статьи, для ввода запроса и периодичности при нескольких статьях, и для остановки мониторинга

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:    #обработка сообщений и запуск функций в зависимости от действий пользователя
        msg = event.object.message
        user_id = msg['from_id']
        text = msg['text']
        match state:
            case 'one':
                if text=='Отмена':
                    state=''
                    default_mesg(user_id)
                    continue
                elif validurl(text):
                    sender(user_id, 'URL корректен, начинаю анализ...')
                    parsee(text)
                    state=''
                else:
                    kbsender(user_id, 'Ошибка\nURL некорректен, либо ведет не на Дзен, либо такой статьи не существует! Попробуйте еще раз')
                    state='singleerror'

            case 'many':
                if text=='Отмена':
                    state=''
                    default_mesg(user_id)
                    continue
                else:
                    kwords=text
                    kbsender3(user_id,'Введите периодичность, с которой будет обновляться список статей на Дзене для поиска новых (в секундах). Низкие значения не рекомендуются')
                    state='many2'
                    continue

            case 'many2':
                if is_int(text):
                    prd=text
                    func_stop.running = 1
                    thread = threading.Thread(target=get_art, args=(kwords, prd),daemon=True) #запуск функции get_art внутри потока
                    thread.start() #thread чтобы бот отвечал на сообщения пока функция работает
                    state = 'sutoppu'
                    kbsender2(user_id, 'Анализ найденных и мониторинг новых статей...')


                elif text=='Отмена':
                    state=''
                    default_mesg(user_id)
                    continue
                else:
                    kbsender3(user_id,'Нужно ввести число!')
                    continue

            case 'sutoppu':
                if text=='Остановить':
                    func_stop.running = 0
                    sender(user_id, 'Мониторинг останавливается...')
                    while thread.is_alive():  # проверяем закончился ли поток и функция перед тем как позволять пользователю делать что-то
                        sleep(5)
                    default_mesg(user_id)
                    state = ''
                    continue
                else:
                    kbsender2(user_id,'Сначала остановите мониторинг!')
                    continue

            case _:
                if text == 'Начать':
                    default_mesg(user_id)
                    state = ''

                elif text == 'Конкретная статья':
                    kbsender3(user_id, 'Отправьте URL статьи на Дзене')
                    state = 'one'
                    continue

                elif text == 'Поиск и анализ статей по ключевому слову':
                    kbsender3(user_id, 'Введите ключевые слова/запрос, по которому будет выполняться поиск и анализ статей')
                    state = 'many'
                    continue

                elif state != 'singleerror':
                    kbsender(user_id, 'Пожалуйста, используйте встроенную клавиатуру, пока от вас не потребуется ручной ввод')
                    continue













