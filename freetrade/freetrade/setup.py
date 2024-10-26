import random
import string
import time

RUN_TIMESTAMP_STR = time.strftime("%Y_%m_%d__%H_%M_%S")

RUN_UNIQUE_ID = "".join(
    random.choices(
        string.ascii_uppercase + string.digits + string.ascii_lowercase, k=10
    )
)
