import requests
import datetime
import logging
from collections import OrderedDict
logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)


def get_stock_info(stockList, companydata):
    data = open(companydata)
    data = open.read()
    data = data.split('\n')
    for line in data:
        line = line.split(',')
        line = [line[0], line[5], line[6]]


def downloadData(start, end, tickerList):
    if not end:
        end = datetime.date.today().strftime("%d/%m/%Y")
    splitStart = start.split('/')
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
    for ticker in tickerList:
        data[ticker] = {}
        url = (
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
        csv = requests.get(url)
        logging.info(url)
        logging.info(csv.text)
        dataList = csv.text.split('\n')
        del dataList[-1]
        for rowIndex in range(len(dataList)):
            dataList[rowIndex] = dataList[rowIndex].split(',')
            original_date = dataList[rowIndex][0]
            if '-' in original_date:
                stata_date = datetime.datetime(1960, 1, 1)
                date_split = original_date.split("-")
                day = int(date_split[2])
                month = int(date_split[1])
                year = int(date_split[0])
                date_time = datetime.datetime(year, month, day)
                time_delta = date_time - stata_date
                time_delta = str(time_delta.days)
                dataList[rowIndex].append(time_delta)
            else:
                dataList[rowIndex].append('Delta')
        headings = dataList[0]
        del dataList[0]
        for n in range(len(headings)):
            data[ticker][headings[n]] = []
            for row in dataList:
                data[ticker][headings[n]].append((row[n]))
    return data


def print_to_csv(dataset, variables):
    if variables == ['']:
        variables = ['Adj Close']
    variables.append('Delta')
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
        writeList.append(str(key + ', ' + ", ".join(value)))
    writeList.insert(-1, writeList[0])
    del writeList[0]
    writeString = "\n".join(list(reversed(writeList)))
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
startDate = '02/03/2017'
# endDate = '03/03/2017'
# stockList = ['SPY','BBVA']
# vars = ['']
dataDict = downloadData(startDate, endDate, stockList)
print_to_csv(dataDict, vars)
