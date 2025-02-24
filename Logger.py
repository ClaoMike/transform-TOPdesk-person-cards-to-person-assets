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

        log_md_filename = datetime.now().strftime(f"{run_timestamp}.md")
        markdown_log_path = os.path.join(self.log_dir, log_md_filename)

        # Configure logging
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        self.logger = logging.getLogger()

        self.markdown_log = open(markdown_log_path, "w", encoding="utf-8")

        # Write initial markdown metadata
        self.markdown_log.write(f"# Log for {run_timestamp}\n\n")

    def _write_markdown(self, text):
        """Writes text to the markdown log file."""
        self.markdown_log.write(text + "\n")
        self.markdown_log.flush()

    def info(self, message):
        self.logger.info(message)
        self._write_markdown(f"- **INFO**: {message}")

    def warning(self, message):
        self.logger.warning(message)
        self._write_markdown(f"- **WARNING**: {message}")

    def error(self, message):
        self.logger.error(message)
        self._write_markdown(f"- **ERROR**: {message}")

    def newline(self):
        self.logger.handlers[0].stream.write("\n")
        self._write_markdown("\n")

    def array(self, array, array_title="No data"):
        self.newline()
        self.logger.info(f"{array_title}")
        self.logger.info(f"Count: {len(array)}")

        self._write_markdown(f"<details><summary><b>{array_title} (Count: {len(array)})</b></summary>\n")
        self._write_markdown("\n```text\n" + "\n".join(map(str, array)) + "\n```\n</details>\n")

        for item in array:
            self.logger.info(item)
        self.newline()

    def dictionary(self, dict_data, dict_title="No data"):
        self.newline()
        self.logger.info(f"{dict_title}")
        self.logger.info(f"Count: {len(dict_data.items())}")

        self._write_markdown(f"<details><summary><b>{dict_title} (Count: {len(dict_data)})</b></summary>\n")
        self._write_markdown("\n```json\n" + "\n".join(f'"{k}": "{v}"' for k, v in dict_data.items()) + "\n```\n</details>\n")

        for key, value in dict_data.items():
            self.logger.info(f"{key}: {value}")
        self.newline()

    def close(self):
        """Closes the markdown log file."""
        self.markdown_log.close()