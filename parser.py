import time
import json
import math
import selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import csv
import os

import bs4
import requests
from lxml import html

import numpy as np
import pandas as pd

class Subject():
    def __init__(self, subject, profiles):
        self.subject = subject
        self.profiles = profiles

    def GetProfiles(self):
        return self.profiles

    def GetSubject(self):
        return self.subject

class Service():
    def __init__(self, service_name, service_cost, service_duration):
        self.service_name = service_name
        self.service_cost = service_cost
        self.service_duration = service_duration

class Profile():
    def __init__(self, fullname, count_rates, total_rate, count_rate_values, service_names, service_prices, service_durations):
        self.fullname = fullname
        self.count_rates = count_rates
        self.total_rate = total_rate
        self.count_rate_values = count_rate_values
        self.service_names = service_names
        self.service_prices = service_prices
        self.service_durations = service_durations

    def GetFullname(self):
        return self.fullname

    def GetCountRates(self):
        return self.count_rates

    def GetTotalRate(self):
        return self.total_rate

    def GetAllRateCountValues(self):
        return self.count_rate_values

    def GetCountRateByMark(self, mark):
        if (mark == 5):
            return self.count_rate_values[0]
        elif (mark == 4):
            return self.count_rate_values[1]
        elif (mark == 3):
            return self.count_rate_values[2]
        elif (mark == 2):
            return self.count_rate_values[3]
        elif (mark == 1):
            return self.count_rate_values[4]

        return 0

    def GetAllServiceNames(self):
        return self.service_names

    def GetAllServicePrices(self):
        return self.service_prices

    def GetAllServiceDurations(self):
        return self.service_durations

    def GetServiceNameByIndex(self, index):
        return self.service_names[index]

    def GetServicePriceByIndex(self, index):
        return self.service_prices[index]

    def GetServiceDurationByIndex(self, index):
        return self.service_durations[index]

    def GetPriceAndDurationByIndex(self, index):
        return self.service_prices[index] + "/" + self.service_durations[index]

    def GetAllPricesAndDurations(self):
        services_output = []
        for index in range(len(self.service_prices)):
            services_output.append(self.service_prices[index] + "/" + self.service_durations[index])

        return services_output

    def GetFullServiceData(self):
        services_output = []
        for index in range(len(self.service_prices)):
            services_output.append(self.service_names[index] + "/" + self.service_prices[index] + "/" + self.service_durations[index])

        return services_output

    def GetServiceCostByServiceName(self, service_name):
        service_name_idx = 0
        for name in self.GetAllServiceNames():
            if name.strip().lower() == service_name:
                break
            service_name_idx += 1

        service_cost = self.GetServicePriceByIndex(service_name_idx)

        return service_cost

SCROLL_PAUSE_TIME = 2

# df_results = pd.DataFrame(columns=['Fullname', 'Rate', 'SubjectName'])
# res = df_results.append({'Fullname' : 'ФИО' , 'Rate' : 5.5, 'SubjectName': 'Математика'} , ignore_index=True)

def GetNormalizedPriceAndDuration(source):
    prerared = source.replace(u'\xa0', u' ').replace(u'\u202f', u'').strip()
    dataForSplit = prerared.replace(' ₽ ', '').replace(' мин.', '').replace('/ ', '/')
    splittedData = dataForSplit.split('/')

    try:
        if (dataForSplit == 'по договорённости'):
            return 'по договорённости', 'по договорённости'
        else:
            return splittedData[0], splittedData[1]
    except:
        return str(np.nan), str(np.nan)

