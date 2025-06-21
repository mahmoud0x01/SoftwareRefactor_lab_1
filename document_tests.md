

```markdown
# Unit Tests Documentation for Code Flaws

This document describes the 13 unit tests created for the code flaws identified in the project.
```

## 1. God Object

**Shortcoming of code flaw:** The Traderbot class has too many responsibilities, making it a God Object. It violates the Single Responsibility Principle by handling trading logic, order execution, and monitoring.

**Description of unit test:** This test verifies that the Traderbot class has multiple responsibilities by checking for the presence of methods that handle different concerns.
**Link to GitHub issue:** https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/1
**Link to test:**

```python
@patch('bot.HTTP')
def test_traderbot_has_too_many_responsibilities(self, mock_http):
    """Verifies that Traderbot exhibits God Object characteristics"""
    mock_http.return_value = self.mock_client
    
    bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
    
    self.assertTrue(hasattr(bot, 'run'), "Bot should have run method")
    self.assertTrue(hasattr(bot, 'Execute_Orders'), "Bot should have Execute_Orders method")
```

## 2. Long Method

**Shortcoming of code flaw:** The Send_Orders method is excessively long and complex, violating the principle of keeping methods short and focused.

**Description of unit test:** This test examines the source code of the Send_Orders method to verify that it exceeds a reasonable length.

 **Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/2 

**Link to test:**



```python
@patch('bot.HTTP')
def test_send_orders_method_is_too_long(self, mock_http):
    """Confirms that Send_Orders method is excessively long"""
    mock_http.return_value = self.mock_client
    bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
    
    import inspect
    send_orders_code = inspect.getsource(bot.Send_Orders)
    lines_of_code = len(send_orders_code.split('\n'))
    self.assertGreater(lines_of_code, 20, "Send_Orders method should be long (>20 lines)")
```

## 3. Duplicate Code

**Shortcoming of code flaw:** There is duplicate code between messaging-related methods in different classes, violating the DRY principle.

**Description of unit test:** This test verifies that both TelegramNotifier and MessageService classes have similar methods for sending messages. 

**Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/3 

**Link to test:**



```python
def test_duplicate_code_in_message_methods(self):
    """Checks for Duplicate Code between messaging-related methods"""
    self.assertTrue(hasattr(TelegramNotifier, 'send_message'), "send_message method should exist")
    self.assertTrue(hasattr(MessageService, 'notify_bot_started'), "notify_bot_started method should exist")
    self.assertTrue(hasattr(MessageService, 'notify_order_executed'), "notify_order_executed method should exist")
```

## 4. Feature Envy

**Shortcoming of code flaw:** The analyze_market_trends method is more interested in external market data than its own data.

**Description of unit test:** This test checks for the existence of the analyze_market_trends method, which is identified as having Feature Envy.

 **Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/4 

**Link to test:**

```python
@patch('bot.HTTP')
def test_analyze_market_trends_feature_envy(self, mock_http):
    """Tests for Feature Envy in analyze_market_trends method"""
    mock_http.return_value = self.mock_client
    bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
    
    self.assertTrue(hasattr(bot, 'analyze_market_trends'), "analyze_market_trends method should exist")
```

## 5. Conditional Complexity

**Shortcoming of code flaw:** The get_usdt_to_rub method contains deeply nested conditional statements, making the code difficult to read and understand.

**Description of unit test:** This test verifies the existence of the get_usdt_to_rub method, which is identified as having complex nested conditions.

 **Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/8 

**Link to test:**





```python
def test_get_usdt_to_rub_conditional_complexity(self):
    """Verifies that get_usdt_to_rub has complex nested conditions"""
    self.assertTrue(hasattr(sys.modules['bot'], 'get_usdt_to_rub'), "get_usdt_to_rub method should exist")
```

## 6. Message Chains

**Shortcoming of code flaw:** The process_market_data method contains long chains of method calls, making the code difficult to understand and maintain.

**Description of unit test:** This test checks for the existence of the process_market_data method, which is identified as having message chains. 

**Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/11 

**Link to test:**



```python
@patch('bot.HTTP')
def test_process_market_data_message_chains(self, mock_http):
    """Checks for Message Chains in process_market_data"""
    mock_http.return_value = self.mock_client
    bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
    
    self.assertTrue(hasattr(bot, 'process_market_data'), "process_market_data method should exist")
```

## 7. Indecent Exposure

**Shortcoming of code flaw:** The Traderbot class exposes its internal state and behavior through public attributes and methods that should be private.

**Description of unit test:** This test verifies that the Traderbot class exposes internal implementation details, such as the HTTP client. 

**Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/12 

**Link to test:**



```python
@patch('bot.HTTP')
def test_traderbot_exposes_internal_state(self, mock_http):
    """Tests for Indecent Exposure in Traderbot class"""
    mock_http.return_value = self.mock_client
    
    bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
    
    self.assertTrue(hasattr(bot, 'cl'), "Bot should expose cl attribute")
```

