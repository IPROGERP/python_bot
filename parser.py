import pprint
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium import webdriver
import time
import logging
import sqlite3
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, select

def logging_dec(func):
    def wrapper(*args, **kwargs):
        logging.basicConfig(
            filename = "parsing.log",
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | Файл: %(filename)s | %(message)s"
        )
        logging.info(f"Использование функции: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@logging_dec
def parse_html(html):
    return BeautifulSoup(html, 'html.parser')


@logging_dec
def get_page(driver, url):
    return driver.get(url)


@logging_dec
def find_table(soup, role, class_name):
    return soup.find('div', {'role': role, 'class': class_name})


@logging_dec
def info_to_db(url):
    try:
        driver = webdriver.Chrome()
        get_page(driver, url)
        time.sleep(10)
        
        html = driver.page_source
        soup = parse_html(html)

        table = find_table(soup, 'table', 'sc-gsrHEG bAKLOS')
        if table:
            rows = table.find_all('tr', {'class': 'sc-jZbSde sc-bFbBKk gRlzay ftjJTC'})
            
            engine = create_engine(f"sqlite:///trains.db")
            conn = engine.connect()
            trains_table = create_db(engine)
            
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 9:

                    route = f"{columns[3].text.strip()} -> {columns[4].text.strip()}"

                    train_data = {
                        'number': columns[2].text.strip(),
                        'route': route,
                        'departure': columns[7].text.strip(),
                        'arrival': columns[8].text.strip()
                    }
                    write_to_db(conn, trains_table, train_data)  
            conn.close()
        else:
            print("Таблица не найдена.")

    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
    finally:
        driver.quit()

def write_to_db(conn, trains_table, train_data):
    try:
        query = select(trains_table).where(trains_table.c.train_number == train_data['number'])
        result = conn.execute(query).fetchone()

        if result:
            logging.info(f"Поезд с номером {train_data['number']} уже существует, пропускаем.")
        else:
            insert_query = trains_table.insert().values(
                train_number=train_data['number'],
                route=train_data['route'],
                departure_time=train_data['departure'],
                arrival_time=train_data['arrival']
            )
            conn.execute(insert_query)
            conn.commit()
    except sqlite3.IntegrityError as e:
        logging.error(f"Ошибка при вставке поезда {train_data['number']}: {str(e)}")


def create_db(engine):
    meta_data = MetaData()
    trains = Table(
        "trains", meta_data,
        Column("id", Integer, primary_key=True),
        Column("train_number", String, unique=True),
        Column("route", String),
        Column("departure_time", String),
        Column("arrival_time", String)
    )
    meta_data.create_all(engine)
    return trains

def filter_trains(engine, column_name, value):
    conn = engine.connect()
    trains_table = Table('trains', MetaData(), autoload_with=engine)

    query = select(trains_table).where(trains_table.c[column_name] == value)
    result = conn.execute(query)

    for row in result:
        print(row)
    conn.close()

def sort_trains(engine, column_name, order='asc'):
    conn = engine.connect()
    trains_table = Table('trains', MetaData(), autoload_with=engine)

    if order == 'asc':
        query = select(trains_table).order_by(trains_table.c[column_name].asc())
    else:
        query = select(trains_table).order_by(trains_table.c[column_name].desc())

    result = conn.execute(query)

    for row in result:
        print(row)
    conn.close()

url = "https://www.kaggle.com/datasets/dnyaneshyeole/indian-trains/data?select=trains.csv"
info_to_db(url)

engine = create_engine(f"sqlite:///trains.db")

print("Поезда с номером 04601:")
filter_trains(engine, 'train_number', '04601')

print("Поезда, отсортированные по времени отправления (по возрастанию):")
sort_trains(engine, 'departure_time', order='asc')

print("Поезда, отсортированные по времени отправления (по убыванию):")
sort_trains(engine, 'departure_time', order='desc')
