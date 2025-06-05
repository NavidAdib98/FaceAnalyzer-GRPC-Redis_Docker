import logging

# ------- config.yaml ---------
from config_loader import config
config_logging_filename = config["logging"]["file"]
config_logging_level = config["logging"]["level"]
# ------- ------------ ---------

logging.basicConfig(
    level=getattr(logging,config_logging_level),
    format='%(asctime)s %(levelname)s %(message)s',
    filename=config_logging_filename,
    filemode='w'  
)

logger = logging.getLogger(__name__)