def GetDataByProfileUrl(driver, url):
    driver.get(url)
    print(f"Поиск по {url}")
    fullname = driver.find_element_by_css_selector("img[data-shmid='profileAvatar']").get_attribute('alt')
    print(f"[{fullname}]")
    services_table = driver.find_elements_by_css_selector("table[class='price-list desktop-profile__prices']")[0]

    # Получили элементы всех названий услуг
    service_names_items = services_table.find_elements_by_css_selector("tbody > tr[data-shmid='priceRow'] > td[class='item_name item_name-bold'] > span:nth-of-type(1)")

    # time.sleep(2)

    check_scroll = True

    # Прокрутили до последней видимой на экране услуги
    try:
        driver.execute_script("arguments[0].scrollIntoView();", service_names_items[-1])
    except:
        try:
            time.sleep(2)
            service_names_items = services_table.find_elements_by_css_selector("tbody > tr[data-shmid='priceRow'] > td[class='item_name item_name-bold'] > span:nth-of-type(1)")
            print(f"except[1], service_names_items = {len(service_names_items)}")
            driver.execute_script("arguments[0].scrollIntoView();", service_names_items[-1])
        except:
            try:
                services_table = driver.find_elements_by_css_selector("table[class='price-list desktop-profile__prices']")[1]
                service_names_items = services_table.find_elements_by_css_selector("tbody > tr[data-shmid='priceRow'] > td[class='item_name item_name-bold'] > span:nth-of-type(1)")
                print(f"except[2], service_names_items = {len(service_names_items)}")
                driver.execute_script("arguments[0].scrollIntoView();", service_names_items[-1])
            except:
                print("except[3] check_scroll = False")
                check_scroll = False
                pass

    # Если есть кнопка "Все услуги и цены", то кликаем на эту кнопку, иначе игнорим её
    try:
        refAllServicesAndPrices = driver.find_element_by_css_selector("a[data-shmid='pricesMore']")

        if not check_scroll:
            driver.execute_script("arguments[0].scrollIntoView();", refAllServicesAndPrices)

        refAllServicesAndPrices.click()
        # print("Кнопка \"Все услуги и цены\" нажата.")
    except:
        # print("Кнопки \"Все услуги и цены\" нет.")
        pass

    try:
        count_rates = driver.find_element_by_css_selector("span[data-shmid='reviewsCount']").text
        total_rate = driver.find_element_by_css_selector("span[data-shmid='ProfileTabsBlock_text']").text

        rate_five = driver.find_element_by_css_selector("div[data-shmid='ReviewHistogramComponent'] > div:nth-of-type(3) > div:nth-of-type(1)").text
        rate_four = driver.find_element_by_css_selector("div[data-shmid='ReviewHistogramComponent'] > div:nth-of-type(3) > div:nth-of-type(2)").text
        rate_three = driver.find_element_by_css_selector("div[data-shmid='ReviewHistogramComponent'] > div:nth-of-type(3) > div:nth-of-type(3)").text
        rate_two = driver.find_element_by_css_selector("div[data-shmid='ReviewHistogramComponent'] > div:nth-of-type(3) > div:nth-of-type(4)").text
        rate_one = driver.find_element_by_css_selector("div[data-shmid='ReviewHistogramComponent'] > div:nth-of-type(3) > div:nth-of-type(5)").text
    except:
        count_rates = 0
        total_rate = 0

        rate_five = 0
        rate_four = 0
        rate_three = 0
        rate_two = 0
        rate_one = 0

    tables = driver.find_elements_by_css_selector("table[class='price-list desktop-profile__prices']")

    # Проверка на случай, если кнопки "Все услуги и цены" всё-таки не было
    try:
        desired_table = tables[1]
    except:
        desired_table = tables[0]

    soup_table = bs4.BeautifulSoup(desired_table.get_attribute('innerHTML').encode('utf-8'), 'lxml')
    soup_service_names_items = soup_table.select("tbody > tr[data-shmid='priceRow'] > td[class='item_name item_name-bold'] > span:nth-of-type(1)")
    soup_service_cost_values = soup_table.select("tbody > tr[data-shmid='priceRow'] > td[class='item_value'] > span")

    service_names = []
    service_cost_values = []

    for name_item in soup_service_names_items:
        full_html = """<html><head></head><body>""" + str(name_item) + """</body></html>"""
        soup_item = bs4.BeautifulSoup(full_html, 'lxml')
        name_text_item = soup_item.find('span').text
        service_names.append(name_text_item)

    for cost_value in soup_service_cost_values:
        full_html = """<html><head></head><body>""" + str(cost_value) + """</body></html>"""
        soup_item = bs4.BeautifulSoup(full_html, 'lxml')
        cost_value_text_item = soup_item.find('span').text
        service_cost_values.append(cost_value_text_item)

    service_prices = []
    service_durations = []
    for cost_value in service_cost_values:
        price, duration = GetNormalizedPriceAndDuration(cost_value)
        service_prices.append(price)
        service_durations.append(duration)

    for idx in range(len(service_names)):
        temp = service_names[idx].strip().lower()
        service_names[idx] = temp

    profile = Profile(fullname, count_rates, total_rate, [rate_five, rate_four, rate_three, rate_two, rate_one],
                      service_names, service_prices, service_durations)

    return profile

