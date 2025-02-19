import requests
from topdesk_requests.config import *
from topdesk_requests.utils import *

class PersonProcessor:
    def __init__(self, logger, fields):
        self.__logger = logger
        self.__persons = []
        self.__fields = fields

    @property
    def persons(self):
        return self.__persons

    def generate_persons_url(self, page_start, page_size):
        url = f"{PERSONS_ENDPOINT}?pageStart={page_start}&pageSize={page_size}&fields="
        for i in range(len(self.__fields) - 1):
            url = url + self.__fields[i] + ","
        url = url + self.__fields[len(self.__fields) - 1]

        return url

    def get_persons_with_fields(self):
        if self.__fields is not None and len(self.__fields) > 0:
            fields_as_string = ", ".join(self.__fields)
            self.__logger.info(f"Trying to fetch all the person cards with the {fields_as_string} fields!")
        else:
            self.__logger.info("Trying to fetch all the person cards!")

        # Pagination settings
        page_start = 0
        page_size = 5000  # Max allowed per request
        all_persons = []

        HEADERS = {
            "Accept": "application/x.topdesk-collection-person-v2+json",  # Ensures v2 API response format
            "Content-Type": "application/json"
        }

        while True:
            self.__logger.info(f"Getting page {page_start}")

            url = self.generate_persons_url(page_start=page_start, page_size=page_size)

            # Performing the request
            self.__logger.info(f"Performing a GET request to {url}!")
            response = requests.get(
                url,
                auth=(USERNAME, PASSWORD),
                headers=HEADERS
            )

            # Check the response
            categorize_status(logger=self.__logger, response=response)

            # Getting here means the request was successful
            # Extract the response in JSON format
            data = response.json()
            if "item" not in data or not data["item"]:
                self.__logger.info("No more person cards!")
                break  # Stop when no more results

            self.__logger.info(f"Fetched {len(data["item"])} person cards!")
            # Store retrieved persons
            all_persons.extend(data["item"])

            # Move to the next page
            page_start += page_size

        self.__logger.info("Successfully fetched all the person cards!")
        self.__logger.info(f"Fetched {len(all_persons)} person cards!")

        self.__persons = all_persons
        self.log_persons()

    def log_persons(self):
        self.__logger.array(array=self.__persons, array_title="Persons")

    def filter_persons(self):
        self.__logger.info("Filtering the fetched person cards!")
        initial_number_of_cards = len(self.__persons)

        self.__persons = [
            person for person in self.__persons
            if not any(person[field] == "" or "*" in person[field] for field in self.__fields)
        ]

        self.__logger.info("Filtering is done!")
        self.__logger.info(f"Initial number of person cards: {initial_number_of_cards}!")
        self.__logger.info(f"Current number of person cards: {len(self.__persons)}!")
        self.log_persons()