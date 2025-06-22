import requests
import threading
import time
import re
import os 
import sys
import asyncio
from pybit import exceptions
from pybit.unified_trading import HTTP
from math import floor
from datetime import datetime , timedelta
from telegram import Update , InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes , ConversationHandler, CallbackContext,CallbackQueryHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps

# Define a common interface for trading
class Trader:
    def __init__(self, symbol, amount):
        self.symbol = symbol
        self.amount = amount
    
    def execute_buy(self):
        """Execute a buy order"""
        raise NotImplementedError("Subclasses must implement execute_buy")
    
    def execute_sell(self):
        """Execute a sell order"""
        raise NotImplementedError("Subclasses must implement execute_sell")
    
    def get_current_price(self):
        """Get current price for the symbol"""
        raise NotImplementedError("Subclasses must implement get_current_price")
    
    def get_account_balance(self):
        """Get account balance"""
        raise NotImplementedError("Subclasses must implement get_account_balance")

# Update BinanceTrader to implement the common interface
class BinanceTrader(Trader):
    def __init__(self, symbol, amount, api_key, api_secret):
        super().__init__(symbol, amount)
        self.client = self._create_client(api_key, api_secret)
    
    def _create_client(self, api_key, api_secret):
        """Create Binance client"""
        # This would use the actual Binance client library
        return {"api_key": api_key, "api_secret": api_secret}
    
    def execute_buy(self):
        """Execute a buy order on Binance"""
        # Implementation for Binance
        print(f"Executing buy order for {self.symbol} on Binance")
        return True
    
    def execute_sell(self):
        """Execute a sell order on Binance"""
        # Implementation for Binance
        print(f"Executing sell order for {self.symbol} on Binance")
        return True
    
    def get_current_price(self):
        """Get current price from Binance"""
        # Implementation for Binance
        return 50000.0  # Example price
    
    def get_account_balance(self):
        """Get account balance from Binance"""
        # Implementation for Binance
        return 1000.0  # Example balance

# Create specialized classes to split Traderbot responsibilities
class OrderExecutor:
    def __init__(self, client, symbol, amount, simulation_flag=1):
        self.client = client
        self.symbol = symbol
        self.amount = amount
        self.simulation_flag = simulation_flag
        
    def execute_order(self, command, last_price=None):
        if command == "Buy":
            side = command
            quantity = float(self.amount)
            return self._place_order(side, quantity, last_price)
        elif command == "Sell":
            side = command
            if self.simulation_flag == 0:  
                pair = self.symbol
                baseCoin = pair[:pair.index('USDT')] 
                prec = self.client.get_coin_info(coin=baseCoin)['result']['rows'][0]['chains'][0]['minAccuracy']
                quantity = self._get_assets(baseCoin)
                quantity = self._truncate_float(quantity, int(prec)) 
            else:
                quantity = float(self.amount)
            return self._place_order(side, quantity, last_price)
        else:
            return None, "Invalid command"
    
    def _place_order(self, side, quantity, last_price):
        try:
            if self.simulation_flag == 0:
                r = self.client.place_order(
                    category="spot",
                    symbol=f"{self.symbol}",
                    side=side,
                    orderType="Market",
                    qty=quantity,
                    marketUnit="baseCoin",
                )
                return True, r['retMsg']
            
            current_utc_time = datetime.utcnow()
            gmt_plus_7_time = current_utc_time + timedelta(hours=7)
            timestamp_of_order = gmt_plus_7_time.strftime("%Y-%m-%d %H:%M:%S")
            return True, "Simulation order placed"
            
        except Exception as e:
            return False, str(e)
    
    def _get_assets(self, coin):
        return get_assets(self.client, coin)
    
    def _truncate_float(self, value, precision):
        if precision > 4:
            precision = precision - 2
        str_value = f"{value:.{precision + 2}f}"
        if '.' in str_value:
            integer_part, decimal_part = str_value.split('.')
            truncated_decimal = decimal_part[:precision]
            return f"{integer_part}.{truncated_decimal}" if truncated_decimal else integer_part
        return str_value

class MarketMonitor:
    def __init__(self, client, symbol):
        self.client = client
        self.symbol = symbol
        
    def get_current_price(self):
        response = self.client.get_tickers(category="spot", symbol=self.symbol)
        return float(response['result']['list'][0]['lastPrice'])
        
    def check_stop_loss(self, last_price, current_price, stop_loss_percent):
        if stop_loss_percent == 0:
            return False
        stop_loss_price = last_price * (1 - (stop_loss_percent / 100))
        return current_price <= stop_loss_price
        
    def check_take_profit(self, last_price, current_price, take_profit_percent):
        if take_profit_percent == 0:
            return False
        take_profit_price = last_price * (1 + (take_profit_percent / 100))
        return current_price >= take_profit_price

