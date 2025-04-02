import requests
from topdesk_requests.config import *
from topdesk_requests.utils import *


class AssetProcessor:
    """
        A class responsible for fetching, creating, and deleting 'person' assets on TOPdesk.

        This class provides the functionality to interact with the TOPdesk API for:
        - Fetching all 'person' assets.
        - Deleting out-of-date 'person' assets.
        - Creating new 'person' assets.

        Attributes:
            __logger (object): A logger instance used for logging information and errors.
            __fields (list): A list of fields (strings) that should be fetched for each asset.
            __assets (dict): Internal storage of assets as a dictionary where the key is the 'persons' field from the asset, and the value is the complete asset information.
    """

    def __init__(self, logger: Logger, fields):
        """
            Initializes the AssetProcessor with a logger and a list of fields to fetch.

           Args:
               logger (object): The logger instance used for logging.
               fields (list): The list of fields to be fetched for each asset.
        """
        self.__logger = logger
        self.__assets: dict = {}
        self.__fields = fields

    @property
    def assets(self):
        """
            Returns the internal dictionary of assets.

            Returns:
                dict: A dictionary of assets keyed by the 'persons' field.
        """
        return self.__assets

    def get_assets(self):
        """
            Fetches all existing person assets from the TOPdesk API.

            This method makes a GET request to the TOPdesk endpoint defined by self.__generate_assets_url(). Upon a successful request, it stores the resulting assets in the internal dictionary (self.__assets).

            Raises:
                HTTPError: Propagated if the request fails, accompanied by logging.
        """
        self.__logger.info("Trying to fetch all the person assets!")

        headers = {
            "Content-Type": "application/json",
        }

        # Construct the URL with the necessary fields
        url = self.__generate_assets_url()

        self.__logger.info(f"Performing a GET request to {url}!")
        response = requests.get(
            url,
            auth=(USERNAME, PASSWORD),
            headers=headers
        )

        # Categorize the response, raising an HTTPError if not successful
        categorize_status(logger=self.__logger, response=response)

        # Parse response JSON to obtain data
        data = response.json()

        # Transform the array of assets into a dictionary
        # where the key is the 'persons' field and value is the entire asset
        self.__assets = {asset['persons']: asset for asset in data["results"]}

        self.__logger.info("Successfully fetched all the person assets!")
        self.__logger.info(f"Fetched {len(self.__assets)} person assets!")

        self.__logger.newline()
        self.__log_assets()

    def get_assets_persons_ids(self):
        """
            Provides a list of 'persons' IDs from the currently fetched assets.

           Returns:
               list: A list of 'persons' values (IDs).
        """
        return [asset["persons"] for asset in self.__assets.values()]

    def delete_assets(self, persons_to_be_deleted_ids):
        """
            Deletes out-of-date assets using the supplied list of person IDs.

            Args:
                persons_to_be_deleted_ids: A set of 'persons' IDs  that need to be deleted from the system.
        """
        self.__logger.info("Delete out-of-date assets!")
        if len(persons_to_be_deleted_ids) == 0:
            self.__logger.info("No assets to delete!")
        else:
            # Gather the 'id' field of each asset that is out-of-date
            assets_to_be_deleted_ids = [
                asset["id"] for _, asset in self.__assets.items() if asset["persons"] in persons_to_be_deleted_ids
            ]

            payload = {
                "unids": assets_to_be_deleted_ids
            }

            headers = {
                "Content-Type": "application/json"
            }

            self.__logger.info(f"Performing a POST request to {DELETE_ASSETS_ENDPOINT}!")
            response = requests.post(
                DELETE_ASSETS_ENDPOINT,
                auth=(USERNAME, PASSWORD),
                headers=headers,
                json=payload  # Automatically converts the Python dictionary to JSON
            )

            # Categorize response and log outcome
            categorize_status(logger=self.__logger, response=response, show_response_text_if_successful=True)
            self.__logger.info(
                "Deletion of the out-of-date assets was a success, check above for details!",
                end_section=True
            )
        self.__logger.newline()

    def create_assets(self, persons):
        """
            Creates new 'person' assets in TOPdesk from a list of person dictionaries.

            Args:
                persons (list): A list of dictionaries, where each dictionary contains the data required to create an asset (e.g., 'firstName', 'surName',  'email', and 'id').
        """
        self.__logger.info("Creating new person assets!")
        if len(persons) == 0:
            self.__logger.info("No new person assets!")
        else:
            # Iterate over each person dict and create an asset
            for person in persons:
                self.__logger.info(f"Create {person}")
                self.__create_asset(person)
                self.__logger.info("Asset created successfully!")
                self.__logger.newline()
            self.__logger.info("Successfully created all the new person assets!")
        self.__logger.newline()

    def __generate_assets_url(self):
        """
            Constructs the URL used to fetch assets, appending the fields to be retrieved.

            Returns:
                str: The constructed URL with the required query parameters.
        """
        # Start with the base endpoint, add default fields
        url = f"{ASSETS_ENDPOINT}?&field=name&field=persons"
        # Append additional fields from self.__fields
        for i in range(len(self.__fields)):
            url = url + f"&field={self.__fields[i]}"

        return url

    def __log_assets(self):
        """
            Logs the current internal state of the assets dictionary using the logger.
       """
        self.__logger.dictionary(dict_data=self.__assets, dict_title="Assets")

    @staticmethod
    def __create_asset_id(person):
        """
            Constructs a concise yet descriptive name for the asset from person data.

           Args:
               person (dict): The dictionary containing personal information (first name, surname, and email).

            Returns:
               str: A string serving as the 'name' field for the new asset.
       """
        # Concatenate firstName, surName and email
        name = person["firstName"] + " " + person["surName"] + " - " + person["email"]
        # Truncate if the length exceeds 60 characters to meet TOPdesk's constraint
        if len(name) > 60:  # Asset ID can have at most 61 characters
            name = name[:57] + "..."

        return name

    def __create_asset(self, person):
        """
                Sends a POST request to the TOPdesk API to create a single person asset.

                Args:
                    person (dict): The dictionary containing personal information (first name,
                        surname, email, and id).
                """
        # Prepare the payload for the API request
        payload = {
            "name": AssetProcessor.__create_asset_id(person),
            "type_id": "D1C4D1A8-5C35-4981-A352-E25C7DC24D55",
            "persons": person["id"],
            "email": person["email"]
        }

        headers = {
            "Content-Type": "application/json"
        }
        self.__logger.info(f"Performing a POST request to {CREATE_ASSET_ENDPOINT}!")
        response = requests.post(
            CREATE_ASSET_ENDPOINT,
            auth=(USERNAME, PASSWORD),
            headers=headers,
            json=payload  # Automatically converts the Python dictionary to JSON
        )

        # Handle the response outcome
        categorize_status(logger=self.__logger, response=response)
