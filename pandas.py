from pandas_datareader import data, wb
#import pandas_finance as pf
import datetime


def download_data(tickerlist, start, finish):
    splitStart = list(reversed(list(map(int, start.split('/')))))
    splitEnd = list(reversed(list(map(int, finish.split('/')))))
    start = datetime.datetime((*splitStart))
    end = datetime.datetime(*splitEnd)
    data = {}
    for ticker in tickerlist:
        data[ticker] = data.get_data_yahoo(ticker, start, end)
    print(data)

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

download_data(['SPY'],'01/01/2017', '03/03/2017')
