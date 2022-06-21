import base64
import logging
import os

import sentry_sdk
from flask import Flask
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

with open("credentials.json", "w") as file:
    file.write(base64.b64decode(os.getenv("GOOGLE_CREDENTIALS_BASE64")).decode("utf-8"))

sentry_sdk.init(
    os.getenv("SENTRY_URL"),
    traces_sample_rate=1.0,
)
sentry_sdk.set_level("warning")

creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()

app = Flask(__name__)


@app.route("/ping")
def ping():
    return "pong"


@app.route("/spreadsheets/<spreadsheet_id>/cells/<cell>/value")
def get_cell_value(spreadsheet_id, cell):

    try:
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=cell).execute()
        values = result.get("values", [])

        if not values:
            logger.warning("No data found.")
            return "No data found", 502

        try:
            return values[0][0]
        except Exception as err:
            logger.error(f"Result in unexpected format: '{result}'", exc_info=err)
            return "Unexpected response from sheet", 502

    except HttpError as err:
        logger.error(err, exc_info=err)
        return "Error", 502