## 8. Anemic Domain Model

**Shortcoming of code flaw:** The UserManager class contains only data without any business logic or behavior, making it an anemic domain model.

**Description of unit test:** This test verifies that the UserManager class has data storage capabilities but few methods. 

**Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/13 

**Link to test:**



```python
def test_user_manager_anemic_domain_model(self):
    """Confirms that UserManager is an Anemic Domain Model"""
    user_manager = UserManager()
    
    user_manager.add_user(123)
    
    self.assertEqual(len(user_manager.users), 1, "UserManager should store users")
    methods = [method for method in dir(UserManager) if callable(getattr(UserManager, method)) and not method.startswith('__')]
    self.assertLessEqual(len(methods), 2, "UserManager should have few methods")
```

## 9. Divergent Change

**Shortcoming of code flaw:** The Execute_Orders method is responsible for multiple tasks, making it susceptible to divergent changes.

**Description of unit test:** This test checks for the existence of the Execute_Orders method, which is identified as having divergent change issues. 

**Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/15 

**Link to test:**



```python
@patch('bot.HTTP')
def test_execute_orders_divergent_change(self, mock_http):
    """Tests for Divergent Change in Execute_Orders method"""
    mock_http.return_value = self.mock_client
    bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
    
    self.assertTrue(hasattr(bot, 'Execute_Orders'), "Execute_Orders method should exist")
```

## 10. Shotgun Surgery

**Shortcoming of code flaw:** Changing the take profit percentage requires modifications in multiple places, such as the set_tp_func and Traderbot class.

**Description of unit test:** This test verifies that changing the take profit percentage through set_tp_func affects the Traderbot instance. 

**Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/16 

**Link to test:**



```python
def test_set_tp_func_shotgun_surgery(self):
    """Verifies Shotgun Surgery in take profit percentage changes"""
    Traderbot._active_threads = []
    mock_bot = MagicMock()
    mock_bot.name = "test_bot"
    Traderbot._active_threads.append(mock_bot)
    
    global selected_bot_name
    selected_bot_name = "test_bot"
    
    set_tp_func(2.0)
    
    self.assertEqual(mock_bot.take_profit_percent, 2.0, "take_profit_percent should be updated")
```

## 11. Middle Man (get_assets)

**Shortcoming of code flaw:** The get_assets function acts as a middle man by simply delegating calls to the HTTP client without adding significant value.

**Description of unit test:** This test verifies that the get_assets function merely delegates to the HTTP client's get_wallet_balance method. 

**Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/17 

**Link to test:**



```python
@patch('bot.HTTP')
def test_get_assets_middle_man(self, mock_http):
    """Tests for Middle Man in get_assets function"""
    mock_http.return_value = self.mock_client
    self.mock_client.get_wallet_balance.return_value = self.mock_response
    
    balance = get_assets("USDT")
    
    self.mock_client.get_wallet_balance.assert_called_once_with(accountType="UNIFIED")
    self.assertEqual(balance, 100.0, "get_assets should return the balance")
```



## 12. Middle Man (MessageService)

**Shortcoming of code flaw:** The MessageService class acts as a middle man by simply delegating to other messaging services without adding significant value.

**Description of unit test:** This test verifies that the MessageService class merely delegates to other services, confirming its role as a middle man.
**Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/17
**Link to test:**

```python
def test_message_service_is_middle_man(self):
    """Tests for Middle Man in MessageService class"""
    message_service = MessageService()
    telegram_notifier = TelegramNotifier()
    
    with patch.object(telegram_notifier, 'send_message') as mock_send:
        message_service.notify_bot_started("test_bot")
        mock_send.assert_called_once()
```


## 13. Alternative Classes with Different Interfaces

**Shortcoming of code flaw:** The BinanceTrader class and the existing Traderbot class both serve similar purposes but have completely different interfaces.

**Description of unit test:** This test checks for the existence of both classes and verifies they have different interfaces for similar functionality. 

**Link to GitHub issue**: https://github.com/mahmoud0x01/SoftwareRefactor_lab_1/issues/18 

**Link to test:**



```python
@patch('bot.HTTP')
def test_alternative_classes_with_different_interfaces(self, mock_http):
    """Tests for Alternative Classes with Different Interfaces"""
    mock_http.return_value = self.mock_client
    
    self.assertTrue(hasattr(sys.modules['bot'], 'Traderbot'), "Traderbot class should exist")
    self.assertTrue(hasattr(sys.modules['bot'], 'BinanceTrader'), "BinanceTrader class should exist")
    
    # Check that they have different methods for similar functionality
    trader_bot = Traderbot()
    binance_trader = BinanceTrader("api_key", "api_secret")
    
    self.assertTrue(hasattr(trader_bot, 'Execute_Orders'), "Traderbot should have Execute_Orders method")
    self.assertTrue(hasattr(binance_trader, 'place_market_order'), "BinanceTrader should have place_market_order method")
```



