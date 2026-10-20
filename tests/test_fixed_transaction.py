"""Verify both paths, audit preservation and cleanup on write failure."""

from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, mock_open, patch

from src.fixed_transaction import process_transaction


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.db = Mock(spec=["get_balance", "update_balance"])
        self.db.get_balance.return_value = 1000

    def test_positive_amount_updates_balance_and_returns_approved(self):
        opener = mock_open()
        with patch("src.fixed_transaction.open", opener, create=True):
            status = process_transaction("user-1", 250, self.db)
        self.assertEqual(status, "approved")
        self.db.get_balance.assert_called_once_with("user-1")
        self.db.update_balance.assert_called_once_with("user-1", 750)
        opener.assert_called_once_with("audit_log.txt", "a", encoding="utf-8")
        opener.return_value.write.assert_called_once_with(
            "Transaction finished with status: approved\n"
        )
        opener.return_value.__exit__.assert_called_once_with(None, None, None)

    def test_nonpositive_amount_is_pending_without_database_access(self):
        for amount in [0, -1, -100]:
            with self.subTest(amount=amount):
                self.db.reset_mock()
                opener = mock_open()
                with patch("src.fixed_transaction.open", opener, create=True):
                    status = process_transaction("user-1", amount, self.db)
                self.assertEqual(status, "pending")
                self.db.get_balance.assert_not_called()
                self.db.update_balance.assert_not_called()
                opener.return_value.write.assert_called_once_with(
                    "Transaction finished with status: pending\n"
                )

    def test_audit_appends_without_destroying_previous_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.txt"
            path.write_text("Предыдущая запись\n", encoding="utf-8")
            process_transaction("user-1", 0, self.db, audit_path=path)
            process_transaction("user-1", 10, self.db, audit_path=path)
            self.assertEqual(path.read_text(encoding="utf-8"),
                             "Предыдущая запись\n"
                             "Transaction finished with status: pending\n"
                             "Transaction finished with status: approved\n")

    def test_real_audit_file_is_closed_after_return(self):
        opened_files = []

        def tracked_open(*args, **kwargs):
            handle = open(*args, **kwargs)
            opened_files.append(handle)
            return handle

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.txt"
            with patch("src.fixed_transaction.open", tracked_open,
                       create=True):
                process_transaction("user-1", 0, self.db, audit_path=path)
            self.assertEqual(len(opened_files), 1)
            self.assertTrue(opened_files[0].closed)

    def test_write_failure_exits_the_file_context(self):
        opener = mock_open()
        opener.return_value.write.side_effect = OSError("write failed")
        with patch("src.fixed_transaction.open", opener, create=True):
            with self.assertRaisesRegex(OSError, "write failed"):
                process_transaction("user-1", 0, self.db)
        opener.return_value.__exit__.assert_called_once()
        self.assertIs(opener.return_value.__exit__.call_args.args[0], OSError)

    def test_database_failures_are_not_reported_as_success(self):
        for method in ["get_balance", "update_balance"]:
            with self.subTest(method=method):
                db = Mock(spec=["get_balance", "update_balance"])
                db.get_balance.return_value = 100
                getattr(db, method).side_effect = RuntimeError("DB failed")
                opener = mock_open()
                with patch("src.fixed_transaction.open", opener, create=True):
                    with self.assertRaisesRegex(RuntimeError, "DB failed"):
                        process_transaction("user-1", 1, db)
                opener.assert_not_called()

    def test_open_failure_propagates(self):
        with patch("src.fixed_transaction.open", create=True,
                   side_effect=OSError("permission denied")):
            with self.assertRaisesRegex(OSError, "permission denied"):
                process_transaction("user-1", 0, self.db)

    def test_decimal_amount_preserves_decimal_balance(self):
        self.db.get_balance.return_value = Decimal("100.50")
        with patch("src.fixed_transaction.open", mock_open(), create=True):
            process_transaction("user-1", Decimal("0.25"), self.db)
        self.db.update_balance.assert_called_once_with(
            "user-1", Decimal("100.25")
        )


if __name__ == "__main__":
    unittest.main()
