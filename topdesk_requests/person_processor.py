import requests
from topdesk_requests.config import *
from topdesk_requests.utils import *


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
