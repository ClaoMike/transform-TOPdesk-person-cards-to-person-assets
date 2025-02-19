from topdesk_requests.assetprocessor import AssetProcessor
from topdesk_requests.personprocessor import PersonProcessor
from Logger import Logger

logger = Logger()

persons_to_be_deleted = []
persons_to_be_created = []
synchronized_persons = []

# getting all the person cards, together with some fields; then filtering them - no need for entries that have empty value, or contain special characters only, such as *
person_fields = ["firstName", "surName", "email", "id", "employeeNumber"]
person_processor = PersonProcessor(logger=logger, fields=person_fields)
person_processor.get_persons_with_fields()
person_processor.filter_persons()

# getting all the assets, together with some fields
asset_fields = ["name", "persons", "email", "id"]
assetProcessor = AssetProcessor(logger=logger, fields=asset_fields)
assetProcessor.get_assets()

# see what persons need to be created
for person in person_processor.persons:
    if person["id"] in assetProcessor.assets:
        synchronized_persons.append(person)
    else:
        persons_to_be_created.append(person)

logger.array(array=synchronized_persons, array_title="Synchronized Assets")
logger.array(array=persons_to_be_created, array_title="Assets to be created")

# see what assets need to be deleted
assets_to_be_created_IDs_asSet = set(asset["id"] for asset in persons_to_be_created)
synchronized_assets_IDs_asSet = set(asset["id"] for asset in synchronized_persons)
persons_to_be_deleted_IDs_asSet = assetProcessor.get_assets_persons_IDs_as_set() - (assets_to_be_created_IDs_asSet | synchronized_assets_IDs_asSet)

logger.array(array=persons_to_be_deleted_IDs_asSet, array_title="IDs of the persons to be deleted")

# first, we delete what we do not need
assetProcessor.delete_assets(list(persons_to_be_deleted_IDs_asSet))

# then, we create what's new
assetProcessor.create_assets(persons_to_be_created)

# we've reached the end of the script successfully
logger.newline()
logger.info("Import successful!")