import unittest
from unittest.mock import MagicMock, patch
import requests
from topdesk_requests.person_processor import PersonProcessor  # Adjust if needed
import logger
import main


class TestPersonProcessor(unittest.TestCase):
    """Unit tests for the PersonProcessor class."""

    def setUp(self):
        """Initialize a mock logger and PersonProcessor instance before each test."""
        self.mock_logger = MagicMock(spec=logger.Logger)
        self.fields = ["id", "firstName", "surName", "email"]
        self.processor = PersonProcessor(logger=self.mock_logger, fields=self.fields)

    ## ===========================
    ##  Tests for get_persons_with_fields
    ## ===========================

    @patch("topdesk_requests.person_processor.requests.get")  # Mock API calls
    def test_get_persons_with_fields_success(self, mock_get):
        """Test successful retrieval of person records with pagination."""

        # Simulated API response data
        mock_get.side_effect = [
            MagicMock(
                status_code=200,
                json=lambda: {"item": [
                    {"id": "1", "firstName": "John", "surName": "Doe", "email": "john@example.com"},
                    {"id": "2", "firstName": "Jane", "surName": "Doe", "email": "jane@example.com"}
                ]}
            ),
            MagicMock(status_code=200, json=lambda: {"item": []})  # Simulate end of pagination
        ]

        self.processor.get_persons_with_fields()

        # Assertions
        self.assertEqual(len(self.processor.persons), 2)
        self.mock_logger.info.assert_any_call("Successfully fetched all the person cards!")

    @patch("topdesk_requests.person_processor.requests.get")
    def test_get_persons_with_fields_empty_response(self, mock_get):
        """Test behavior when API returns no persons."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"item": []}  # No results

        self.processor.get_persons_with_fields()

        self.assertEqual(len(self.processor.persons), 0)
        self.mock_logger.info.assert_any_call("No more person cards!")

    @patch("topdesk_requests.person_processor.requests.get")
    def test_get_persons_with_fields_http_error(self, mock_get):
        """Test behavior when API returns an error (e.g., 500 Internal Server Error)."""
        mock_get.return_value.status_code = 500
        mock_get.return_value.text = "Internal Server Error"

        with self.assertRaises(SystemExit):  # categorize_status should raise SystemExit
            self.processor.get_persons_with_fields()

        self.mock_logger.error.assert_any_call("Error 500: Internal Server Error")

    ## ===========================
    ##  Tests for filter_persons
    ## ===========================

    def test_filter_persons_removes_invalid_entries(self):
        """Test that filter_persons removes invalid records with missing or '*' values."""
        self.processor._PersonProcessor__persons = [
            {"id": "1", "firstName": "John", "surName": "Doe", "email": "john@example.com"},
            {"id": "2", "firstName": "Jane", "surName": "*", "email": "jane@example.com"},  # Invalid
            {"id": "3", "firstName": "", "surName": "Smith", "email": "smith@example.com"},  # Invalid
            {"id": "4", "firstName": "Alice", "surName": "Jones", "email": "alice@example.com"}
        ]

        self.processor.filter_persons()

        # Valid persons left: John Doe & Alice Jones
        self.assertEqual(len(self.processor.persons), 2)
        self.assertEqual(self.processor.persons[0]["id"], "1")  # John Doe
        self.assertEqual(self.processor.persons[1]["id"], "4")  # Alice Jones
        self.mock_logger.info.assert_any_call("Filtering is done!")

    def test_filter_persons_no_changes_if_valid(self):
        """Test that filter_persons keeps all valid entries unchanged."""
        self.processor._PersonProcessor__persons = [
            {"id": "1", "firstName": "John", "surName": "Doe", "email": "john@example.com"},
            {"id": "2", "firstName": "Alice", "surName": "Smith", "email": "alice@example.com"}
        ]

        self.processor.filter_persons()

        # Should still have both persons
        self.assertEqual(len(self.processor.persons), 2)
        self.mock_logger.info.assert_any_call("Filtering is done!")

    ## ===========================
    ##  Tests for __generate_persons_url
    ## ===========================

    def test_generate_persons_url(self):
        """Test that the generated URL includes correct pagination and fields."""
        url = self.processor._PersonProcessor__generate_persons_url(page_start=0, page_size=5000)

        self.assertIn("pageStart=0", url)
        self.assertIn("pageSize=5000", url)
        self.assertIn("fields=id,firstName,surName,email", url)


if __name__ == "__main__":
    unittest.main()
