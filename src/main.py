import pygsheets
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import datetime
import logging
import sys
from mfp import *
from googlesheets import *

# Add logging config
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    stream=sys.stdout)

# Set logger
logger = logging.getLogger(__name__)

USER = "mcarle"
# Get yesterday's date
yesterday = dt.date(dt.now() - timedelta(1))
logger.info(f"Yeserday's date: {yesterday}")
# Create client for communication with myfitnesspal
mfpClient = initialize_mfp_client()
# Initialize Google Sheets Client
gsClient = initialize_gsheet_client()
# Get a reference to the nutrition coaching spreadsheet
spreadsheet = gsClient.open_by_key(
    "1dgwN6dEDscQTOGpIE0tuEt4uvSPb3aQciGuizrxm9iI")
# Select a specific worksheet from the spreadsheet
worksheet = spreadsheet.worksheet(property='title', value=USER)
# Get all ordered information for a particular day and numDays before it
mfpData = get_multiple_mfp_dicts(mfpClient=mfpClient, day=yesterday, numDays=3)
# Load OrderedDict into a Dataframe
mfpDf = pd.DataFrame(mfpData, columns=mfpData[0].keys())
logger.info(mfpDf)
latestDate = get_latest_date_in_sheet(worksheet=worksheet)
# If we already have data for the day we are pulling then we should just overwrite it o/w we need to make space for the new row
if (latestDate < yesterday):
    logger.info(
        f"yesterday: {yesterday} is < the latest date in the worksheet: {latestDate}, therefore we will insert a row.")
    # Inserts a row underneath the column headers
    worksheet.insert_rows(row=1, number=1, values=None)
else:
    logger.info(
        f"yesterday: {yesterday} is not < the latest date in the worksheet: {latestDate}, therefore we will not insert a row.")
# Inserts dailyTotalsDf in worksheet starting from A2
worksheet.set_dataframe(mfpDf, 'A2', copy_head=False)
# print(val)
# gsClient.create
