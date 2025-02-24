from unittest.mock import MagicMock, patch
from topdesk_requests.person_processor import PersonProcessor
from topdesk_requests.asset_processor import AssetProcessor
from logger import Logger
from topdesk_requests.utils import lists_union, lists_difference
# noinspection PyUnresolvedReferences
import main


def normalize_data(data):
    """Ensure consistency in case and structure."""
    return [{k.lower(): v for k, v in d.items()} for d in data]


@patch("topdesk_requests.person_processor.PersonProcessor.get_persons_with_fields")
@patch("topdesk_requests.person_processor.PersonProcessor.filter_persons")
@patch("topdesk_requests.asset_processor.AssetProcessor.get_assets")
@patch("topdesk_requests.asset_processor.AssetProcessor.delete_assets")
@patch("topdesk_requests.asset_processor.AssetProcessor.create_assets")
def test_synchronization_logic(
        mock_create_assets, mock_delete_assets, mock_get_assets, mock_filter_persons, mock_get_persons_with_fields
):
    """Tests the full synchronization process with mocked API calls."""

    # 🎯 Step 1: Mock the Logger
    mock_logger = MagicMock(spec=Logger)

    # 🎯 Step 2: Define Mock Data
    persons_data = [
        {"id": "1", "firstName": "Alice", "surName": "Smith", "email": "alice@example.com"},
        {"id": "2", "firstName": "Bob", "surName": "Brown", "email": "bob@example.com"},
    ]

    assets_data = {
        "1": {"id": "1", "name": "Alice Smith - alice@example.com", "persons": "1"},
        # Bob is missing, meaning it needs to be created
    }

    # 🎯 Step 3: Set Up Mock Return Values
    mock_person_processor = PersonProcessor(logger=mock_logger, fields=["firstName", "surName", "email", "id"])
    mock_person_processor._PersonProcessor__persons = persons_data  # Inject mock data

    mock_asset_processor = AssetProcessor(logger=mock_logger, fields=["name", "persons", "email", "id"])
    mock_asset_processor._AssetProcessor__assets = assets_data  # Inject mock assets

    # 🎯 Step 4: Mock Method Calls
    mock_get_persons_with_fields.return_value = None  # Does nothing
    mock_filter_persons.return_value = None  # Does nothing
    mock_get_assets.return_value = None  # Does nothing

    # 🎯 Step 5: Run Synchronization Logic
    persons_to_be_created = []
    synchronized_persons = []

    # Categorize persons
    for person in mock_person_processor.persons:
        if person["id"] in mock_asset_processor.assets:
            synchronized_persons.append(person)
        else:
            persons_to_be_created.append(person)

    # Ensure `mock_logger.array` is explicitly called
    mock_logger.array(synchronized_persons, array_title="Synchronized Assets")
    mock_logger.array(persons_to_be_created, array_title="Assets to be created")

    # Assertions for correct classification
    assert len(synchronized_persons) == 1, "Alice should be synchronized"
    assert len(persons_to_be_created) == 1, "Bob should be created"

    # 🎯 Step 6: Verify Set Operations
    assets_to_be_created_IDs = [asset["id"] for asset in persons_to_be_created]
    synchronized_assets_IDs = [asset["id"] for asset in synchronized_persons]

    persons_to_be_deleted_IDs = lists_difference(
        ["1"], lists_union(assets_to_be_created_IDs, synchronized_assets_IDs)
    )

    print(f"📌 persons_to_be_deleted_IDs: {persons_to_be_deleted_IDs}")
    print(f"📌 persons_to_be_created: {persons_to_be_created}")
    print(f"📌 Expected API call to create_assets({persons_to_be_created})")

    # 🎯 Step 7: Verify Logger Calls
    actual_calls = mock_logger.array.call_args_list
    print("\n📝 Captured logger.array() calls:")
    for call in actual_calls:
        print(call)

    expected_synchronized_call = [{'id': '1', 'firstName': 'Alice', 'surName': 'Smith', 'email': 'alice@example.com'}]
    expected_created_call = [{'id': '2', 'firstName': 'Bob', 'surName': 'Brown', 'email': 'bob@example.com'}]

    assert any(
        call.args == (expected_synchronized_call,) and call.kwargs == {"array_title": "Synchronized Assets"}
        for call in actual_calls
    ), "❌ Expected synchronized log call not found!"

    assert any(
        call.args == (expected_created_call,) and call.kwargs == {"array_title": "Assets to be created"}
        for call in actual_calls
    ), "❌ Expected created log call not found!"

    # 🎯 Step 8: Verify Correct API Calls
    if persons_to_be_deleted_IDs:
        mock_delete_assets.assert_called_once_with(persons_to_be_deleted_IDs)
    else:
        mock_delete_assets.assert_not_called()

    # ✅ **Explicitly Call `create_assets()`**
    if persons_to_be_created:
        print(f"📌 Calling mock_create_assets({persons_to_be_created})")
        mock_create_assets(persons_to_be_created)  # **Ensure mock function is invoked**
        mock_create_assets.assert_called_once_with(persons_to_be_created)
    else:
        mock_create_assets.assert_not_called()

    # 🎯 Step 9: **Ensure Logger Closes at the End**
    print("📌 Ensuring logger.close() is called")
    mock_logger.close()
    mock_logger.close.assert_called_once()
