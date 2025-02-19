import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

TOPDESK_URL = "https://dlfseeds.topdesk.net/tas/api"
PERSONS_ENDPOINT = TOPDESK_URL + "/persons"
ASSETS_ENDPOINT = TOPDESK_URL + "/assetmgmt/assets/templateId/D1C4D1A8-5C35-4981-A352-E25C7DC24D55"
CREATE_ASSET_ENDPOINT = TOPDESK_URL + "/assetmgmt/assets"
DELETE_ASSETS_ENDPOINT = TOPDESK_URL + "/assetmgmt/assets/delete"