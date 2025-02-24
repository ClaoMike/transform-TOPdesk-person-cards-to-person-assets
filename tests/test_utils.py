import unittest
from unittest.mock import MagicMock
from requests import Response
from logger import Logger
from topdesk_requests.utils import categorize_status, lists_union, lists_difference
import main

class TestUtils(unittest.TestCase):
    """Unit tests for categorize_status, lists_union, and lists_difference functions."""

    def setUp(self):
        """Initialize a mock logger before each test."""
        self.mock_logger = MagicMock(spec=Logger)
        self.mock_response = MagicMock(spec=Response)

    ## ===========================
    ##  Tests for categorize_status
    ## ===========================

    def test_categorize_status_success(self):
        """Test successful response (2xx) with and without response text logging."""
        self.mock_response.status_code = 200
        self.mock_response.text = "Success message"

        # Case: show_response_text_if_successful = False
        categorize_status(self.mock_logger, self.mock_response, show_response_text_if_successful=False)
        self.mock_logger.info.assert_called_with("Request was successful! Status code: 200")

        # Case: show_response_text_if_successful = True
        categorize_status(self.mock_logger, self.mock_response, show_response_text_if_successful=True)
        self.mock_logger.info.assert_called_with("Request was successful! Status code: 200, Message: Success message")

    def test_categorize_status_redirect(self):
        """Test 3xx response (redirect) raises SystemExit and logs an error."""
        self.mock_response.status_code = 302
        self.mock_response.text = "Redirect message"

        with self.assertRaises(SystemExit):
            categorize_status(self.mock_logger, self.mock_response)

        self.mock_logger.error.assert_called_with("Error 302: Redirect message")

    def test_categorize_status_client_error(self):
        """Test 4xx response (client error) raises SystemExit and logs an error."""
        self.mock_response.status_code = 404
        self.mock_response.text = "Not Found"

        with self.assertRaises(SystemExit):
            categorize_status(self.mock_logger, self.mock_response)

        self.mock_logger.error.assert_called_with("Error 404: Not Found")

    def test_categorize_status_server_error(self):
        """Test 5xx response (server error) raises SystemExit and logs an error."""
        self.mock_response.status_code = 500
        self.mock_response.text = "Internal Server Error"

        with self.assertRaises(SystemExit):
            categorize_status(self.mock_logger, self.mock_response)

        self.mock_logger.error.assert_called_with("Error 500: Internal Server Error")

    def test_categorize_status_unexpected_error(self):
        """Test unexpected status code logs an error and raises SystemExit."""
        self.mock_response.status_code = 999
        self.mock_response.text = "Unexpected Error"

        with self.assertRaises(SystemExit):
            categorize_status(self.mock_logger, self.mock_response)

        self.mock_logger.error.assert_called_with("Error 999: Unexpected Error")

    ## ===========================
    ##  Tests for lists_union
    ## ===========================

    def test_lists_union_no_duplicates(self):
        """Test union of two lists with no duplicates."""
        result = lists_union([1, 2, 3], [4, 5, 6])
        self.assertCountEqual(result, [1, 2, 3, 4, 5, 6])

    def test_lists_union_with_duplicates(self):
        """Test union of two lists with overlapping values."""
        result = lists_union([1, 2, 3], [3, 4, 5])
        self.assertCountEqual(result, [1, 2, 3, 4, 5])

    def test_lists_union_empty_lists(self):
        """Test union where one or both lists are empty."""
        self.assertEqual(lists_union([], [1, 2, 3]), [1, 2, 3])
        self.assertEqual(lists_union([1, 2, 3], []), [1, 2, 3])
        self.assertEqual(lists_union([], []), [])

    ## ===========================
    ##  Tests for lists_difference
    ## ===========================

    def test_lists_difference_basic(self):
        """Test difference of two lists with some overlapping values."""
        result = lists_difference([1, 2, 3, 4, 5], [3, 4, 6])
        self.assertCountEqual(result, [1, 2, 5])

    def test_lists_difference_no_common_elements(self):
        """Test difference where no elements are common."""
        result = lists_difference([1, 2, 3], [4, 5, 6])
        self.assertCountEqual(result, [1, 2, 3])

    def test_lists_difference_empty_lists(self):
        """Test difference where one or both lists are empty."""
        self.assertEqual(lists_difference([], [1, 2, 3]), [])
        self.assertEqual(lists_difference([1, 2, 3], []), [1, 2, 3])
        self.assertEqual(lists_difference([], []), [])

    def test_lists_difference_all_elements_removed(self):
        """Test difference where all elements are removed."""
        result = lists_difference([1, 2, 3], [1, 2, 3])
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
