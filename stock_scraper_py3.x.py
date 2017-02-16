import urllib.request
import urllib.error
import csv
import json
import datetime
import time
from random import randint

def request_until_succeed(url):
    req = urllib.request.Request(url)
    success = False
    fails = 0
    while success is False:
        try: 
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            if response.getcode() == 400:
                fails += 1
                if fails >= 5:
                    print('%s does not have a valid symbol, consider removing it from the list' % url)
                    return False
            print(e)
            print("Error for URL %s at %s" % (url, datetime.datetime.now()))
            time.sleep(1)
            print("Retrying.")
    data = response.read().decode('utf-8')
    data = data.replace('[','').replace('//','').replace('\n','').replace(']','')
    return data

def getStockData(stockSym):
    base = "http://finance.google.com/finance/info?q="
    parameter = stockSym.replace(' ','')

    url = base + parameter

    data = request_until_succeed(url)
    if data == False:
        return False
    data = json.loads(data)

    return data

def processStockData(stock):
    stock_sym = stock['t']
    stock_price = stock['l']
    stock_chg = stock['c']

    stock_time = stock['lt_dts'].replace('Z','')
    if stock_time != '':
        stock_time = datetime.datetime.strptime(\
                stock_time,'%Y-%m-%dT%H:%M:%S')
        stock_time = stock_time + + datetime.timedelta(hours=-5)
        stock_time = stock_time.strftime('%Y-%m-%d %H:%M:%S')

    return (stock_sym, stock_price, stock_chg, stock_time)

def pickStocks(list):
    stocks_scraped = []
    stocks_results = []
    
    tryAgain = True
    
    while(tryAgain):
        value = input('Number of Stocks to scrape (Max %s): ' % len(list))
        try:
            scrape_num = int(value)
            if(scrape_num <= len(list)):
                tryAgain = False
            else:
                print('Input value is larger than amount of stocks')
        except(ValueError):
            print('%s is not a number' % value)
    i = 0
    offset = randint(0, len(list) - scrape_num - 1)
    while i < scrape_num:
        if scrape_num == len(list) - int(len(list) / 10):
            index = randint(0, len(list) - 1)
        else:
            index = i + offset

        if (index in stocks_scraped):
            continue

        else:
            stocks_scraped.append(index)
            rawStock = getStockData(list[index])
            if rawStock == False:
                continue
            stocks_results.append(rawStock)
            i += 1
            if i % 10 == 0:
                print('%s stocks scraped' % i)

    return stocks_results
    

def scrapeStocks():
    with open('stockList.csv', 'r') as f:
        reader = csv.reader(f)
        stockList = list(reader)[0]

    scrape_starttime = datetime.datetime.now()
    scrape_path = scrape_starttime.strftime('%Y%m%d_%H%M')
    with open('%s_stocks.csv' % scrape_path, 'w', newline='') as file:
        w = csv.writer(file)
        w.writerow(["symbol","price","change","last update"])
       
        num_processed = 0
    
        print('Stock scrape started at %s' % (scrape_starttime))
    
        stocks = pickStocks(stockList)

        for i in range(len(stocks)):
            w.writerow(processStockData(stocks[i]))
            num_processed += 1
            if num_processed % 10 == 0:
                print("%s Stocks Processed: %s" % (num_processed, datetime.datetime.now()))
    
    print("\nDone!\n%s Stocks Processed in %s" % \
        (num_processed, datetime.datetime.now() - scrape_starttime))

if __name__ == '__main__':
    scrapeStocks()