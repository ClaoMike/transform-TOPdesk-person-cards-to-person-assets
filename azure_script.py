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

from datetime import datetime


class Logger:
    """
        A logging utility class that writes to console..
        """

    def __init__(self):
        """
            Initializes the Logger.
        """
        self.__log("Stated logging!")

    @staticmethod
    def __log(message: str):
        print(f"{datetime.now().strftime("app_%Y-%m-%d_%H-%M-%S")} / {message}")

    def info(self, message):
        """
            Logs an info-level message.

            Args:
               message (str): The message to log.
        """
        self.__log(f"** INFO** {message}")


    def warning(self, message):
        """
            Logs a warning-level message.

           Args:
               message (str): The message to log.
        """
        self.__log(f"** WARNING** {message}")

    def error(self, message):
        """
            Logs an error-level message.

            Args:
                message (str): The message to log.
        """
        self.__log(f"** ERROR** {message}")

    def newline(self):
        """
        Inserts a newline.
        """
        print()

    def array(self, array, array_title="No data"):
        """
            Logs an array of data.

            Args:
                array (list): The data array to log.
                array_title (str): A title for this section of the log. Default: "No data".
        """
        self.info(array_title)
        print(f"Count: {len(array)}")

        # Log each item in the standard logger
        for item in array:
            print(item)
        print()

    def dictionary(self, dict_data, dict_title="No data"):
        """
            Logs a dictionary.

           Args:
               dict_data (dict): The dictionary to log.
               dict_title (str): A title for this section of the log. Default: "No data".
        """
        self.info(f"{dict_title}")
        print(f"Count: {len(dict_data.items())}")

        # Log each key-value pair in the standard logger
        for key, value in dict_data.items():
            print(f"{key}: {value}")
        print()

    def close(self):
        """
            Closes the Markdown log file gracefully, indicating that the import (or run) is complete.
        """
        self.__log(f"** INFO** Logging Done!")

