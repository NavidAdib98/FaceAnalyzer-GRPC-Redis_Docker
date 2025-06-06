import os
import logging

# ------- environment variables ---------
config_logging_filename = os.getenv("LOGGING_FILE", "./app.log")
config_logging_level = os.getenv("LOGGING_LEVEL", "INFO")
# ------- --------------------- ---------


logging.basicConfig(
    level=getattr(logging,config_logging_level),
    format='%(asctime)s %(levelname)s %(message)s',
    filename=config_logging_filename,
    filemode='w'  
)

logger = logging.getLogger(__name__)
