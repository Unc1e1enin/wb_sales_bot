import time

import telebot
import requests
from datetime import datetime, timedelta

from keys import API64, TG_TOKEN, CHAT_ID
from smiles import smile

bot = telebot.TeleBot(TG_TOKEN)
num_order_list = []
num_sales_list = []


def get_past_date():
    pastdate = datetime.today() - timedelta(hours=1)
    return pastdate.strftime('%Y-%m-%dT%H:%M:%S')


def get_act_date():
    return str(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))


@bot.message_handler(commands=['get_data'])
def get_data(message):
    print('Unclelenin. 2022')
    while True:
        try:
            print(get_act_date(), 'Новый запрос по заказам ')
            orders = requests.get(f'https://suppliers-stats.wildberries.ru/api/v1/supplier/orders'
                                  f'?dateFrom={get_past_date()}&key={API64}&flag=1')
            response_orders = orders.json()
            for i in response_orders:
                if i.get('gNumber') in num_order_list:
                    print(get_act_date(), 'Новых заказов нет')
                else:
                    num_order_list.append(i.get('gNumber'))
                    date = i.get('date')
                    date_form = str(date).split('T')
                    article = i.get('nmId')
                    sup_article = i.get('supplierArticle')
                    price = i.get('totalPrice')
                    discount = i.get('discountPercent')
                    final_price = int(price) - (int(price) * int(discount) / 100)
                    destination = i.get('oblast')
                    subject = i.get('subject')
                    smile_ordered_item = ''
                    if subject in smile:
                        smile_ordered_item = smile.get(subject) + ' ' + i.get('subject')
                    order_text = f'{smile.get("calendar")} {date_form[0]} {smile.get("time")} {date_form[1]} \n' \
                                 f'{smile.get("shopping_cart")} Новый заказ: {smile_ordered_item}' \
                                 f'{smile.get("money_bag")} {round(final_price, 2)}₽ \n{smile.get("id")} Артикул ' \
                                 f'{sup_article} \n{smile.get("link")} https://www.wildberries.ru/catalog/{article}' \
                                 f'/detail.aspx?targetUrl=XS \n{smile.get("globe")} Доставка в {destination}'
                    bot.send_message(chat_id=CHAT_ID, text=order_text)
                    print(get_act_date(), 'Новый заказ!!!')
            if len(num_order_list) == 0:
                print(get_act_date(), 'Новых заказов нет')
            time.sleep(30)
            print(get_act_date(), 'Новый запрос по выкупам')
            sales = requests.get(f'https://suppliers-stats.wildberries.ru/api/v1/supplier/sales?dateFrom='
                                 f'{get_past_date()}&key={API64}&flag=1')
            sales_response = sales.json()
            for i in sales_response:
                if i.get('saleID') in num_sales_list:
                    print(get_act_date(), 'Новых выкупов и возвратов нет')
                else:
                    num_sales_list.append(i.get('saleID'))
                    date = i.get('date')
                    date_form = str(date).split('T')
                    article = i.get('nmId')
                    sup_article = i.get('supplierArticle')
                    finish_priice = i.get('finishedPrice')
                    destination = i.get('regionName')
                    subject = i.get('subject')
                    smile_sales_item = ''
                    if subject in smile:
                        smile_sales_item = smile.get(subject) + ' ' + i.get('subject')
                    if str(i.get('saleID')).startswith('S'):
                        sales_text = f'{smile.get("calendar")} {date_form[0]} {smile.get("time")} {date_form[1]} \n' \
                                     f'{smile.get("credit_card")} Выкупили: {smile_sales_item} ' \
                                     f'{smile.get("money_bag")} {round(finish_priice, 2)}₽ \n' \
                                     f'{smile.get("id")} Артикул {sup_article} \n{smile.get("link")} ' \
                                     f'https://www.wildberries.ru/catalog/{article}/detail.aspx?targetUrl=XS \n' \
                                     f'{smile.get("globe")} Выкуп из {destination}'
                        bot.send_message(chat_id=CHAT_ID, text=sales_text)
                        print(get_act_date(), 'Новый выкуп!!!')
                    else:
                        return_text = f'Неизвестный saleID!!! {i.get("saleID")}'
                        bot.send_message(chat_id=CHAT_ID, text=return_text)
                        print(get_act_date(), 'Похоже на возват!')
            if len(num_sales_list) == 0:
                print(get_act_date(), 'Новых выкупов и возвратов нет')
            print(get_act_date(), 'Запросы выполнены успешно, следующий запрос через 20 минут')
            time.sleep(1200)
        except:
            print(get_act_date(), 'Ошибка, повторный запрос к API WB')
            time.sleep(30)
            get_data(message)


@bot.message_handler(commands=['get_stock'])
def get_stock():
    stock = requests.get(
        'https://suppliers-stats.wildberries.ru/api/v1/supplier/stocks?dateFrom=2022-07-09&'
        'key=API64')
    stock_response = stock.json()
    for i in stock_response:
        nmid = i.get('nmId')
        subject = i.get('subject')
        to_client = i.get('inWayToClient')
        from_client = i.get('inWayFromClient')
        quanity = i.get('quantity')
        article = i.get('supplierArticle')
        warehouse = i.get('warehouseName')
        stock_text = f'{smile.get("link")}https://www.wildberries.ru/catalog/{nmid}/detail.aspx?targetUrl=EX \n' \
                     f'{smile.get(subject)}{subject} {smile.get("id")}{article} \n' \
                     f'{smile.get("red_car")}В пути до клиента {to_client} \n' \
                     f'{smile.get("green_car")}В пути от клиента {from_client} \n'
        f'{smile.get("box")}На складе {warehouse} {quanity} \n'
        bot.send_message(chat_id=CHAT_ID, text=stock_text)


if __name__ == '__main__':
    bot.infinity_polling(timeout=60)