class MarketAnalyzer:
    def __init__(self, client, symbol):
        self.client = client
        self.symbol = symbol
    
    def analyze_market_trends(self, timeframe='1h', lookback_periods=14):
        """Analyze market trends using price data"""
        try:
            # Get historical price data
            kline_data = self.client.get_kline(
                category="spot",
                symbol=self.symbol,
                interval=timeframe,
                limit=lookback_periods
            )
            
            if 'result' not in kline_data or 'list' not in kline_data['result']:
                return {'trend': 'unknown', 'strength': 0}
            
            # Extract closing prices
            closes = [float(candle[4]) for candle in kline_data['result']['list']]
            
            # Calculate simple moving averages
            short_ma = sum(closes[-5:]) / 5 if len(closes) >= 5 else sum(closes) / len(closes)
            long_ma = sum(closes) / len(closes)
            
            # Determine trend direction and strength
            trend = 'bullish' if short_ma > long_ma else 'bearish'
            strength = abs((short_ma / long_ma - 1) * 100)
            
            return {
                'trend': trend,
                'strength': strength,
                'short_ma': short_ma,
                'long_ma': long_ma
            }
            
        except Exception as e:
            log_event('error', f"Error analyzing market trends: {e}")
            return {'trend': 'unknown', 'strength': 0}
    
    def get_support_resistance_levels(self, timeframe='1d', lookback_periods=30):
        """Identify support and resistance levels"""
        try:
            # Implementation of support/resistance detection
            # This would be a simplified version
            kline_data = self.client.get_kline(
                category="spot",
                symbol=self.symbol,
                interval=timeframe,
                limit=lookback_periods
            )
            
            if 'result' not in kline_data or 'list' not in kline_data['result']:
                return {'support': [], 'resistance': []}
            
            # Extract high and low prices
            highs = [float(candle[2]) for candle in kline_data['result']['list']]
            lows = [float(candle[3]) for candle in kline_data['result']['list']]
            
            # Simple implementation - just use min/max as support/resistance
            support = min(lows)
            resistance = max(highs)
            
            return {
                'support': support,
                'resistance': resistance
            }
            
        except Exception as e:
            log_event('error', f"Error finding support/resistance: {e}")
            return {'support': [], 'resistance': []}

class MarketDataProcessor:
    def __init__(self, client):
        self.client = client
        
    def get_market_data(self, symbol):
        """Get current market data for a symbol"""
        return self.client.get_tickers(category="spot", symbol=symbol)
        
    def get_current_price(self, symbol):
        """Extract current price from market data"""
        market_data = self.get_market_data(symbol)
        return float(market_data['result']['list'][0]['lastPrice'])
        
    def calculate_price_change(self, symbol, reference_price):
        """Calculate percentage change from reference price"""
        current_price = self.get_current_price(symbol)
        return ((current_price - reference_price) / reference_price) * 100
        
    def get_trade_volume(self, symbol, timeframe='24h'):
        """Get trading volume for a symbol"""
        market_data = self.get_market_data(symbol)
        return float(market_data['result']['list'][0]['volume24h'])

class OrderManager:
    def __init__(self, client, symbol, amount, simulation_flag=1):
        self.client = client
        self.symbol = symbol
        self.amount = amount
        self.simulation_flag = simulation_flag
        self.message_service = MessageService()
    
    def execute_buy_order(self, bot_name, mode):
        """Execute a buy order"""
        quantity = float(self.amount)
        
        # Log the order
        self.message_service.notify_order_executed(
            bot_name=bot_name,
            command="Buy",
            symbol=self.symbol,
            price=self._get_current_price(),
            last_price=0,  # No previous price for buy
            timestamp=self._get_timestamp()
        )
        
        # Execute the order
        if self.simulation_flag == 0:
            return self._place_real_order("Buy", quantity)
        else:
            return True, "Simulation buy order executed"
    
    def execute_sell_order(self, bot_name, mode, last_price):
        """Execute a sell order"""
        if self.simulation_flag == 0:
            quantity = self._get_available_quantity()
        else:
            quantity = float(self.amount)
        
        # Log the order
        current_price = self._get_current_price()
        percentage_change = ((current_price - last_price) / last_price) * 100 if last_price > 0 else 0
        
        result_message = f"☘☘ Profit: +{percentage_change:.2f}%" if percentage_change > 0 else f"❗❗ Loss: {percentage_change:.2f}%"
        
        self.message_service.notify_order_executed(
            bot_name=bot_name,
            command="Sell",
            symbol=self.symbol,
            price=current_price,
            last_price=last_price,
            timestamp=self._get_timestamp()
        )
        
        # Execute the order
        if self.simulation_flag == 0:
            return self._place_real_order("Sell", quantity)
        else:
            return True, "Simulation sell order executed"
    
    def _place_real_order(self, side, quantity):
        """Place a real order through the API"""
        try:
            response = self.client.place_order(
                category="spot",
                symbol=self.symbol,
                side=side,
                orderType="Market",
                qty=quantity,
                marketUnit="baseCoin",
            )
            return True, response['retMsg']
        except Exception as e:
            return False, str(e)
    
    def _get_current_price(self):
        """Get the current price of the symbol"""
        response = self.client.get_tickers(category="spot", symbol=self.symbol)
        return float(response['result']['list'][0]['lastPrice'])
    
    def _get_available_quantity(self):
        """Get available quantity for trading"""
        pair = self.symbol
        baseCoin = pair[:pair.index('USDT')]
        prec = self.client.get_coin_info(coin=baseCoin)['result']['rows'][0]['chains'][0]['minAccuracy']
        quantity = self._get_assets(baseCoin)
        return self._truncate_float(quantity, int(prec))
    
    def _get_assets(self, coin):
        """Get available assets for a specific coin"""
        return get_assets(self.client, coin)
    
    def _truncate_float(self, value, precision):
        """Truncate a float to a specific precision"""
        if precision > 4:
            precision = precision - 2
        str_value = f"{value:.{precision + 2}f}"
        if '.' in str_value:
            integer_part, decimal_part = str_value.split('.')
            truncated_decimal = decimal_part[:precision]
            return float(f"{integer_part}.{truncated_decimal}" if truncated_decimal else integer_part)
        return float(str_value)
    
    def _get_timestamp(self):
        """Get current timestamp in GMT+7"""
        current_utc_time = datetime.utcnow()
        gmt_plus_7_time = current_utc_time + timedelta(hours=7)
        return gmt_plus_7_time.strftime("%Y-%m-%d %H:%M:%S")

