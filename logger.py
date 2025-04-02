import logging
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
