import logging
from datetime import datetime
import os

class Logger:
    def __init__(self, log_dir="logs"):
        # if the logs directory does not exist, we create it
        self.log_dir = log_dir

        os.makedirs(self.log_dir, exist_ok=True)

        run_timestamp = datetime.now().strftime("app_%Y-%m-%d_%H-%M-%S")
        self.log_dir = os.path.join(self.log_dir, run_timestamp)
        os.makedirs(self.log_dir, exist_ok=True)

        # Generate a timestamped filename
        log_filename = datetime.now().strftime(f"{run_timestamp}.log")
        log_path = os.path.join(self.log_dir, log_filename)

        # Configure logging
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        self.logger = logging.getLogger()

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def newline(self):
        self.logger.handlers[0].stream.write("\n")

    def array(self, array, array_title="No data"):
        self.newline()
        self.logger.info(f"{array_title}")
        self.logger.info(f"Count: {len(array)}")
        for item in array:
            self.logger.info(item)
        self.newline()

    def dictionary(self, dict, dict_title="No data"):
        self.newline()
        self.logger.info(f"{dict_title}")
        self.logger.info(f"Count: {len(dict.items())}")
        for key, value in dict.items():
            self.logger.info(f"{key}: {value}")
        self.newline()