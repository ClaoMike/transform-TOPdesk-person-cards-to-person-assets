import unittest
from unittest.mock import MagicMock, patch
from topdesk_requests.asset_processor import AssetProcessor
from logger import Logger


class TestAssetProcessor(unittest.TestCase):
    def setUp(self):
        """Set up the test environment with a mocked logger and AssetProcessor instance."""
        self.mock_logger = MagicMock(spec=Logger)
        self.fields = ["name", "persons", "email", "id"]
        self.asset_processor = AssetProcessor(logger=self.mock_logger, fields=self.fields)

    @patch("requests.get")
    def test_get_assets_success(self, mock_get):
        """Test successful retrieval of assets from TOPdesk API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [
            {"persons": "123", "name": "Alice", "email": "alice@example.com"},
            {"persons": "456", "name": "Bob", "email": "bob@example.com"}
        ]}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        self.asset_processor.get_assets()

        self.assertEqual(len(self.asset_processor.assets), 2)
        self.assertIn("123", self.asset_processor.assets)
        self.assertIn("456", self.asset_processor.assets)

        self.mock_logger.info.assert_called()

    @patch("requests.post")
    def test_delete_assets_success(self, mock_post):
        """Test successful deletion of assets."""
        self.asset_processor._AssetProcessor__assets = {
            "123": {"id": "A1", "persons": "123"},
            "456": {"id": "B2", "persons": "456"}
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.asset_processor.delete_assets(["123"])

        mock_post.assert_called_once()
        self.mock_logger.info.assert_called()

    @patch("requests.post")
    def test_create_assets_success(self, mock_post):
        """Test successful creation of a new asset."""
        persons = [{"id": "789", "firstName": "Charlie", "surName": "Smith", "email": "charlie@example.com"}]

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        self.asset_processor.create_assets(persons)

        mock_post.assert_called()
        self.mock_logger.info.assert_called()

    def test_get_assets_persons_ids(self):
        """Test extraction of persons IDs from the stored assets."""
        self.asset_processor._AssetProcessor__assets = {
            "123": {"id": "A1", "persons": "123"},
            "456": {"id": "B2", "persons": "456"}
        }

        result = self.asset_processor.get_assets_persons_ids()
        self.assertEqual(result, ["123", "456"])

    def test_create_asset_id_truncation(self):
        """Test truncation of asset name if it exceeds 60 characters."""
        person = {
            "firstName": "Charlie",
            "surName": "VeryLongSurnameToExceedCharacterLimit",
            "email": "longemail@example.com"
        }

        # Use getattr to access the private method dynamically
        create_asset_id_method = getattr(self.asset_processor, "_AssetProcessor__create_asset_id")

        asset_name = create_asset_id_method(person)

        self.assertTrue(len(asset_name) <= 60)
        self.assertTrue(asset_name.endswith("..."))


if __name__ == "__main__":
    unittest.main()
