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
select id from strategy where name= 'Bullish-Three-Line-Strike'
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
            f"Bullish Pattern Found! Suggested stop loss:{newest_low} ")
        print(messages)
        pattern = True
    else:
        print("Bullish pattern not in play.")
        pattern = False

    if pattern == True:
        with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
            server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)

    email_message = f"Subject: Trade Notifications for {current_date}\n\n"
    email_message = "\n".join(messages)
    server.sendmail(config.EMAIL_ADDRESS, config.EMAIL_ADDRESS, email_message)


'''
    #print(symbol)
    #print(minute_bars[symbol]['low'])
    opening_range_mask =(minute_bars.index >= start_minute_bar) & (minute_bars.index <end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]
    #print(opening_range_bars[symbol]['low'])
    #print(opening_range_bars)
    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].max()
    opening_range = opening_range_high - opening_range_low

    #print(opening_range_low)
    #print(opening_range_high)
    #print(opening_range)
    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]

    #print(after_opening_range_bars)

    after_opening_range_breakout =after_opening_range_bars[after_opening_range_bars['close'] > opening_range_high]

    print(after_opening_range_breakout)
    #print(after_opening_range_breakout.iloc[0]['close])
    if not after_opening_range_breakout.empty:
        
        if symbol not in existing_order_symbols:
            limit_price = after_opening_range_breakout.iloc[0]['close']

            
            messages.append(f"placing order for {symbol} at {limit_price}, closed_above {opening_range_high} at {after_opening_range_breakout.iloc[0]}")
            print(f"placing order for {symbol} at {limit_price}, closed_bove {opening_range_high} at {after_opening_range_breakout.iloc[0]}")

       #     api.submit_order(
       #         symbol=symbol,
       #         side='buy',
       #         type='limit',
       #         qty='100',
       #         time_in_force='day',
       #         order_class='bracket',
       #         limit_price=limit_price,
       #         take_profit=dict(
       #             limit_price=limit_price +opening_range,
       #         ),
       #         stop_loss=dict(
       #             stop_price=limit_price-opening_range,
                    
       #         )
       #     )
       # else:
       #     print(f"Already an order for {symbol}, skipping")
print(messages)

with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
    
    email_message = f"Subject: Trade Notifications for {current_date}\n\n"
    email_message = "\n".join(messages)
    server.sendmail(config.EMAIL_ADDRESS,config.EMAIL_ADDRESS,email_message)
'''
