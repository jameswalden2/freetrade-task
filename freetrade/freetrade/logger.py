import logging

from freetrade import RUN_IDENTIFIER

logger = logging.getLogger("freetrade")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

LOGS_FILE_NAME = f"logs/{RUN_IDENTIFIER}.txt"

file_handler = logging.FileHandler(LOGS_FILE_NAME)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
