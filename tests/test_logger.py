import unittest
from unittest.mock import patch, mock_open
import logging
import os
from datetime import datetime
from logger import Logger  # Import the Logger class
# noinspection PyUnresolvedReferences
import main


class TestLogger(unittest.TestCase):
    """Unit tests for the Logger class."""

    def setUp(self):
        """Prepare the Logger instance with mocked file handling and logging."""
        self.mock_open = mock_open()
        self.mock_makedirs = patch("os.makedirs").start()  # Mock directory creation
        self.mock_datetime = patch("datetime.datetime").start()
        self.mock_datetime.now.return_value = datetime(2024, 2, 24, 12, 0, 0)  # Fixed timestamp

        # Mock the logger object
        self.mock_logging = patch("logging.getLogger").start()
        self.mock_logger_instance = self.mock_logging.return_value

        # Patch open() to use our mock_open
        self.mock_open_patch = patch("builtins.open", self.mock_open).start()

        # Initialize logger
        self.logger = Logger(log_dir="test_logs")

    def tearDown(self):
        """Stop all patches after each test."""
        patch.stopall()

    ## ===========================
    ##  Tests for Initialization
    ## ===========================

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_logger_initializes_correctly(self, mock_makedirs, mock_open1):
        """Test if Logger creates necessary files and directories correctly."""

        # Reset logging before running the test
        logging.shutdown()
        for handler in logging.getLogger().handlers[:]:
            logging.getLogger().removeHandler(handler)
        logging.getLogger().handlers.clear()

        # Reconfigure logging to ensure basicConfig() works
        logging.basicConfig(level=logging.INFO)

        # Initialize Logger to trigger directory and file creation
        Logger(log_dir="test_logs")

        # Print captured makedirs calls
        print(f"\n🔍 Captured makedirs calls: {mock_makedirs.call_args_list}")

        # Extract created directories and normalize paths
        created_dirs = [os.path.normpath(call[0][0]) for call in mock_makedirs.call_args_list]
        print(f"\n📂 Created directories: {created_dirs}")

        # Dynamically find the log subdirectory
        expected_subdir = next((d for d in created_dirs if "test_logs" in d and "app_" in os.path.basename(d)), None)

        assert expected_subdir is not None, f"❌ Expected log directory was not created! Captured: {created_dirs}"

        # Print all captured open file calls
        print(f"\n📝 Captured file open calls: {mock_open1.call_args_list}")

        # Verify base log directory creation
        mock_makedirs.assert_any_call(os.path.normpath("test_logs"), exist_ok=True)
        mock_makedirs.assert_any_call(expected_subdir, exist_ok=True)

        # Verify markdown file is created
        expected_md_file = os.path.join(expected_subdir, os.path.basename(expected_subdir) + ".md")
        assert any(call[0][0] == expected_md_file for call in mock_open1.call_args_list), \
            f"❌ Markdown file {expected_md_file} was not opened!"

    ## ===========================
    ##  Tests for Logging Methods
    ## ===========================

    def test_info_logs_correctly(self):
        """Test logging an info message to both log and markdown."""
        self.logger.info("Test message")

        self.mock_logger_instance.info.assert_called_with("Test message")
        self.mock_open().write.assert_called_with("- **INFO**: Test message\n")

    def test_warning_logs_correctly(self):
        """Test logging a warning message to both log and markdown."""
        self.logger.warning("Warning message")

        self.mock_logger_instance.warning.assert_called_with("Warning message")
        self.mock_open().write.assert_called_with("- **WARNING**: Warning message\n")

    def test_error_logs_correctly(self):
        """Test logging an error message to both log and markdown."""
        self.logger.error("Error message")

        self.mock_logger_instance.error.assert_called_with("Error message")
        self.mock_open().write.assert_called_with("- **ERROR**: Error message\n")

    ## ===========================
    ##  Tests for Structured Markdown Logging
    ## ===========================

    def test_markdown_section_logging(self):
        """Test if new markdown section starts and ends properly."""
        self.logger.info("Section Start", new_section=True)
        self.mock_open().write.assert_any_call("<details><summary><b>Section Start</b></summary>\n\n")  # Extra \n

        self.logger.info("Section End", end_section=True)
        self.mock_open().write.assert_any_call("- **INFO**: Section End\n")
        self.mock_open().write.assert_any_call("</details>\n\n")  # Extra \n

    def test_log_array(self):
        """Test logging an array with Markdown formatting."""
        self.logger.array(["Item1", "Item2"], "Test Array")

        self.mock_logger_instance.info.assert_any_call("Test Array")
        self.mock_logger_instance.info.assert_any_call("Count: 2")
        self.mock_open().write.assert_any_call("<details><summary><b>Test Array (Count: 2)</b></summary>\n\n")
        self.mock_open().write.assert_any_call("\n```text\nItem1\nItem2\n```\n\n")
        self.mock_open().write.assert_any_call("</details>\n\n")

    def test_log_dictionary(self):
        """Test logging a dictionary with Markdown formatting."""
        test_dict = {"key1": "value1", "key2": "value2"}
        self.logger.dictionary(test_dict, "Test Dictionary")

        self.mock_logger_instance.info.assert_any_call("Test Dictionary")
        self.mock_logger_instance.info.assert_any_call("Count: 2")
        self.mock_open().write.assert_any_call("<details><summary><b>Test Dictionary (Count: 2)</b></summary>\n\n")
        self.mock_open().write.assert_any_call('\n```json\n"key1": "value1"\n"key2": "value2"\n```\n</details>\n\n')

    ## ===========================
    ##  Tests for Newline Insertion
    ## ===========================

    def test_newline_inserts_correctly(self):
        """Test if newline is inserted correctly in both logs."""
        self.logger.newline()

        # Ensure markdown newline is logged
        self.mock_open().write.assert_any_call("\n\n")  # Extra newline now expected

        # Ensure it tries to write to the logger stream
        for handler in self.mock_logger_instance.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.stream.write.assert_any_call("\n")  # Verify console log
                break

    ## ===========================
    ##  Test for Closing Markdown Log
    ## ===========================

    def test_logger_closes_markdown_file(self):
        """Test if the markdown log file closes properly."""
        self.logger.close()

        self.mock_open().write.assert_any_call("- **INFO**: Import successful!\n")
        self.mock_open().close.assert_called()


if __name__ == "__main__":
    unittest.main()
