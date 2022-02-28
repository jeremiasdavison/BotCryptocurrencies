import requests
import json
import time
import datetime
import schedule
from pyowm import OWM
import claves
from telegram.ext import *
import os


"""
from flask import Flask
app = Flask(__name__)
@app.route('/')
 def Index():
    #return 'Hello from Flask!'

"""

def dayReportETH():
    consulta = json.loads(requests.get(f"https://min-api.cryptocompare.com/data/v2/histoday?fsym=ETH&tsym=USD&limit=1{claves.clave}").text)
    return consulta['Data']['Data'][1]['low'], consulta['Data']['Data'][1]['high']
eth_low, eth_high = dayReportETH()

def dayReportBTC():
    consulta = json.loads(requests.get(f"https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=1{claves.clave}").text)
    return consulta['Data']['Data'][1]['low'], consulta['Data']['Data'][1]['high']
btc_low, btc_high = dayReportBTC()

def dayReportSOL():
    consulta = json.loads(requests.get(f"https://min-api.cryptocompare.com/data/v2/histoday?fsym=SOL&tsym=USD&limit=1{claves.clave}").text)
    return consulta['Data']['Data'][1]['low'], consulta['Data']['Data'][1]['high']
sol_low, sol_high = dayReportSOL()

def dayReportADA():
    consulta = json.loads(requests.get(f"https://min-api.cryptocompare.com/data/v2/histoday?fsym=ADA&tsym=USD&limit=1{claves.clave}").text)
    return consulta['Data']['Data'][1]['low'], consulta['Data']['Data'][1]['high']
ada_low, ada_high = dayReportADA()


def actualCrypto():
    consultaBTC = json.loads(requests.get(f'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD{claves.clave}').text)["USD"]
    consultaETH = json.loads(requests.get(f'https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD{claves.clave}').text)["USD"]
    consultaSOL = json.loads(requests.get(f'https://min-api.cryptocompare.com/data/price?fsym=SOL&tsyms=USD{claves.clave}').text)["USD"]
    consultaADA = json.loads(requests.get(f'https://min-api.cryptocompare.com/data/price?fsym=ADA&tsyms=USD{claves.clave}').text)["USD"]

    return int(consultaETH), int(consultaBTC), consultaADA, consultaSOL

def sendMsg(mensaje):
    send_text = f'{claves.telegram}{mensaje}'
    response = requests.get(send_text)
    return response.json()

def weather():
    owm = OWM(claves.owm)
    mgr = owm.weather_manager()
    clima = mgr.weather_at_place('Buenos Aires, Argentina')
    w = clima.weather
    detalle = w.detailed_status
    return f'The Weather is {detalle}\nTemperature is {w.temperature("celsius")["temp"]}°🌥'

def news_report():
    algo = ''
    consulta = json.loads(requests.get(f"https://min-api.cryptocompare.com/data/v2/news/?lang=ES{claves.clave}").text)
    for x in range(5):
        msg = (consulta['Data'][x]['title'])
        url = consulta['Data'][x]['url']
        algo = algo + msg + "\n" + url +'\n'
    return f'Day News {datetime.date.today()}: \n {algo}'
        
def dailyReport():
    global eth_low, eth_high, btc_low, btc_high
    eth_low, eth_high = dayReportETH()
    btc_low, btc_high = dayReportBTC()
    sol_low, sol_high = dayReportSOL()
    ada_low, ada_high = dayReportADA()
    sendMsg(f'Daily Report of {datetime.date.today()}\n\nBITCOIN || HIGH: {btc_high} LOW: {btc_low}\nETHEREUM || HIGH: {eth_high} LOW: {eth_low}\nCARDANO || HIGH: {ada_high} LOW: {ada_low}\nSOLANA || HIGH: {sol_high} LOW: {sol_low}\n\n{weather()}')

def clean():
    os.system('cls')

def minutesReport():
    global eth_high, eth_low, btc_high, btc_low, ada_low, ada_high, sol_low, sol_high
    actualETH, actualBTC, actualADA, actualSOL = actualCrypto()

    if actualBTC < btc_low:    
        sendMsg(f'BTC LOW:      {actualBTC}')
        btc_low = actualBTC - 100   # Esto lo hacemos para que avise cuando baje un precio relativo
    elif actualBTC > btc_high:
        sendMsg(f'BTC HIGH:     {actualBTC}')
        btc_high = actualBTC + 100 

    if actualETH < eth_low:
        sendMsg(f'ETH LOW:      {actualETH}')
        eth_low = actualETH - 50
    elif actualETH > eth_high:
        sendMsg(f'ETH HIGH:     {actualETH}')
        eth_high = actualETH + 50 

    if actualADA  < ada_low:
        sendMsg(f'ADA LOW:      {actualADA}')
        ada_low = actualADA - 0.01
    elif actualADA > ada_high:
        sendMsg(f'ADA HIGH:     {actualADA}')
        ada_high = actualADA + 0.01

    if actualSOL < sol_low:
        sendMsg(f'SOL LOW:      {actualSOL}')
        sol_low = actualSOL - 5
    elif actualSOL > sol_high:
        sendMsg(f'SOL HIGH:     {actualSOL}')
        sol_high = actualSOL + 5      

def handle_message(update, ctx):
    text = str(update.message.text)
    update.message.reply_text(text)

def check_command(update, ctx):
    update.message.reply_text('I´m alive')
#############################################

if __name__ == '__main__':
    try:
        schedule.every().day.at("00:30").do(dailyReport)
        schedule.every().day.at("11:00").do(dailyReport)
        schedule.every().day.at("11:00").do(news_report)
        schedule.every(1).minutes.do(minutesReport) 
    except:
        sendMsg('Error en consultas Diarias/News')

    updater = Updater(claves.telegram_key, use_context=True)
    dp = updater.dispatcher
    #Commands handlers
    dp.add_handler(CommandHandler('check', check_command))
    updater.start_polling(1.0)

    while True: 
        try:
            schedule.run_pending()
            time.sleep(15) # Para que no se sobre-cargue el server :) (: 
        except:
            try:
                schedule.run_pending()
                time.sleep(15) # Para que no se sobre-cargue el server :) (: 
            except:
                clean()
                print("URGENTE\nError en el codigo")
                sendMsg("URGENTE\nError en el codigo")
        
            
"""                              ---     Ideas   ---
        .   Social Media Cryptos
"""