bot_token = "000000:00000" # TOKEN EXAMPLE
chat_id = 00000000 # CHAT ID EXAMPLE
domain_name = ""
API_KEY = ""
BB_API_KEY = ""
BB_SECRET_KEY = ""
secret_command = "secret_command"

def log_event(level, message):
    """Log an event at the specified level."""
    if level == 'info':
        logging.info(message)
    elif level == 'debug':
        logging.debug(message)
    elif level == 'error':
        logging.error(message)

def rate_limit(calls_per_second):
    interval = 1.0 / calls_per_second

    def decorator(func):
        last_called = [0.0]

        @wraps(func)
        def wrapped(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < interval:
                time.sleep(interval - elapsed)
            last_called[0] = time.time()
            return func(*args, **kwargs)

        return wrapped

    return decorator

@rate_limit(calls_per_second=5)  
def getmessagedata(storage_key):
    # Construct the URL for the stored message
    url = f"https://api.mailgun.net/v3/domains/{domain_name}/messages/{storage_key}"
    # Make the GET request to retrieve the stored message
    response = requests.get(url, auth=("api", API_KEY))
    # Check the response status
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        Body_plain = data.get("body-plain")
        return Body_plain

def get_assets(client, coin):
    """Get available assets for a specific coin directly from the client"""
    try:
        r = client.get_wallet_balance(accountType="UNIFIED")
        for asset in r.get('result', {}).get('list', [])[0].get('coin', []):
            if asset.get('coin') == coin:
                return float(asset.get('availableToWithdraw', '0.0'))
        return 0.0
    except Exception as e:
        log_event('error', f"Error getting assets: {e}")
        return 0.0

def get_account_balance():
    balance = get_assets(HTTP(api_key=BB_API_KEY, api_secret=BB_SECRET_KEY, recv_window=60000), "USDT")
    balance = round(balance,3)
    return balance

@rate_limit(calls_per_second=5)  
def get_usdt_to_rub(amount):
    """Convert USDT amount to RUB using exchange rate API"""
    if amount is None or amount <= 0:
        log_event('error', f"Invalid amount for conversion: {amount}")
        return 0
        
    try:
        return _fetch_and_calculate_rub_value(amount)
    except requests.exceptions.RequestException as e:
        log_event('error', f"Error fetching exchange rate data: {e}")
        return _fallback_conversion(amount)
    except (KeyError, ValueError) as e:
        log_event('error', f"Error processing exchange rate data: {e}")
        return _fallback_conversion(amount)
    except Exception as e:
        log_event('error', f"Unexpected error in currency conversion: {e}")
        return _fallback_conversion(amount)

def _fetch_and_calculate_rub_value(amount):
    """Fetch exchange rate and calculate RUB value"""
    usdt_to_rub_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/USD" 
    rub_response = requests.get(usdt_to_rub_url)
    
    if rub_response.status_code != 200:
        raise requests.exceptions.RequestException(f"API returned status code {rub_response.status_code}")
        
    exchange_data = rub_response.json()
    usd_to_rub_rate = float(exchange_data['conversion_rates']['RUB'])
    return amount * usd_to_rub_rate

def _fallback_conversion(amount):
    """Fallback conversion using a fixed rate when API fails"""
    # Use a fixed fallback rate (should be updated periodically)
    fallback_rate = 75.0  # Example fallback rate
    log_event('info', f"Using fallback conversion rate: {fallback_rate}")
    return amount * fallback_rate

@rate_limit(calls_per_second=5)
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"  # Optional, use "Markdown" or "HTML" for formatting
    }
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("telegram Message sent successfully")
    else:
        log_event('error', f"Failed to send message")
        print("Failed to send message:", response.text)

def command_filter(command): 

    match = re.search(r'\b(Sell|Buy)\b', command, re.IGNORECASE)

    if match:
        word = match.group()
        word = word[0].upper() + word[1:]
        return word  # Output: sell
    else:
        return 0

