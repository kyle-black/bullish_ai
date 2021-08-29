import sqlite3
import config
import alpaca_trade_api as tradeapi
from datetime import date
#from polygon import Wev
import smtplib
import ssl

context = ssl.create_default_context()

connection = sqlite3.connect(config.DB_FILE)

connection.row_factory = sqlite3.Row
cursor = connection.cursor()


cursor.execute("""
select id from strategy where name= 'Two-Black-Gapping'
""")


strategy_id = cursor.fetchone()['id']


cursor.execute("""
    SELECT symbol, name
    FROM stock
    JOIN stock_strategy on stock_strategy.stock_id = stock.id
    WHERE stock_strategy.strategy_id =?
    """, (strategy_id,))


stocks = cursor.fetchall()
symbols = [stock['symbol'] for stock in stocks]
current_date = date.today().isoformat()


#start_minute_bar = f"{current_date} 09:30:00-04:00"
#end_minute_bar = f"{current_date} 09:45:00-04:00"


api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)


#orders = api.list_orders()
#existing_order_symbols =[order.symbol for order in orders]

messages = []

for symbol in symbols:

    minute_bars = api.get_barset(symbol, 'minute').df

    minute_bars = minute_bars[symbol]
    # USE WHEN ALPACA MARKET BROKERAGE ACCOUNT IS APPROVED
    #minute_bars= api.polygon.historic_agg_v2(symbol,1,'minute', _from=current_date, to=current_date).df

    newest_bar = minute_bars.iloc[-1]
    second_newest_bar = minute_bars.iloc[-2]
    third_newest_bar = minute_bars.iloc[-3]
    fourth_newest_bar = minute_bars.iloc[-3]

    newest_low = newest_bar["low"]
    newest_high = newest_bar["high"]

    if newest_bar['close'] < second_newest_bar['close'] and newest_bar["open"] >= second_newest_bar["close"] and second_newest_bar['open'] < second_newest_bar['close'] and third_newest_bar['open'] < third_newest_bar['close'] and fourth_newest_bar['open'] < fourth_newest_bar['close']:

        messages.append(
            f"Bearish Pattern Found! Lowest Price for last period: {newest_low} ")
        print(messages)
        pattern = True
    else:
        print("Bearish pattern not in play.")
        pattern = False

    if pattern == True:
        with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
            server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)

    email_message = f"Subject: Trade Notifications for {current_date}\n\n"
    email_message = "\n".join(messages)
    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message)
