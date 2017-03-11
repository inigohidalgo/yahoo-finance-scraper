import requests
import datetime
import logging
from collections import OrderedDict
logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)



def get_stock_info(stockList,companydata):
    data = open(companydata)
    data = open.read()
    data = data.split('\n')
    for line in data:
        line = line.split(',')
        line = [line[0], line[5], line[6]]
    # for stock in stockList:

    
def downloadData(start, end, tickerList):
    if not end: # if no end date provided, set today as the end date
        end = datetime.date.today().strftime("%d/%m/%Y")
    splitStart = start.split('/') # split given dates into day, month, year
    splitEnd = end.split('/')
    startDict = {}
    endDict = {}
    # e day close,
    # d = month close,
    # f = year close,
    # b = day open,
    # a = month open,
    # c = year open
    startDict['day'] = splitStart[0]
    startDict['month'] = str(int(splitStart[1]) - 1)
    startDict['year'] = splitStart[2]
    endDict['day'] = splitEnd[0]
    endDict['month'] = str(int(splitEnd[1]) - 1)
    endDict['year'] = splitEnd[2]
    data = {}
    marketList = []
    for ticker in tickerList:
        name = ticker.split(".")[0] #split into ticker and market
        marketName = ticker.split(".")[1] #split into ticker and market
        if marketName not in marketList:
                marketList.append(marketName)
        market = str(marketList.index(marketName))
        #print(ticker)
        data[name] = {} # setting up the dictionary entry for the ticker
        url = ( #downloading the data as a string
            "https://ichart.finance.yahoo.com/table.csv"
            "?e=%s"
            "&d=%s"
            "&f=%s"
            "&g=d"
            "&b=%s"
            "&a=%s"
            "&c=%s"
            "&ignore=.csv"
            "&s=%s"
            % (endDict['day'], endDict['month'], endDict['year'],
               startDict['day'], startDict['month'], startDict['year'], ticker))
        csv = requests.get(url).text
        if 'Yahoo! - 404 Not Found' in csv: # error prevention
            print('restarting ' + ticker)
            continue
        logging.info(url)
        logging.info(csv)
        dataList = csv.split('\n') # splitting observations into different items in a list
        del dataList[-1] # deleting empty line at the end of the dataset
        for rowIndex in range(len(dataList)):
            dataList[rowIndex] = dataList[rowIndex].split(',') # splitting each observation by commas (list of lists)
            original_date = dataList[rowIndex][0]
            if '-' in original_date:
                stata_date = datetime.datetime(1960, 1, 1)
                # print(original_date)
                date_split = original_date.split("-")
                #print(len(date_split))    redundant error prevention
#                if not len(date_split) == 3:
#                    print('restarting'+ticker)
#                    continue
                day = int(date_split[2])
                month = int(date_split[1])
                year = int(date_split[0])
                date_time = datetime.datetime(year, month, day)
                time_delta = date_time - stata_date
                time_delta = str(time_delta.days)
                dataList[rowIndex].append(time_delta)
                dataList[rowIndex].append(market)
            else:
                dataList[rowIndex].extend(['Delta', 'market']) #hacky way of adding Delta and market name into the list of variables
        # print(dataList[0])
        headings = dataList[0]
        # print(headings)
      #  print(dataList[1:3])
      #  del dataList[0]
        for n in range(len(headings)):
            data[name][headings[n]] = []
            for row in dataList[1:]:
                # print(headings)
                data[name][headings[n]].append((row[n]))
                #data[name][headings[n]].append('hello')
    # print(data)
    return data


def print_to_csv(dataset, variables):
    if variables == ['']:
        variables = ['Adj Close']
    variables.extend(['Delta', 'market'])
    writingDict = {}
    orderedWriting = OrderedDict(writingDict)
    stock = 0
    for ticker in dataset:
        for column in dataset[ticker]:
            if column in variables:
                orderedWriting.setdefault('t, ind, Date, n ', [])
                ncolumn = column.replace(" ", "")
                if ncolumn not in orderedWriting['t, ind, Date, n ']:
                    orderedWriting['t, ind, Date, n '].append(ncolumn)
                for n in range(len(dataset[ticker][column]) - 1, -1, -1):
                    row = str(n) + ', ' + ticker
                    orderedWriting.setdefault(row, [])
                    if dataset[ticker]['Date'][n] not in orderedWriting[row]:
                        orderedWriting[row].extend(
                            (dataset[ticker]['Date'][n], str(stock)))
                    orderedWriting[row].append(dataset[ticker][column][
                                               n])
        stock += 1
    writeList = []
    for key, value in orderedWriting.items():
        observations = ",".join(value)
        writing = key + "," + observations
        writeList.append(writing)
#    writeList.insert(-1, writeList[0])
    headings = writeList[0]
    del writeList [0]
    writeString = headings + "\n" + "\n".join(list(reversed(writeList)))
    sheet = open('data.csv', 'w')
    sheet.write(writeString)
    sheet.close()
    return(writeString)


def csv_to_lst(path):
    list = open(path)
    tickers = list.read()
    tickers = tickers.replace(" ", "")
    list = tickers.split(',')
    return list



# startDate = input('Enter starting date (DD/MM/YYYY): ')
endDate = input('Enter final date (DD/MM/YYYY) [Default today]: ')
stock_list_path = input('Enter the path to list of stocks: ')
vars = input('Enter desired variables [Default: Adj Close]: ').split(",")
stockList = csv_to_lst(stock_list_path)
startDate = '09/03/2017'
# endDate = '03/03/2017'
# stockList = ['SPY','BBVA']
vars = ['']
dataDict = downloadData(startDate, endDate, stockList)
print_to_csv(dataDict, vars)
