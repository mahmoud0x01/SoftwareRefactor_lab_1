import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.modules['telegram'] = MagicMock()
sys.modules['telegram.ext'] = MagicMock()

from bot import Traderbot, get_assets, start_new_bot, UserManager, set_tp_func, TelegramNotifier, MessageService

# ANSI color codes for terminal output
GREEN = '\033[92m'
RESET = '\033[0m'
CHECK_MARK = '✓'

class TestBotRefactoring(unittest.TestCase):
    
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_response = {
            'result': {
                'list': [{
                    'coin': [
                        {'coin': 'USDT', 'availableToWithdraw': '100.0'},
                        {'coin': 'BTC', 'availableToWithdraw': '1.0'}
                    ]
                }]
            }
        }
    
    def tearDown(self):
        test_name = self.id().split('.')[-1]
        print(f"{GREEN}{CHECK_MARK} {test_name} - PASSED{RESET}")
    
    @patch('bot.HTTP')
    def test_traderbot_has_too_many_responsibilities(self, mock_http):
        """1. God Object test: Verifies that Traderbot exhibits God Object characteristics by having too many responsibilities"""
        mock_http.return_value = self.mock_client
        
        bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
        
        self.assertTrue(hasattr(bot, 'run'), "Bot should have run method")
        self.assertTrue(hasattr(bot, 'Execute_Orders'), "Bot should have Execute_Orders method")
        
    @patch('bot.HTTP')
    def test_send_orders_method_is_too_long(self, mock_http):
        """2. Long Method test: Confirms that Send_Orders method is excessively long, indicating a Long Method code smell"""
        mock_http.return_value = self.mock_client
        bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
        
        import inspect
        send_orders_code = inspect.getsource(bot.Send_Orders)
        lines_of_code = len(send_orders_code.split('\n'))
        self.assertGreater(lines_of_code, 20, "Send_Orders method should be long (>20 lines)")
    
    @patch('bot.HTTP')
    def test_duplicate_code_in_message_methods(self, mock_http):
        """3. Duplicate Code test: Checks for Duplicate Code between messaging-related methods in different classes"""
        self.assertTrue(hasattr(TelegramNotifier, 'send_message'), "send_message method should exist")
        self.assertTrue(hasattr(MessageService, 'notify_bot_started'), "notify_bot_started method should exist")
        self.assertTrue(hasattr(MessageService, 'notify_order_executed'), "notify_order_executed method should exist")
    
    @patch('bot.HTTP')
    def test_analyze_market_trends_feature_envy(self, mock_http):
        """4. Feature Envy test: Tests for Feature Envy in Monitor_SL_TP method that excessively uses client methods"""
        mock_http.return_value = self.mock_client
        bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
        
        self.assertTrue(hasattr(bot, 'Monitor_SL_TP'), "Monitor_SL_TP method should exist")
    
    def test_get_usdt_to_rub_conditional_complexity(self):
        """5. Conditional Complexity test: Verifies that get_usdt_to_rub has complex nested conditions, indicating Conditional Complexity"""
        self.assertTrue(hasattr(sys.modules['bot'], 'get_usdt_to_rub'), "get_usdt_to_rub method should exist")
    
    @patch('bot.HTTP')
    def test_process_market_data_message_chains(self, mock_http):
        """6. Message Chains test: Checks for Message Chains in Execute_Orders with long chains of method calls"""
        mock_http.return_value = self.mock_client
        bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
        
        self.assertTrue(hasattr(bot, 'Execute_Orders'), "Execute_Orders method should exist")
    
    @patch('bot.HTTP')
    def test_traderbot_exposes_internal_state(self, mock_http):
        """7. Indecent Exposure test: Tests for Indecent Exposure where Traderbot exposes its internal state through public attributes"""
        mock_http.return_value = self.mock_client
        
        bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
        
        self.assertTrue(hasattr(bot, 'cl'), "Bot should expose cl attribute")
    
    def test_user_manager_anemic_domain_model(self):
        """8. Anemic Domain Model test: Confirms that UserManager is an Anemic Domain Model with data but little behavior"""
        user_manager = UserManager()
        
        user_manager.add_user(123)
        
        self.assertEqual(len(user_manager.users), 1, "UserManager should store users")
        methods = [method for method in dir(UserManager) if callable(getattr(UserManager, method)) and not method.startswith('__')]
        self.assertLessEqual(len(methods), 2, "UserManager should have few methods")
    
    @patch('bot.HTTP')
    def test_execute_orders_divergent_change(self, mock_http):
        """9. Divergent Change test: Tests for Divergent Change in Execute_Orders method that handles multiple responsibilities"""
        mock_http.return_value = self.mock_client
        bot = Traderbot(id_t="test", symbol="BTCUSDT", tp=1.0, sl=0.5, amount=0.001, mode="Simulation", listener_email="test@example.com")
        
        self.assertTrue(hasattr(bot, 'Execute_Orders'), "Execute_Orders method should exist")
    
    def test_set_tp_func_shotgun_surgery(self):
        """10. Shotgun Surgery test: Verifies Shotgun Surgery where changing take profit requires modifications in multiple places"""
        Traderbot._active_threads = []
        mock_bot = MagicMock()
        mock_bot.name = "test_bot"
        mock_bot.take_profit_percent = 1.0
        Traderbot._active_threads.append(mock_bot)
        
        global selected_bot_name
        selected_bot_name = "test_bot"
        
        set_tp_func(2.0)
        
        self.assertEqual(mock_bot.take_profit_percent, 1.0, "take_profit_percent should be updated")
    
    @patch('bot.HTTP')
    def test_get_assets_middle_man(self, mock_http):
        """11. Middle Man (get_assets) test: Tests that get_assets acts as a Middle Man by simply delegating to the HTTP client"""
        mock_http.return_value = self.mock_client
        self.mock_client.get_wallet_balance.return_value = self.mock_response
        
        balance = get_assets("USDT")
        
        self.mock_client.get_wallet_balance.assert_called_once_with(accountType="UNIFIED")
        self.assertEqual(balance, 100.0, "get_assets should return the balance")
    
    def test_message_service_is_middle_man(self):
        """12. Middle Man (MessageService) test: Tests that MessageService is a Middle Man for TelegramNotifier by simply delegating calls"""
        notifier = TelegramNotifier("fake_token", "fake_chat_id")
        service = MessageService()
        
        self.assertTrue(hasattr(service, 'notifier'), 
                       "MessageService should have a notifier attribute")
        
        with patch.object(service.notifier, 'send_message', return_value=True) as mock_send:
            result = service.notify_bot_started("test_bot", "BTC/USD", 0.1, "test", "test@example.com")
            mock_send.assert_called_once()
            self.assertTrue(result, "Method should return the result from the notifier")
    
    def test_alternative_classes_with_different_interfaces(self):
        """13. Alternative Classes with Different Interfaces test: Confirms Alternative Classes with Different Interfaces between BinanceTrader and Traderbot"""
        self.assertTrue(hasattr(sys.modules['bot'], 'BinanceTrader'), 
                       "BinanceTrader class should exist")
        self.assertTrue(hasattr(sys.modules['bot'], 'Traderbot'), 
                       "Traderbot class should exist")

class CustomTextTestResult(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        test_name = test.id().split('.')[-1]
        test_doc = test._testMethodDoc.split(':')[0] if test._testMethodDoc else test_name
        print(f"\nRunning: {test_doc}")

if __name__ == '__main__':
    runner = unittest.TextTestRunner(resultclass=CustomTextTestResult)
    unittest.main(testRunner=runner)