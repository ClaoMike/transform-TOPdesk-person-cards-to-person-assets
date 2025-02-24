"""
    This script demonstrates how to synchronize person records from TOPdesk with related 'person' assets.

    High-Level Process:
        1. Fetch and filter person records using `PersonProcessor`.
        2. Fetch existing assets using `AssetProcessor`.
        3. Determine which assets need to be created, deleted, or are already synchronized.
        4. Perform the necessary creation and deletion operations.
        5. Log the entire process to both a .log file and a .md file.

    Requirements:
        - The relevant TOPdesk configuration values (USERNAME, PASSWORD, etc.) are read from environment variables (see topdesk_requests/config.py).
        - The log directory structure is handled by the Logger class.

    Classes Used:
        - Logger: A custom class for logging messages to both a .log and a .md file.
        - PersonProcessor: Retrieves and filters person records from TOPdesk.
        - AssetProcessor: Retrieves, creates, and deletes person-related assets in TOPdesk.

    Functions Used:
        - listsUnion(list1, list2): Returns the union of two lists as a list.
        - listsDifference(list1, list2): Returns the difference of two lists as a list.
"""

from topdesk_requests.asset_processor import AssetProcessor
from topdesk_requests.person_processor import PersonProcessor
from logger import Logger
from topdesk_requests.utils import lists_union, lists_difference

# Instantiate a logger that will manage both a .log file and a .md file.
logger = Logger()

# Prepare collections for different sets of person records
persons_to_be_deleted = []
persons_to_be_created = []
synchronized_persons = []

# Define the fields we want to retrieve for each person
person_fields = ["firstName", "surName", "email", "id", "employeeNumber"]

# Instantiate the PersonProcessor with the required fields
person_processor = PersonProcessor(logger=logger, fields=person_fields)
# Fetch persons from TOPdesk, then filter out invalid records
person_processor.get_persons_with_fields()
person_processor.filter_persons()

# Define the fields we want to retrieve for each asset
asset_fields = ["name", "persons", "email", "id"]

# Instantiate the AssetProcessor with the required fields
assetProcessor = AssetProcessor(logger=logger, fields=asset_fields)
# Fetch existing 'person' assets from TOPdesk
assetProcessor.get_assets()

# Determine which person records already exist as assets (synchronized) or need creation
for person in person_processor.persons:
    # If the person's ID already appears as a key in the AssetProcessor's assets, it's synchronized
    if person["id"] in assetProcessor.assets:
        synchronized_persons.append(person)
    else:
        # Otherwise, this person needs to be created as a new asset
        persons_to_be_created.append(person)

# Log the results of the synchronization check
logger.array(array=synchronized_persons, array_title="Synchronized Assets")
logger.array(array=persons_to_be_created, array_title="Assets to be created")

# Collect IDs of persons who need new assets
assets_to_be_created_IDs = [asset["id"] for asset in persons_to_be_created]
# Collect IDs of persons who are already synchronized
synchronized_assets_IDs = [asset["id"] for asset in synchronized_persons]

# Determine which assets need to be deleted by finding any asset "persons" IDs not in our to-be-created or synchronized lists
persons_to_be_deleted_IDs = lists_difference(
    assetProcessor.get_assets_persons_ids(),
    lists_union(
        assets_to_be_created_IDs,
        synchronized_assets_IDs
    )
)

# Log the IDs of persons whose assets should be deleted
logger.array(array=persons_to_be_deleted_IDs, array_title="IDs of the persons to be deleted")

# Delete out-of-date assets
assetProcessor.delete_assets(persons_to_be_deleted_IDs)

# Create new assets for those persons who lack them
assetProcessor.create_assets(persons_to_be_created)

# Close the logger to finalize .log and .md files
logger.close()

# TODO
#
# 7. Create workflow diagram
# 8. Send logs somewhere
# 9. Publish
#
