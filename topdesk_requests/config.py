"""
Configuration module for environment variables and endpoints for TOPdesk integration.

This module is responsible for:
1. Loading environment variables from a .env file.
2. Accessing and storing those variables in Python variables.
3. Constructing TOPdesk API endpoints for use in other parts of the application.

Usage:
    from topdesk_requests.config import (
        USERNAME,
        PASSWORD,
        PERSONS_ENDPOINT,
        ASSETS_ENDPOINT,
        CREATE_ASSET_ENDPOINT,
        DELETE_ASSETS_ENDPOINT
    )
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access and store environment variables
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# Base URL for the TOPdesk instance
TOPDESK_URL = "https://dlfseeds.topdesk.net/tas/api"

# Endpoint for managing person objects in TOPdesk
PERSONS_ENDPOINT = TOPDESK_URL + "/persons"

# Endpoint for retrieving assets of a particular type (via template ID)
ASSETS_ENDPOINT = TOPDESK_URL + "/assetmgmt/assets/templateId/D1C4D1A8-5C35-4981-A352-E25C7DC24D55"

# Endpoint for creating new assets
CREATE_ASSET_ENDPOINT = TOPDESK_URL + "/assetmgmt/assets"

# Endpoint for bulk deletion of assets
DELETE_ASSETS_ENDPOINT = TOPDESK_URL + "/assetmgmt/assets/delete"