# Update Traderbot to implement the common interface
class Traderbot(threading.Thread, Trader):
    _active_threads = []  # Class-level list to store all active threads
    def __init__(self,id_t="Undefined",symbol="BTCUSDT",tp=0.0,sl=0.0,amount=0.00011,mode="Simulation",listener_email="any"):
        threading.Thread.__init__(self)
        Trader.__init__(self, symbol, amount)
        self.stop_thread = False
        self.paused = False  # Flag to control pausing
        self.pause_condition = threading.Condition()  # Condition to manage pausing
        self.name = id_t
        self.symbol = symbol #BTCUSDT , ETHUSDT
        self.amount = amount
        self.mode = (str(mode)).replace(" ", "") # Real , Simulation
        self.running = True  # Flag to control the loop in func1 and func2
        self._last_command_received = "Sell"
        self._last_price = 1.0
        self._accumulated_percentage_change = 0.0
        self._last_buy_price = 0.0
        self.listener_email = listener_email
        self._skip_next_signal = 0
        self.domain_name = domain_name
        self._order_counter = 0
        self._wins = 0 
        self._loses = 0 
        self.take_profit_percent = tp
        self.stop_loss_percent = sl
        if (self.mode == "Real"):
            self._simulation_flag = 0
        elif (self.mode == "Simulation"):
            self._simulation_flag = 1
        self._cl = self._create_client()
        self.order_executor = OrderExecutor(self._cl, self.symbol, self.amount, self._simulation_flag)
        self.market_monitor = MarketMonitor(self._cl, self.symbol)
        self.market_analyzer = MarketAnalyzer(self._cl, self.symbol)

        Traderbot._active_threads.append(self)  # Add this thread to the active threads list

    def _create_client(self):
        """Factory method to create API client"""
        return HTTP(
            api_key=BB_API_KEY,
            api_secret=BB_SECRET_KEY,
            recv_window=60000
        )

    def get_last_price(self):
        return self._last_price
        
    def get_last_command(self):
        return self._last_command_received
        
    def get_order_counter(self):
        return self._order_counter
        
    def get_wins(self):
        return self._wins
        
    def get_losses(self):
        return self._loses
        
    def get_accumulated_percentage_change(self):
        return self._accumulated_percentage_change
        
    def is_simulation(self):
        return self._simulation_flag == 1

    def truncate_float(self,value, precision):
        if ( precision > 4):
            precision = precision - 2
        # Convert to string with enough precision
        str_value = f"{value:.{precision + 2}f}"  # Add extra space to avoid rounding
        # Find the decimal point
        if '.' in str_value:
            integer_part, decimal_part = str_value.split('.')
            # Truncate the decimal part
            truncated_decimal = decimal_part[:precision]
            # Combine back the integer and truncated decimal parts
            return f"{integer_part}.{truncated_decimal}" if truncated_decimal else integer_part
        return str_value

    @rate_limit(calls_per_second=5)  
    def Send_Orders(self):
        while self.running:
            with self.pause_condition:
                while self.paused:
                    self.pause_condition.wait()
            
                try:
                    events = self._fetch_email_events()
                    if events:
                        self._process_email_events(events)
                except Exception as e:
                    log_event('error', f"Exception happened in Send_Orders{e}")
                    send_telegram_message(f"Exception happened in Send_Orders{e}")

            time.sleep(1)

    def _fetch_email_events(self):
        events_url = f"https://api.mailgun.net/v3/{domain_name}/events"
        params = {
            "event": "stored",
            "ascending": "no",
            "recipients": f"{self.listener_email}@{domain_name}",
            "limit": 1
        }
        response = requests.get(events_url, auth=("api", API_KEY), params=params)
        
        if response.status_code == 200:
            return response.json()
        return None

    def _process_email_events(self, data):
        for item in data.get("items", []):
            storage = item.get('storage', {})
            if storage:
                storage_key = storage.get('key')
                if storage_key:
                    self._process_storage_item(storage_key)

    def _process_storage_item(self, storage_key):
        Body_plain_New = getmessagedata(storage_key)
        command = command_filter(Body_plain_New)
        
        if command != self._last_command_received:
            if self._skip_next_signal == 0:
                result = self.Execute_Orders(command)
                if result == 1:
                    return
                send_telegram_message("----------------------------------------")
            else:
                self._skip_next_signal = 0
        
        self._last_command_received = command

    @rate_limit(calls_per_second=5)  
    def Execute_Orders(self,command):
        success, message = self.order_executor.execute_order(command, self._last_price)
        if not success:
            send_telegram_message(f"_{self.name}_ *{self.mode} Mode* : {message}")
            log_event('error', f"_{self.name}_ *{self.mode} Mode* : {message}")
            return 1

        current_utc_time = datetime.utcnow()
        gmt_plus_7_time = current_utc_time + timedelta(hours=7)
        timestamp_of_order = gmt_plus_7_time.strftime("%Y-%m-%d %H:%M:%S")
        self._order_counter = self._order_counter + 1 

        try:
            response = self._cl.get_tickers(category="spot", symbol=f"{self.symbol}")
            current_price = float(response['result']['list'][0]['lastPrice'])
            resultoftrade = "" 
            if(command == "Sell" ):
                percentage_change = ((current_price - self._last_price) / self._last_price) * 100
                self._accumulated_percentage_change += percentage_change
                if percentage_change > 0:
                    resultoftrade = f"☘☘ Profit: +{percentage_change:.2f}%"
                    self._wins+=1
                else:
                    resultoftrade = f"❗❗ Loss: {percentage_change:.2f}%"
                    self._loses+=1

                accumulated_percentage_change_str = f"{self._accumulated_percentage_change:.2f}%"
                send_telegram_message(f"_{self.name}_ Executed `{command}` {self.symbol} at price *{current_price}* . _{resultoftrade}_ || all time : *{accumulated_percentage_change_str}* || Time : *{timestamp_of_order}* ")

            else:
                send_telegram_message(f"_{self.name}_ Executed `{command}` {self.symbol} at price *{current_price}* . last price : *{self._last_price}* || Time : *{timestamp_of_order}*")
                self._last_buy_price = current_price
            self._last_price = current_price

        except Exception as e:
            send_telegram_message(f"_{self.name}_ *{self.mode} Mode* Unexpected error: {e}")
            log_event('error',f"_{self.name}_ *{self.mode} Mode* Unexpected error: {e}")
            return 1

        return 0
        
    def Monitor_SL_TP(self):
        while self.running:
            with self.pause_condition:
                while self.paused:
                    self.pause_condition.wait()
                try:
                    current_price = self.market_monitor.get_current_price()
                    if self.market_monitor.check_stop_loss(self._last_price, current_price, self.stop_loss_percent):
                        send_telegram_message(f" _{self.name}_ *Stop LOSS* 🔴! : hit by *{self.stop_loss_percent}%*")
                        self.Execute_Orders("Sell")
                        self._skip_next_signal = 1
                    if self.market_monitor.check_take_profit(self._last_price, current_price, self.take_profit_percent):
                        send_telegram_message(f" _{self.name}_ *TAKE PROFIT* 🟦 ! : hit by *{self.take_profit_percent}%*")
                        self.Execute_Orders("Sell")
                        self._skip_next_signal = 1
                except Exception as e:
                    send_telegram_message(f"{e}")
            time.sleep(10)

    def manual_trigger(self,command):
        if (command == "Buy"):
            self.Execute_Orders("Buy")
            self._skip_next_signal = 1
            send_telegram_message(f" _{self.name}_ Executed manual_trigger)")
        elif(command == "Sell"):
            self.Execute_Orders("Sell")
            self._skip_next_signal = 1
            send_telegram_message(f" _{self.name}_ Executed manual_trigger)")

    @rate_limit(calls_per_second=5)  
    def listlast_commands(self):
        listlast_commands = []
        events_url = f"https://api.mailgun.net/v3/{domain_name}/events"

        params = {
            "event": "stored",  
            "ascending": "no",   
            "recipients": f"{self.listener_email}@{self.domain_name}",
            "limit": 20
        }
        response = requests.get(events_url, auth=("api", API_KEY), params=params)

        if response.status_code == 200:
            data = response.json()
            last_message_body = None
            for item in data.get("items", []):
                timestamp = item.get('timestamp')
                message = item.get('message', {})
                storage = item.get('storage', {})  # Get the storage details
                if storage:
                    storage_key = storage.get('key')  # Get the storage key
                    if storage_key:
                        Body_plain_New = getmessagedata(storage_key)
                        command = Body_plain_New
                        dt_object = datetime.fromtimestamp(timestamp)  
                        dt_object += timedelta(hours=4)
                        listlast_commands.append(f"{command}  {dt_object}")

        return listlast_commands

    def run(self):
        send_telegram_message(f"BOT *{self.name}* Started ```{self.symbol} {self.amount} {self.mode} {self.listener_email} ```")

        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(self.Send_Orders)
            future2 = executor.submit(self.Monitor_SL_TP)

            while True:
                try:
                    future1.result(timeout=None)  
                except Exception as e:
                    send_telegram_message(f"Error occurred in send orders: {e}")
                    
                try:
                    future2.result(timeout=None)
                except Exception as e:
                    send_telegram_message(f"Error occurred in monitor sl tp: {e}")

                time.sleep(0.1)  

    def stop(self):
        self.running = False
        Traderbot._active_threads.remove(self)  
        self.resume()  
        send_telegram_message(f"*{self.name}* is Stopping ...")

    def pause(self):
        with self.pause_condition:
            self.paused = True
            send_telegram_message(f"*{self.name}* is Paused")

    def resume(self):
        with self.pause_condition:
            self.paused = False
            self.pause_condition.notify()  
            self.pause_condition.notify()  
            send_telegram_message(f"*{self.name}* is resumed")

    def set_TP(self, take_profit_percent):
        self.take_profit_percent = take_profit_percent

    def set_ST(self, stop_loss_percent):
        self.stop_loss_percent = stop_loss_percent

    def update_parameter(self, parameter_type, value):
        """Update trading parameters (Observer pattern)"""
        if parameter_type == 'take_profit':
            self.take_profit_percent = value
            log_event('info', f"Bot {self.name}: Take profit updated to {value}%")
        elif parameter_type == 'stop_loss':
            self.stop_loss_percent = value
            log_event('info', f"Bot {self.name}: Stop loss updated to {value}%")

    def execute_buy(self):
        """Execute a buy order using ByBit API"""
        return self.Execute_Orders("Buy")
    
    def execute_sell(self):
        """Execute a sell order using ByBit API"""
        return self.Execute_Orders("Sell")
    
    def get_current_price(self):
        """Get current price from ByBit"""
        response = self._cl.get_tickers(category="spot", symbol=self.symbol)
        return float(response['result']['list'][0]['lastPrice'])
    
    def get_account_balance(self):
        """Get account balance from ByBit"""
        return get_account_balance()

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, message, parse_mode="Markdown"):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        response = requests.post(url, json=payload)
        return response.status_code == 200