def init_driver():
    # options = Options()
    # options.headless = True

    options = webdriver.FirefoxOptions()
    options.set_preference('general.useragent.override', 'example :)')
    options.headless = True

    profile = webdriver.FirefoxProfile()

    caps = DesiredCapabilities().FIREFOX
    caps["pageLoadStrategy"] = "eager"

    driver = webdriver.Firefox(
        options=options,
        firefox_profile=profile,
        desired_capabilities=caps,
        executable_path="C:\\Users\\ipluk\\PycharmProjects\\Курсач\\webdrivers\\geckodriver.exe",
        firefox_binary="C:\\Program Files\\Mozilla Firefox\\firefox.exe"
    )

    return driver

def main():
    driver = init_driver()

    driver.get('https://profi.ru/services/repetitor/')

    print("Страница загрузилась")

    subjects = []

    # Получили все темы
    items = driver.find_elements_by_css_selector("a.services-catalog__column-title")

    page_counter = 0

    scroll_count = 0

    subject = ""

    # Проходимся по всем темам
    for den in range(len(items)):
        try:
            # # Получили все темы
            items = driver.find_elements_by_css_selector("a.services-catalog__column-title")

            # Выбрали определённую тему
            item = items[den]

            # Проискролимся до нужного элемента
            driver.execute_script("arguments[0].scrollIntoView();", item)

            # Записали название темы
            subject = item.text

            fullname_subject = item.text.split(' ')
            subject = ''
            for subject_part in range(len(fullname_subject)):
                if (subject_part != (len(fullname_subject) - 1)):
                    subject += (fullname_subject[subject_part] + ' ')
            subject = subject.strip()

            # recorded_subjects = ['Актёрское мастерство', 'Английский язык', 'Арабский язык', 'Аренда учебных помещений', 'Биология', 'Бухгалтерский учёт', 'География', 'Дизайн', 'Другие языки', 'Журналистика']
            #
            # if subject in recorded_subjects:
            #     print(f"Тема {subject} уже записана.")
            #     continue

            # Проверяем есть ли данные по выбранной теме
            if ('#' in item.get_attribute('href')):
                print("Тема \"" + subject + "\" пропущена")
                continue

            print("Тема: " + subject)

            # Переходим по выбранной теме
            item.click()

            # Ищем вкладку "Специалисты"
            specs = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "a.seamless__navigation-static-link[data-shmid='navigationTab__PROFILES']> span > span"))
            )

            # Переходим на вкладку "Специалисты"
            specs.click()

            time.sleep(4)

            total_time_scroll = 0

            touch = 0 # сколько нажатий на кнопку "Показать ещё"
            while True:
                start_time = time.time()
                # Скролимся до нижней границы экрана (страницы)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Если ещё есть куда скролить, т.е. если есть кнопка "Показать ещё"
                try:
                    # Ищем кнопку "Показать ещё"
                    next_page = WebDriverWait(driver, 10, ignored_exceptions=StaleElementReferenceException).until(
                        ec.presence_of_element_located((By.CSS_SELECTOR, "a.pagination__show-more"))
                    )

                    # Кликаем на кнопку "Показать ещё"
                    next_page.click()
                except:
                    # Ждём пока страница прогрузится
                    time.sleep(5)

                    try:
                        # Ищем кнопку "Показать ещё"
                        next_page = WebDriverWait(driver, 10, ignored_exceptions=StaleElementReferenceException).until(
                            ec.presence_of_element_located((By.CSS_SELECTOR, "a.pagination__show-more"))
                        )

                        # Кликаем на кнопку "Показать ещё"
                        next_page.click()
                    except:
                        print("Кнопка \"Посмотреть ещё 20\" не найдена")
                        break

                touch += 1
                end_time = time.time() - start_time
                total_time_scroll += end_time
                print(f"Пролистано {touch * 20} профилей [{round(end_time, 3)} сек.]")

                # if touch == 1:
                #     break

            print(f"Общее время, затраченное на пролистывание {touch * 20} страниц = {total_time_scroll} сек.")

            source_page = driver.find_element_by_xpath("/html").get_attribute("innerHTML")

            print("> Запись начата.")
            with open('source_page.html', 'w', encoding='utf-8') as writer:
                writer.write(source_page)
            print("> Запись закончена.")

            print("> Чтение начато.")
            # root = bs4.BeautifulSoup(open("C:/Users/roman/PycharmProjects/SeleniumTests/source_page.html", encoding="utf8").read(), 'lxml')
            root = bs4.BeautifulSoup(source_page.encode('utf-8'), 'lxml')
            print("> Чтение закончено.")

            links = root.find_all('a', href=True)

            correct_links = []
            for link in links:
                try:
                    if('listing-profile__name' in link['class']):
                        temp = ""
                        if "profi.ru" in link['href']:
                            temp = link['href']
                        else:
                            temp = "https://profi.ru" + link['href']

                        correct_links.append(temp)
                except:
                    temp = ""
                    if "profi.ru" in link['href']:
                        temp = link['href']
                    else:
                        temp = "https://profi.ru" + link['href']

                    correct_links.append(temp)

            profiles = []

            driver.close()
            driver.quit()
            driver = init_driver()

            counter = 1
            total_time_profiles_data = 0
            for link in correct_links:
                start_time = time.time()
                # print(f"link = [{link}]")

                if counter % 100 == 0:
                    start_restart = time.time()
                    driver.close()
                    driver.quit()
                    driver = init_driver()
                    end_restart = time.time() - start_restart
                    print(f"> WebDriver перезапустился [{end_restart}]")

                try:
                    profile_item = GetDataByProfileUrl(driver, link)
                    profiles.append(profile_item)
                    end_time = time.time() - start_time
                    total_time_profiles_data += end_time
                    print(f"{counter}. [{round(end_time, 3)} сек.] ✓ — {profile_item.GetFullname()} [{link}]")
                    counter += 1
                except:
                    # print("``````````````````````````````````````````Встретилась плохая ссылочка``````````````````````````````````````````")
                    counter += 1
                    continue

            print(f"Общее время, затраченное на получение инфы с {counter - 1} профиля (-ей) = {total_time_profiles_data} сек.")

            # Вывод всех профилей конкретной темы
            subject = Subject(subject, profiles)
            subjects.append(subject)

            column_names = ['Fullname', 'CountRates', 'TotalRate', 'FiveRate', 'FourRate', 'ThreeRate', 'TwoRate',
                            'OneRate']

            # Получаем нормальное название темы и CSV файла
            subject_filename = subject.GetSubject().strip() + ".xlsx"

            dict_rows = []
            unique_services = []
            total_services = 0
            for profile in subject.GetProfiles():
                total_services += len(profile.GetAllServiceNames())
                for service_name in profile.GetAllServiceNames():
                    prepared_service_name = service_name.strip().lower()
                    if not (prepared_service_name in unique_services):
                        unique_services.append(prepared_service_name)

            column_names += unique_services

            subject_df = pd.DataFrame(columns=column_names)

            result_for_additional_columns = []
            indexes_counter = 0
            for profile in subject.GetProfiles():
                result_for_additional_columns.append(profile.GetFullname())
                result_for_additional_columns.append(profile.GetCountRates())
                result_for_additional_columns.append(profile.GetTotalRate())

                result_for_additional_columns.append(profile.GetCountRateByMark(5))
                result_for_additional_columns.append(profile.GetCountRateByMark(4))
                result_for_additional_columns.append(profile.GetCountRateByMark(3))
                result_for_additional_columns.append(profile.GetCountRateByMark(2))
                result_for_additional_columns.append(profile.GetCountRateByMark(1))

                for column_name in unique_services:
                    if column_name in profile.GetAllServiceNames():
                        result_for_additional_columns.append(profile.GetServiceCostByServiceName(column_name))
                    else:
                        result_for_additional_columns.append(np.nan)

                subject_df.loc[indexes_counter] = result_for_additional_columns

                indexes_counter += 1

                result_for_additional_columns = []

            subject_df.to_excel("Subjects/" + subject_filename, encoding='utf-8', index=False)  # ascii

            scroll_count += 1
            # if scroll_count == 2:
            #     break

            print("> Переход на новый предмет (5 секунд)")
            time.sleep(5)

            driver.get('https://profi.ru/services/repetitor/')
            items = driver.find_elements_by_css_selector("a.services-catalog__column-title")
        except:

            # print("``````````````````````````````````````````Чёто пошло не так``````````````````````````````````````````")

            # Вывод всех профилей конкретной темы
            subject = Subject(subject, profiles)
            subjects.append(subject)

            column_names = ['Fullname', 'CountRates', 'TotalRate', 'FiveRate', 'FourRate', 'ThreeRate', 'TwoRate',
                            'OneRate']

            # Получаем нормальное название темы и CSV файла
            subject_filename = subject.GetSubject().strip() + ".xlsx"

            dict_rows = []
            unique_services = []
            total_services = 0
            for profile in subject.GetProfiles():
                total_services += len(profile.GetAllServiceNames())
                for service_name in profile.GetAllServiceNames():
                    prepared_service_name = service_name.strip().lower()
                    if not (prepared_service_name in unique_services):
                        unique_services.append(prepared_service_name)

            column_names += unique_services

            subject_df = pd.DataFrame(columns=column_names)

            result_for_additional_columns = []
            indexes_counter = 0
            for profile in subject.GetProfiles():
                result_for_additional_columns.append(profile.GetFullname())
                result_for_additional_columns.append(profile.GetCountRates())
                result_for_additional_columns.append(profile.GetTotalRate())

                result_for_additional_columns.append(profile.GetCountRateByMark(5))
                result_for_additional_columns.append(profile.GetCountRateByMark(4))
                result_for_additional_columns.append(profile.GetCountRateByMark(3))
                result_for_additional_columns.append(profile.GetCountRateByMark(2))
                result_for_additional_columns.append(profile.GetCountRateByMark(1))

                for column_name in unique_services:
                    if column_name in profile.GetAllServiceNames():
                        result_for_additional_columns.append(profile.GetServiceCostByServiceName(column_name))
                    else:
                        result_for_additional_columns.append(np.nan)

                subject_df.loc[indexes_counter] = result_for_additional_columns

                indexes_counter += 1
                result_for_additional_columns = []

            subject_df.to_excel("Subjects/" + subject_filename, encoding='utf-8', index=False)  # ascii

            scroll_count += 1
            # if scroll_count == 2:
            #     break

            print("> Переход на новый предмет (5 секунд)")
            time.sleep(5)

            driver.get('https://profi.ru/services/repetitor/')
            items = driver.find_elements_by_css_selector("a.services-catalog__column-title")


    driver.close()

    for subject in subjects:
        subject_filename = ''

        column_names = ['Fullname', 'CountRates', 'TotalRate', 'FiveRate', 'FourRate', 'ThreeRate', 'TwoRate', 'OneRate']

        # Получаем нормальное название темы и CSV файла
        fullname_subject = subject.GetSubject().split(' ')
        subject_correct = ''
        for subject_part in range(len(fullname_subject)):
            if (subject_part != (len(fullname_subject) - 1)):
                subject_correct += (fullname_subject[subject_part] + ' ')
        subject_filename = subject_correct.strip() + ".xlsx"

        dict_rows = []
        unique_services = []
        total_services = 0
        for profile in subject.GetProfiles():
            total_services += len(profile.GetAllServiceNames())
            for service_name in profile.GetAllServiceNames():
                prepared_service_name = service_name.strip().lower()
                if not (prepared_service_name in unique_services):
                    unique_services.append(prepared_service_name)

        column_names += unique_services

        subject_df = pd.DataFrame(columns=column_names)

        result_for_additional_columns = []
        indexes_counter = 0
        for profile in subject.GetProfiles():
            result_for_additional_columns.append(profile.GetFullname())
            result_for_additional_columns.append(profile.GetCountRates())
            result_for_additional_columns.append(profile.GetTotalRate())

            result_for_additional_columns.append(profile.GetCountRateByMark(5))
            result_for_additional_columns.append(profile.GetCountRateByMark(4))
            result_for_additional_columns.append(profile.GetCountRateByMark(3))
            result_for_additional_columns.append(profile.GetCountRateByMark(2))
            result_for_additional_columns.append(profile.GetCountRateByMark(1))

            for column_name in unique_services:
                if column_name in profile.GetAllServiceNames():
                    result_for_additional_columns.append(profile.GetServiceCostByServiceName(column_name))
                else:
                    result_for_additional_columns.append(np.nan)

            subject_df.loc[indexes_counter] = result_for_additional_columns

            indexes_counter += 1

            result_for_additional_columns = []

        subject_df.to_excel("Subjects/" + subject_filename, encoding='utf-8', index=False) # ascii

if __name__ == '__main__':
    main()
