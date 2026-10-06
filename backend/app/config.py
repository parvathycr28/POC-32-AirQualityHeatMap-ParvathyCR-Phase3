import os

from dotenv import load_dotenv


load_dotenv()


OPENAQ_API_KEY = os.getenv(
    "OPENAQ_API_KEY"
)

OPENAQ_BASE_URL = os.getenv(
    "OPENAQ_BASE_URL",
    "https://api.openaq.org/v3",
)

WORLDPOP_BASE_URL = os.getenv(
    "WORLDPOP_BASE_URL",
    "https://api.worldpop.org/v2",
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000",
)