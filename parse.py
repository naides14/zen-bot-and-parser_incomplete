from time import sleep
import func_stop

from selenium import webdriver as wd
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait as wdw
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def get_art(keyword,period):    #навигация по дзену, сохранение url найденных статей и передача их на парсинг

    options = Options()
    # options.add_argument("--headless")  # !!ПОТОМ РАСКОММЕНТИРОВАТЬ| чтоб браузер не открывался, закомментировано чтобы видеть как все делается
    options.add_argument("--disable-gpu")  # для стабильности
    options.add_argument("--no-sandbox")  # нужно для Linux

    browser = wd.Chrome(options=options)
    browser.get('https://dzen.ru/')

    matte=1 #<--- не пытаемся нажать на строку поиска до того как откроем ее (неуверенчтоэтовообщенужно)
    try:
        shindekisama = wdw(browser, 15).until(EC.element_to_be_clickable((By.XPATH,"//span[@aria-label='Закрыть']/*[local-name()='svg']")))
        shindekisama.click()   #закрытие окна с предложением установить расширение яндекса
    except TimeoutException: #если оно не всплывет, кто знает
        pass

    o_search = browser.find_element(By.CSS_SELECTOR,'a.dzen-layout--navigation-tab__tabWrapper-3L:nth-child(3) > li:nth-child(1)')
    o_search.click()         #нажатие на поиск по дзену (третья иконка, 'найти' в меню слева)
    matte=0
    if matte==0:
        searchbar = wdw(browser,15).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="search-input"]')))
        searchbar.send_keys(keyword) #вбивание того, что было отправлено боту, в поиск
        searchbar.send_keys(Keys.ENTER)

        art_and_posts=wdw(browser,15).until(EC.presence_of_element_located((By.CSS_SELECTOR,'a.search--base-tab__tab-3s:nth-child(6)')))
        art_and_posts.click() #переход на список статей

        sleep(3) #прогрузка списка статей

    seen_links_list=[]
    while func_stop.running==1:
        print('Страница обновлена. Команды на остановку не поступало.')
        articles = browser.find_elements(By.CLASS_NAME,"search--card-horizontal-article__cardLink-AC")

        new_links_list=[]

        for i in articles:
            link=(str(i.get_attribute('href'))[0:34])
            if link not in seen_links_list:
                seen_links_list.append(link)
                new_links_list.append(link)
                                                #сначала считываем и отправляем на парсинг статьи, которые выдало по запросу
                                                #затем через заданный период перезагружаем страницу и                                         #
                                                #смотрим, появились ли новые статьи, добавляем их в список
        count=0                                 #просмотренных и отправляем на парсинг. до бесконечности
        for i in new_links_list:
            print(i)
            count+=1
            parsee(i)

        if len(new_links_list)==count:
            sleep(int(period))
            browser.refresh()
        continue
    browser.quit() #когда боту отправляется 'остановить'
    return None


def parsee(url):
    options = Options()
    #options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    browser = wd.Chrome(options=options)
    browser.get(url)

    #время на прогрузку элементов страницы
    sleep(3)

    soup=BeautifulSoup(browser.page_source,"lxml")

    tags=['p','h2','h3','ul','ol','blockquote'] #считываем весь текст статьи
    bodies=soup.find_all(tags)

    for p in bodies:
        if p.find(class_='content--article-navigation__listItemText-3y'): #убираем оглавления статей
            bodies.remove(p)

    with open('article.json','w',encoding='utf-8') as f:   #записываем статью в json
        f.write(f'{soup.title.string}\n\n\n')
        for parag in bodies[1:]:
            if 'Рекламу можно отключить' not in parag.get_text() and 'Дзен Про' not in parag.get_text() and 'Дзен без рекламы' not in parag.get_text():
                f.write(f'{parag.get_text()}\n\n')
        f.write(f'Ссылка на статью: {url}\n')
        f.write('-'*100)

    browser.quit()
    # дальше - текст файла в ии, отформатированный выход ии - вернуть в бота, и так статьи по очереди
    return None
