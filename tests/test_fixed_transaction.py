import unittest
from unittest.mock import Mock, mock_open, patch

from src.fixed_transaction import process_transaction


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.db.get_balance.return_value = 1000

    def test_positive_amount(self):
        opener = mock_open()
        with patch("src.fixed_transaction.open", opener, create=True):
            result = process_transaction(1, 250, self.db)
        self.assertEqual(result, "approved")
        self.db.update_balance.assert_called_once_with(1, 750)
        opener.return_value.write.assert_called_once_with(
            "Transaction finished with status: approved\n"
        )
        opener.return_value.__exit__.assert_called_once_with(None, None, None)

    def test_zero_and_negative_amount(self):
        for amount in [0, -10]:
            with self.subTest(amount=amount):
                opener = mock_open()
                with patch("src.fixed_transaction.open", opener, create=True):
                    result = process_transaction(1, amount, self.db)
                self.assertEqual(result, "pending")
                self.db.get_balance.assert_not_called()
                self.db.update_balance.assert_not_called()
                opener.return_value.write.assert_called_once_with(
                    "Transaction finished with status: pending\n"
                )

    def test_file_context_closes_on_write_error(self):
        opener = mock_open()
        opener.return_value.write.side_effect = OSError("write error")
        with patch("src.fixed_transaction.open", opener, create=True):
            with self.assertRaises(OSError):
                process_transaction(1, 0, self.db)
        opener.return_value.__exit__.assert_called_once()


if __name__ == "__main__":
    unittest.main()
