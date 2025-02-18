import time, datetime
import queue
import pandas as pd
from threading import Thread
from lightweight_charts import Chart

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.client import Contract, Order, ScannerSubscription
from ibapi.tag_value import TagValue
import pytz
from datetime import datetime

# create a queue for data coming from Interactive Brokers API
data_queue = queue.Queue()

# a list for keeping track of any indicator lines
current_lines = []

# initial chart symbol to show
INITIAL_SYMBOL = "EUR"

# settings for live trading vs. paper trading mode
LIVE_TRADING = False
LIVE_TRADING_PORT = 7496
PAPER_TRADING_PORT = 7497
TRADING_PORT = PAPER_TRADING_PORT
if LIVE_TRADING:
    TRADING_PORT = LIVE_TRADING_PORT

# these defaults are fine
DEFAULT_HOST = '127.0.0.1'
DEFAULT_CLIENT_ID = 1

# Client for connecting to Interactive Brokers
class PTLClient(EWrapper, EClient):
     
    def __init__(self, host, port, client_id):
        EClient.__init__(self, self) 
        
        self.connect(host, port, client_id)

        # create a new Thread
        thread = Thread(target=self.run)
        thread.start()

        time.sleep(3)


    

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.order_id = orderId
        print(f"next valid id is {self.order_id}")

    # callback when historical data is received from Interactive Brokers
    def historicalData(self, req_id, bar):
        # creation bar dictionary for each bar received
        date_str = str(bar.date)

        date_part, time_part, tz_str = date_str.split()
        # Parse the datetime portion into a naive datetime object
        naive_dt = datetime.strptime(f"{date_part} {time_part}", "%Y%m%d %H:%M:%S")
        # Localize the naive datetime using the specified timezone
        timezone = pytz.timezone(tz_str)

        data = {
            'Datetime': timezone.localize(naive_dt),
            'Open': bar.open,
            'High': bar.high,
            'Low': bar.low,
            'Close': bar.close,
            'Volume': int(bar.volume)
        }

        # Put the data into the queue
        data_queue.put(data)

    def parse_datetime(dt_str):
        # Split the string into the datetime and timezone parts
        date_part, time_part, tz_str = dt_str.split()
        # Parse the datetime portion into a naive datetime object
        naive_dt = datetime.strptime(f"{date_part} {time_part}", "%Y%m%d %H:%M:%S")
        # Localize the naive datetime using the specified timezone
        timezone = pytz.timezone(tz_str)
        return timezone.localize(naive_dt)

    # callback when all historical data has been received
    def historicalDataEnd(self, reqId, start, end):
        print(f"end of data {start} {end}")
        


    # callback to log order status, we can put more behavior here if needed
    def orderStatus(self, order_id, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print(f"order status {order_id} {status} {filled} {remaining} {avgFillPrice}")    


    # callback for when a scan finishes
    def scannerData(self, req_id, rank, details, distance, benchmark, projection, legsStr):
        super().scannerData(req_id, rank, details, distance, benchmark, projection, legsStr)
        print("got scanner data")
        print(details.contract)

        data = {
            'secType': details.contract.secType,
            'secId': details.contract.secId,
            'exchange': details.contract.primaryExchange,
            'symbol': details.contract.symbol
        }

        print(data)
        
        # Put the data into the queue
        data_queue.put(data)


# called by charting library when the
def get_bar_data(client, symbol, timeframe, end_datetime, duration_str):
    print(f"getting bar data for {symbol} {timeframe}")

    contract = Contract()
    contract.symbol = symbol
    contract.secType = 'CASH'
    contract.exchange = 'IDEALPRO'
    contract.currency = 'USD'
    what_to_show = 'TRADES'
    

    client.reqHistoricalData(1, contract, end_datetime, duration_str, '1 hour', 'BID', 0, 1, False, [])

    time.sleep(25)
    



def get_historical_dataframe(client, symbol, timeframe, end_datetime, duration_str):
    """
    Request historical data for the given symbol and timeframe,
    then poll the data_queue to build a pandas DataFrame.
    """
    # Clear the queue in case there's leftover data
    while not data_queue.empty():
        data_queue.get()

    get_bar_data(client, symbol, timeframe, end_datetime, duration_str)  # this calls client.reqHistoricalData internally

    # Wait for data to arrive; adjust sleep time or add a timeout as needed.
    time.sleep(5)

    bars = []
    try:
        while True:
            # Try to get all available bars from the queue.
            bars.append(data_queue.get_nowait())
    except queue.Empty:
        pass

    if bars:
        df = pd.DataFrame(bars)
        # Optionally set 'Datetime' column as datetime and index it.
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df.set_index('Datetime', inplace=True)
        return df
    else:
        return pd.DataFrame()  # return empty DataFrame if no data



"""

if __name__ == '__main__':
    # create a client object
    client = PTLClient(DEFAULT_HOST, TRADING_PORT, DEFAULT_CLIENT_ID)

    # populate initial chart
    get_bar_data(INITIAL_SYMBOL, '1 hour')

"""


