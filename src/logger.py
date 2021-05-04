import logging

LOG_FORMAT = "[%(levelname)s][%(asctime)s] - %(message)s"
logging.basicConfig(
    filename="logger.log",
    level=logging.DEBUG,
    format=LOG_FORMAT
)
logger_backend = logging.getLogger("backend")

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(LOG_FORMAT)
console.setFormatter(formatter)

logging.getLogger().addHandler(console)

logger_main = logging.getLogger("main")
