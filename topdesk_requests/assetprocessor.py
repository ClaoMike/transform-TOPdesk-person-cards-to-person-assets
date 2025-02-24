import requests
from topdesk_requests.config import *
from topdesk_requests.utils import *

class AssetProcessor:
    def __init__(self, logger, fields):
        self.__logger = logger
        self.__assets = []
        self.__fields = fields

    @property
    def assets(self):
        return self.__assets

    def get_assets(self):
        self.__logger.info("Trying to fetch all the person assets!", newSection=True)

        HEADERS = {
            "Content-Type": "application/json",
        }

        url = self.__generate_assets_url()

        self.__logger.info(f"Performing a GET request to {url}!")
        response = requests.get(
            url,
            auth=(USERNAME, PASSWORD),
            headers=HEADERS
        )

        # Check the response
        categorize_status(logger=self.__logger, response=response)

        # Parse response JSON
        data = response.json()

        # transform the array of assets into a hash map, where each item's key is the persons value
        self.__assets = {asset['persons']: asset for asset in data["results"]}

        self.__logger.info("Successfully fetched all the person assets!")
        self.__logger.info(f"Fetched {len(self.__assets)} person assets!", endSection=True)

        self.__logger.newline()
        self.__log_assets()

    def get_assets_persons_IDs(self):
        return [asset["persons"] for asset in self.__assets.values()]

    def delete_assets(self, persons_to_be_deleted_IDs_asSet):
        self.__logger.info("Delete out-of-date assets!", newSection=True)
        if len(persons_to_be_deleted_IDs_asSet) == 0:
            self.__logger.info("No assets to delete!", endSection=True)
        else:
            assets_to_be_deleted_IDs = [
                asset["id"] for _, asset in self.__assets.items() if asset["persons"] in persons_to_be_deleted_IDs_asSet
            ]

            payload = {
                "unids": assets_to_be_deleted_IDs  # Convert set to list
            }

            HEADERS = {
                "Content-Type": "application/json"
            }

            self.__logger.info(f"Performing a POST request to {DELETE_ASSETS_ENDPOINT}!")
            response = requests.post(
                DELETE_ASSETS_ENDPOINT,
                auth=(USERNAME, PASSWORD),
                headers=HEADERS,
                json=payload  # Automatically converts to JSON
            )

            categorize_status(logger=self.__logger, response=response, showResponseTextIfSuccessfull=True)
            self.__logger.info("Deletion of the out-of-date assets was a success, check above for details!", endSection=True)
        self.__logger.newline()

    def create_assets(self, persons):
        self.__logger.info("Creating new person assets!", newSection=True)
        if len(persons) == 0:
            self.__logger.info("No new person assets!", endSection=True)
        else:
            for person in persons:
                self.__logger.info(f"Create {person}", newSection=True)
                self.__create_asset(person)
                self.__logger.info("Asset created successfully!", endSection=True)
                self.__logger.newline()
            self.__logger.info("Successfully created all the new person assets!", endSection=True)
        self.__logger.newline()

    def __generate_assets_url(self):
        url = f"{ASSETS_ENDPOINT}?&field=name&field=persons"
        for i in range(len(self.__fields)):
            url = url + f"&field={self.__fields[i]}"

        return url

    def __log_assets(self):
        self.__logger.dictionary(dict_data=self.__assets, dict_title="Assets")

    def __create_asset_id(self, person):
        name = person["firstName"] + " " + person["surName"] + " - " + person["email"]
        if len(name) > 60: # Asset ID can have at most 61 characters
            name = name[:57] + "..."

        return name

    def __create_asset(self, person):
        payload = {
            "name": self.__create_asset_id(person),
            "type_id": "D1C4D1A8-5C35-4981-A352-E25C7DC24D55",
            "persons": person["id"],
            "email": person["email"]
        }

        HEADERS = {
            "Content-Type": "application/json"
        }
        self.__logger.info(f"Performing a POST request to {CREATE_ASSET_ENDPOINT}!")
        response = requests.post(
            CREATE_ASSET_ENDPOINT,
            auth=(USERNAME, PASSWORD),
            headers=HEADERS,
            json=payload  # Automatically converts to JSON
        )

        categorize_status(logger=self.__logger, response=response)