"""
Configuration module for environment variables and endpoints for TOPdesk integration.

This module is responsible for:
1. Loading environment variables from a .env file.
2. Accessing and storing those variables in Python variables.
3. Constructing TOPdesk API endpoints for use in other parts of the application.

Usage:
    from topdesk_requests.config import (
        USERNAME,
        PASSWORD,
        PERSONS_ENDPOINT,
        ASSETS_ENDPOINT,
        CREATE_ASSET_ENDPOINT,
        DELETE_ASSETS_ENDPOINT
    )
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access and store environment variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# Base URL for the TOPdesk instance
TOPDESK_URL = "https://dlfseeds.topdesk.net/tas/api"

# Endpoint for managing person objects in TOPdesk
PERSONS_ENDPOINT = TOPDESK_URL + "/persons"

# Endpoint for retrieving assets of a particular type (via template ID)
ASSETS_ENDPOINT = TOPDESK_URL + "/assetmgmt/assets/templateId/D1C4D1A8-5C35-4981-A352-E25C7DC24D55"

# Endpoint for creating new assets
CREATE_ASSET_ENDPOINT = TOPDESK_URL + "/assetmgmt/assets"

# Endpoint for bulk deletion of assets
DELETE_ASSETS_ENDPOINT = TOPDESK_URL + "/assetmgmt/assets/delete"

from requests import Response

def categorize_status(logger: Logger, response: Response, show_response_text_if_successful=False):
    """
        Categorizes and handles the status code of an HTTP response.

        This function checks the response's status code and logs or raises an error depending on whether the request was successful. By default, successful responses (2xx) are simply logged, but the complete response text can be logged with the 'showResponseTextIfSuccessful' parameter.

        Args:
            logger (object): A logging object that provides the 'info' and 'error' methods.
            response (requests.Response): The response object returned from the HTTP request.
            show_response_text_if_successful (bool, optional): If True, the full response text will be included in the success log. Defaults to False.

        Raises:
            SystemExit: If the status code is not in the 2xx range.
    """
    # If the request was not a success (status code != 2xx), then we halt the program
    match response.status_code:
        case _ if 200 <= response.status_code < 300:
            # Log success, optionally including the response text
            if show_response_text_if_successful:
                logger.info(f"Request was successful! Status code: {response.status_code}, Message: {response.text}")
            else:
                logger.info(f"Request was successful! Status code: {response.status_code}")
        case _ if 300 <= response.status_code < 400:
            logger.error(f"Error {response.status_code}: {response.text}")
            raise SystemExit
        case _ if 400 <= response.status_code < 500:
            logger.error(f"Error {response.status_code}: {response.text}")
            raise SystemExit
        case _ if 500 <= response.status_code < 600:
            logger.error(f"Error {response.status_code}: {response.text}")
            raise SystemExit
        case _:
            logger.error(f"Error {response.status_code}: {response.text}")
            raise SystemExit


def lists_union(list1, list2):
    """
        Returns the union of two lists as a new list, without duplicates.

        This function combines the elements of 'list1' and 'list2' into a single list, discarding any duplicate elements. The order in the resulting list is  not guaranteed.

        Args:
            list1 (list): The first list.
            list2 (list): The second list.

        Returns:
            list: A list containing unique elements from both 'list1' and 'list2'.
    """
    # Convert each list to a set, perform a union operation, then convert back to a list
    return list(set(list1) | set(list2))


def lists_difference(list1, list2):
    """
        Returns the difference of two lists as a new list, removing duplicates.

        This function finds all elements that are present in 'list1' but not in 'list2'. Duplicate elements are removed. The order in the resulting list is not guaranteed.

        Args:
            list1 (list): The list from which elements are subtracted.
            list2 (list): The list whose elements should not appear in the result.

        Returns:
            list: A list of elements present in 'list1' but not in 'list2'.
    """
    # Convert each list to a set, perform a difference operation, then convert back to a list
    return list(set(list1) - set(list2))


import requests


class PersonProcessor:
    """
       A class responsible for fetching, storing, and filtering 'person' records from TOPdesk.

       This class interacts with TOPdesk's persons endpoint to:
       - Retrieve person records (paged) with specified fields.
       - Filter out invalid or incomplete records.

       Attributes:
           __logger (object): A logger instance for standardized logging operations.
           __fields (list): A list of field names (strings) to be retrieved for each person.
           __persons (list): Internal storage of all fetched person records.
    """

    def __init__(self, logger: Logger, fields):
        """
            Initializes the PersonProcessor with a logger and a list of fields to fetch.

            Args:
                logger (object): The logger instance used for logging information and errors.
                fields (list): The list of fields (strings) to be fetched for each person.
        """
        self.__logger = logger
        self.__persons = []
        self.__fields = fields

    @property
    def persons(self):
        """
            Provides access to the currently stored person records.

            Returns:
                list: A list of all fetched and optionally filtered person records.
        """
        return self.__persons

    def get_persons_with_fields(self):
        """
            Retrieves person records from TOPdesk using the configured fields.

            The method supports pagination. It keeps retrieving records (max 5000 per page) until no more records are available.

            Raises:
                HTTPError: Propagated if any GET request to TOPdesk fails. The request status is checked via the 'categorize_status' utility function.
        """
        # Log the fields we intend to fetch, if provided
        if self.__fields is not None and len(self.__fields) > 0:
            fields_as_string = ", ".join(self.__fields)
            self.__logger.info(f"Trying to fetch all the person cards with the {fields_as_string} fields!")
        else:
            self.__logger.info("Trying to fetch all the person cards!")

        # Pagination settings
        page_start = 0
        page_size = 5000  # Max allowed per request
        all_persons = []

        # Define headers for the request (ensures we get V2 format)
        headers = {
            "Accept": "application/x.topdesk-collection-person-v2+json",  # Ensures v2 API response format
            "Content-Type": "application/json"
        }

        # Loop until no more results are returned
        while True:
            self.__logger.info(f"Getting page {page_start}")

            # Construct the URL with pagination and fields
            url = self.__generate_persons_url(page_start=page_start, page_size=page_size)

            # Performing the request
            self.__logger.info(f"Performing a GET request to {url}!")
            response = requests.get(
                url,
                auth=(USERNAME, PASSWORD),
                headers=headers
            )

            # Validate response status
            categorize_status(logger=self.__logger, response=response)

            # Parse JSON response
            data = response.json()

            # If "item" is missing or empty, we've reached the end
            if "item" not in data or not data["item"]:
                self.__logger.info("No more person cards!")
                break  # Stop when no more results

            self.__logger.info(f"Fetched {len(data["item"])} person cards!")
            # Extend our all_persons list with the newly fetched items
            all_persons.extend(data["item"])

            # Increment page_start to fetch the next batch
            page_start += page_size

        self.__logger.info("Successfully fetched all the person cards!")
        self.__logger.info(f"Fetched {len(all_persons)} person cards!")
        self.__logger.newline()

        # Store the complete list of fetched persons internally
        self.__persons = all_persons
        # Log the fetched person records for debugging
        self.__log_persons()

    def filter_persons(self):
        """
            Filters the currently stored person records based on the configured fields.

            Any record where a specified field is empty or contains an asterisk ('*') is discarded. This helps clean up invalid or incomplete data.
        """
        self.__logger.info("Filtering the fetched person cards!")
        initial_number_of_cards = len(self.__persons)

        self.__persons = [
            person for person in self.__persons
            if all(
                person.get(field) not in (None, "") and "*" not in str(person.get(field))
                for field in self.__fields
            )
        ]

        self.__logger.info("Filtering is done!")
        self.__logger.info(f"Initial number of person cards: {initial_number_of_cards}!")
        self.__logger.info(f"Current number of person cards: {len(self.__persons)}!")

        self.__logger.newline()
        self.__log_persons()

    def __generate_persons_url(self, page_start, page_size):
        """
            Constructs the URL for retrieving person records, including pagination and fields.

            Args:
                page_start (int): The starting index (offset) for the records to be fetched.
                page_size (int): The maximum number of records to be fetched per request.

            Returns:
                str: A fully constructed URL to retrieve a page of person records from TOPdesk.
        """
        # Start building the URL with query parameters for pagination
        url = f"{PERSONS_ENDPOINT}?pageStart={page_start}&pageSize={page_size}&fields="
        # Add each field in the fields list, comma-separated
        for i in range(len(self.__fields) - 1):
            url = url + self.__fields[i] + ","
        # Append the last field (without an extra comma)
        url = url + self.__fields[len(self.__fields) - 1]

        return url

    def __log_persons(self):
        """
            Logs the currently stored person records for debugging and traceability.
        """
        self.__logger.array(array=self.__persons, array_title="Persons")


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
            self.__logger.info("Deletion of the out-of-date assets was a success, check above for details!")
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
        name = person["firstName"] + " " + person["surName"] + " / " + person["employeeNumber"] + " / " + person["location"]["name"]
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
            "email": person["email"],
            "location": person["location"]["name"]
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


# Instantiate a logger that will manage both a .log file and a .md file.
logger = Logger()

# Prepare collections for different sets of person records
persons_to_be_deleted = []
persons_to_be_created = []
synchronized_persons = []

# Define the fields we want to retrieve for each person
person_fields = ["firstName", "surName", "email", "id", "employeeNumber", "location", "branch"]

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