class MessageService:
    def __init__(self, bot_token=None, chat_id=None):
        # Allow custom token and chat_id or use defaults
        self.bot_token = bot_token or bot_token
        self.chat_id = chat_id or chat_id
        
    def send_message(self, message, parse_mode="Markdown"):
        """Send a message directly without using a notifier"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        try:
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            log_event('error', f"Error sending message: {e}")
            return False

    def notify_bot_started(self, bot_name, symbol, amount, mode, email):
        message = f"BOT *{bot_name}* Started ```{symbol} {amount} {mode} {email} ```"
        return self.send_message(message)

    def notify_order_executed(self, bot_name, command, symbol, price, last_price, timestamp):
        message = f"_{bot_name}_ Executed `{command}` {symbol} at price *{price}* . last price : *{last_price}* || Time : *{timestamp}*"
        return self.send_message(message)

    def notify_error(self, bot_name, mode, error_message):
        message = f"_{bot_name}_ *{mode} Mode* Unexpected error: {error_message}"
        return self.send_message(message)

def get_active_threads():
    if not Traderbot._active_threads:
        return []
    return [thread.name for thread in Traderbot._active_threads]

botlists = []
selected_bot_name = None
NAME, DETAILS, EMAIL, SIMORREAL, GET_TP, GET_SL, CHOICE = range(7)

def start_new_bot(user_data):
    details = user_data['details']
    name = user_data['name']
    email = user_data['email']
    simorreal = str(user_data['simorreal'])
    get_tp = user_data['get_tp']
    get_sl = user_data['get_sl']
    symbol, amount_str = details.split()
    amount = float(amount_str)
    new_bot = Traderbot(id_t=name,symbol=symbol,tp=get_tp, sl=get_sl , amount=amount,mode=simorreal,listener_email=email)
    botlists.append(user_data['name'])
    new_bot.start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) in user_manager.users:
        await update.message.reply_text("Hello! You're authorized to use this bot.")
        print("someone clicked start")
    else:
        await update.message.reply_text("You're not authorized to use this bot.")

async def create_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if str(update.message.chat_id) in user_manager.users:
        await update.message.reply_text("Please enter your new bot name  :")
        return NAME
    else:
        await update.message.reply_text("You're not authorized to use this bot.")

async def get_name(update: Update, context: CallbackContext) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Please enter your bot config in the following format : BTCUSDT 0.000110")
    return DETAILS

async def get_details(update: Update, context: CallbackContext) -> int:
    context.user_data['details'] = update.message.text
    await update.message.reply_text("Please enter your bot email listener : ")
    return EMAIL

async def get_email(update: Update, context: CallbackContext) -> int:
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Please enter mode : (Simulation/Real) ")
    return SIMORREAL

async def get_simorreal(update: Update, context: CallbackContext) -> int:
    context.user_data['simorreal'] = update.message.text
    await update.message.reply_text("Please enter Take profit percentage [write 0 for none set ]:")
    return GET_TP

async def get_tp(update: Update, context: CallbackContext) -> int:
    context.user_data['get_tp'] = float(update.message.text)
    await update.message.reply_text("Please enter stop loss percentage [write 0 for none set ]:")
    return GET_SL

async def get_sl(update: Update, context: CallbackContext) -> int:
    context.user_data['get_sl'] = float(update.message.text)
    details = context.user_data['details']
    name = context.user_data['name']
    email = context.user_data['email']
    simorreal = context.user_data['simorreal']
    get_tp = context.user_data['get_tp']
    get_sl = context.user_data['get_sl']
    await update.message.reply_text(f"Thank you! Here's what you entered:\nBot : {name}\nconfig: {details} email : {email} MODE : {simorreal} TP: {get_tp}SL: {get_sl}\n is all correct to start the bot ?(y)")
    return CHOICE 

async def start_new_bot_handle(update: Update, context: CallbackContext) -> int:
    context.user_data['choice'] = update.message.text
    if (context.user_data['choice'] == "y"):
        context.user_data.pop('choice', None)
        start_new_bot(context.user_data)
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("creating a bot canceled.")
    return ConversationHandler.END

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    if str(update.message.chat_id) in user_manager.users:
        balance = get_account_balance()
        balance_rub = get_usdt_to_rub(balance)
        send_telegram_message(f"```Account USD : {balance}\n RUB : {balance_rub} ```")            

    else:
        await update.message.reply_text("You're not authorized to use this bot.")

async def set_tp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) in user_manager.users:
        keyboard = [
            [InlineKeyboardButton(f"{val}%", callback_data=f"take_profit_{val}")]
            for val in stop_loss_options 
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select a take profit percentage:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("You're not authorized to use this bot.")

async def handle_takeprofit_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if str(query.message.chat_id) == str(chat_id):
        selected_take_profit = float(query.data.split('_')[2])
        await query.edit_message_text(text=f"take profit set to {selected_take_profit}%")
        set_tp_func(selected_take_profit)
    else:
        await query.edit_message_text(text="You're not authorized to use this bot.")

def set_tp_func(selected_take_profit):
    trading_params = TradingParameters()
    
    for thread in Traderbot._active_threads:
        trading_params.register_observer(thread)
    
    trading_params.set_take_profit(selected_take_profit)

async def set_st(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) in user_manager.users:
        keyboard = [
            [InlineKeyboardButton(f"{val}%", callback_data=f"stop_loss_{val}")]
            for val in stop_loss_options
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select a stop-loss percentage:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("You're not authorized to use this bot.")

async def handle_stoploss_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if str(query.message.chat_id) == str(chat_id):
        selected_stop_loss = float(query.data.split('_')[2])
        await query.edit_message_text(text=f"Stop-loss set to {selected_stop_loss}%")
        set_st_func(selected_stop_loss)
    else:
        await query.edit_message_text(text="You're not authorized to use this bot.")

def set_st_func(selected_stop_loss):
    trading_params = TradingParameters()
    
    for thread in Traderbot._active_threads:
        trading_params.register_observer(thread)
    
    trading_params.set_stop_loss(selected_stop_loss)

async def list_signals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    if str(update.message.chat_id) in user_manager.users:
        list_signals_func(selected_bot_name)
    else:
        await update.message.reply_text("You're not authorized to use this bot.")

def list_signals_func(bot_name):
    for thread in Traderbot._active_threads:
        if thread.name==bot_name:
            listx = thread.listlast_commands()
            send_telegram_message(f"{listx}")

async def list_bots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) in user_manager.users:
        if not not botlists:
            keyboard = [
                [InlineKeyboardButton(f"{val}", callback_data=f"select_bot_{val}")]
                for val in botlists
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("List of running bots :", reply_markup=reply_markup)
        else:
             await update.message.reply_text("You do not have any active bots")
    else:
        await update.message.reply_text("You're not authorized to use this bot.")

async def select_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global selected_bot_name  
    query = update.callback_query
    await query.answer()
    if str(query.message.chat_id) in user_manager.users:
        selected_bot_name = str(query.data.split('_')[2])
        await query.edit_message_text(text=f"Now {selected_bot_name} is the selected bot. You may execute now /show_bot_status or /halt_bot or /trigger_signal or others. ")
    else:
        await query.edit_message_text(text="You're not authorized to use this bot.")

async def show_bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    if str(update.message.chat_id) in user_manager.users:
        show_bot_status_func(selected_bot_name)
    else:
        await update.message.reply_text("You're not authorized to use this bot.")

def escape_markdown(text):
    return re.sub(r'([*_`\[\]])', r'\\\1', text)

def show_bot_status_func(bot_name):
    for thread in Traderbot._active_threads:
        if thread.name==bot_name:
            cl = thread._cl
            response = cl.get_tickers(category="spot", symbol=f"{thread.symbol}")
            current_price = float(response['result']['list'][0]['lastPrice'])
            if (thread.get_last_command() == "Buy" or thread.get_order_counter() != 0 ):      
                current_pl = ((current_price*thread.amount) / thread.get_last_price()) - thread.amount
                current_pl = current_pl - (thread.amount * (1 * 00.1 ))
                current_pl_percentage = (current_pl / thread.amount) * 100
                current_pl_percentage = round(current_pl_percentage,3)
                current_pl = current_pl * current_price  
                current_pl = round(current_pl,3)
                current_pl_RUB = get_usdt_to_rub(current_pl)
                current_pl_RUB = round(current_pl_RUB,2)
            else:
                current_pl = 0
                current_pl_RUB = 0
                current_pl_percentage = 0 

            amount_of_trade_in_rub = thread.amount * current_price
            amount_of_trade_in_rub = get_usdt_to_rub(amount_of_trade_in_rub)
            amount_of_trade_in_rub = round(amount_of_trade_in_rub,2)
            Realized_pl = thread.amount * ((thread.get_accumulated_percentage_change() / 100) - (thread.get_order_counter() * 0.001 ))
            Realized_pl_percentage = (Realized_pl / thread.amount) * 100
            Realized_pl_percentage = round(Realized_pl_percentage,3)
            Realized_pl = Realized_pl * current_price
            Realized_pl = round(Realized_pl,3)
            Realized_pl_RUB = get_usdt_to_rub(Realized_pl)
            Realized_pl_RUB = round(Realized_pl_RUB,2)
            if thread.paused == True :
                appended = "Paused🔄"
            else :
                appended = "Running 🟩"

            escaped_email = escape_markdown(thread.listener_email)
            escaped_name = escape_markdown(bot_name)
            message = (f"""BOT *{escaped_name}* is *{appended}* : ```
        - symbol : {thread.symbol}
        - amount : {thread.amount}
        - amount RUB : {amount_of_trade_in_rub}
        - mode : {thread.mode}
        - last_price: {thread.get_last_price()}
        - Current_price: {current_price}
        - Unrealized_PL : {current_pl} USD
        - Unrealized_PL_RUB : {current_pl_RUB} RUB
        - Unrealized_PL_% : {current_pl_percentage} %
        - Realized_pl : {Realized_pl} USD
        - Realized_pl_RUB : {Realized_pl_RUB} RUB
        - Realized_pl_% : {Realized_pl_percentage} %
        - Orders No : {thread.get_order_counter()}
        - Wins : {thread.get_wins()}
        - Losses : {thread.get_losses()}
        - take_profit_percent : {thread.take_profit_percent}
        - stop_loss_percent : {thread.stop_loss_percent}
        - listener_email : {escaped_email}
        - last_command_received : {thread.get_last_command()}
        - skip_next_signal : {thread._skip_next_signal}

                    ```""")
            send_telegram_message(message)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) in user_manager.users:
        await update.message.reply_text(f"You said: {update.message.text}")

async def trigger_signal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.chat_id) in user_manager.users:
        if selected_bot_name:
            keyboard = [
                [
                InlineKeyboardButton("🔵", callback_data=f"trigger_signal_Green"),
                InlineKeyboardButton("🔴", callback_data=f"trigger_signal_Red"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Choose action: (BUY/SELL)", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Select a bot first with /list_bots")          
    else:
        await update.message.reply_text("You're not authorized to use this bot.")

async def handle_trigger_signal_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if str(query.message.chat_id) in user_manager.users:
        if (query.data == "trigger_signal_Green"):
            if selected_bot_name:
                await query.edit_message_text(text=f"🔵 Buying ...")
                for thread in Traderbot._active_threads:
                    if thread.name==selected_bot_name:
                        thread.manual_trigger("Buy")
        
            else:
                await update.message.reply_text("Select a bot first with /list_bots")

        if (query.data == "trigger_signal_Red"):
            if selected_bot_name:
                await query.edit_message_text(text=f"🔴 Selling  ...")
                for thread in Traderbot._active_threads:
                    if thread.name==selected_bot_name:
                        thread.manual_trigger("Sell")
        
            else:
                await update.message.reply_text("Select a bot first with /list_bots")
    else:
        await query.edit_message_text(text="You're not authorized to use this bot.")

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    if str(update.message.chat_id) in user_manager.users:
        if selected_bot_name:
            for thread in Traderbot._active_threads:
                if thread.name==selected_bot_name:
                    thread.stop()
                    botlists.remove(str(selected_bot_name))
        
        else:
            await update.message.reply_text("Select a bot first with /list_bots")     

    else:
        await update.message.reply_text("You're not authorized to use this bot.")

async def resume_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    if str(update.message.chat_id) in user_manager.users:
        if selected_bot_name:
            for thread in Traderbot._active_threads:
                if thread.name==selected_bot_name:
                    thread.resume()
        
        else:
            await update.message.reply_text("Select a bot first with /list_bots")     

    else:
        await update.message.reply_text("You're not authorized to use this bot.")

async def help_general(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    if str(update.message.chat_id) in user_manager.users:
        await update.message.reply_text("/start: Initializes the bot and verifies authorization.\
            /balance: Retrieves account balance in USD and RUB.\
            /create_bot: Prompts the user to configure and start a new trading bot instance.\
            /halt_bot: Pauses the selected bot instance.\
            /resume_bot: Resumes the selected bot instance.\
            /stop_bot: Stops and deletes the selected bot instance.\
            /list_bots: Lists all active bot instances.\
            /show_bot_status: Displays the current status of the selected bot.\
            /list_signals: Shows the last few received trading signals.\
            /set_st: Configures stop-loss for the selected bot instance.\
            /set_tp: Configures take-profit for the selected bot instance.\
            /trigger_signal: Manually triggers a buy or sell command. \
            /secret_command : Changable command to a secret one. to authorize new telegram users to use the bot.")      

    else:
        await update.message.reply_text("You're not authorized to use this bot.")

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    UserManager.add_user(str(update.message.chat_id))
    if str(update.message.chat_id) in user_manager.users:
        await update.message.reply_text("You have been Authorized to use the bot")
    else:
        await update.message.reply_text("command failed")

def run_bot() -> None:
    application = Application.builder().token(bot_token).build()
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('create_bot', create_bot)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_details)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            SIMORREAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_simorreal)],
            GET_TP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tp)],
            GET_SL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sl)],
            CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_new_bot_handle)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(conversation_handler)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("set_tp", set_tp))
    application.add_handler(CommandHandler("set_st", set_st))
    application.add_handler(CommandHandler("list_signals", list_signals))
    application.add_handler(CommandHandler("list_bots", list_bots))
    application.add_handler(CommandHandler("show_bot_status", show_bot_status))
    application.add_handler(CommandHandler("set_st", set_st))
    application.add_handler(CommandHandler("set_tp", set_tp))
    application.add_handler(CommandHandler("stop_bot", stop_bot))
    application.add_handler(CommandHandler("resume_bot", resume_bot))
    application.add_handler(CommandHandler("trigger_signal", trigger_signal))
    application.add_handler(CommandHandler("help", help_general))
    application.add_handler(CommandHandler(f"{secret_command}", add_user))
    application.add_handler(CallbackQueryHandler(handle_stoploss_selection, pattern=r"stop_loss_"))
    application.add_handler(CallbackQueryHandler(handle_takeprofit_selection, pattern=r"take_profit_"))
    application.add_handler(CallbackQueryHandler(handle_trigger_signal_selection, pattern=r"trigger_signal_"))
    application.add_handler(CallbackQueryHandler(select_bot_handler, pattern=r"select_bot_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))  
    application.run_polling()

if __name__ == "__main__":
    run_bot()
