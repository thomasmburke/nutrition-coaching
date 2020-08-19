import pygsheets
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import datetime
import logging
import sys
import base64
from mfp import *
from googlesheets import *

# To deploy run from src/ dir:
# gcloud functions deploy pull-mfp-data --entry-point pull_mfp_data --runtime python37 --trigger-topic mfp-1-topic --timeout 540s --env-vars-file .env.yaml --project <PROJECT_ID>


def daily_mfp_data_update(user: "str", mfpClient: "<class 'myfitnesspal.client.Client'>", gsClient: "< class 'pygsheets.client.Client' >") -> "<class 'pandas.Dataframe'>":
    """
    Summary: Pulls the last 3 days of data for a given user and updates their Google Sheet
    """
    # Get yesterday's date
    yesterday = dt.date(dt.now() - timedelta(1))
    logger.info(f"Yesterday's date: {yesterday}")
    # Get a reference to the nutrition coaching spreadsheet
    spreadsheet = gsClient.open(title=user)
    # Select a specific worksheet from the spreadsheet
    nutritionHistoryWorksheet = spreadsheet.worksheet(
        property='title', value=f"{user}_NUTRITION_HISTORY")
    # Get all ordered information for a particular day and numDays before it
    mfpData = get_multiple_mfp_dicts(
        mfpClient=mfpClient, day=yesterday, numDays=3)
    # Load OrderedDict into a Dataframe
    mfpDf = pd.DataFrame(mfpData, columns=mfpData[0].keys())
    logger.info(mfpDf)
    latestDate = get_latest_date_in_sheet(worksheet=nutritionHistoryWorksheet)
    # New clients will not have a latest date so we don't want to compare dates
    if latestDate is not None:
        # If we already have data for the day we are pulling then we should just overwrite it o/w we need to make space for the new row
        if (latestDate < yesterday):
            logger.info(
                f"yesterday: {yesterday} is < the latest date in the worksheet: {latestDate}, therefore we will insert a row.")
            # Inserts a row underneath the column headers
            nutritionHistoryWorksheet.insert_rows(row=1, number=1, values=None)
        else:
            logger.info(
                f"yesterday: {yesterday} is not < the latest date in the worksheet: {latestDate}, therefore we will not insert a row.")
    # Inserts dailyTotalsDf in worksheet starting from A2
    nutritionHistoryWorksheet.set_dataframe(mfpDf, 'A2', copy_head=False)
    return mfpDf


def copy_weekly_view(user: "str", gsClient: "< class 'pygsheets.client.Client' >") -> "<class 'pandas.Dataframe'>":
    """
    Summary: Copy data from a user's nutrition history to a user's weekly view
    """
    spreadsheet = gsClient.open(title=user)
    # Get a reference to the nutrition history worksheet
    nutritionHistoryWorksheet = spreadsheet.worksheet(
        property='title', value=f"{user}_NUTRITION_HISTORY")
    # 8 rows because the first is the header, then grab all active columns
    weekDf = nutritionHistoryWorksheet.get_as_df(
        start='A1', end=(8, nutritionHistoryWorksheet.cols))
    # Get a reference to the weekly worksheet
    weeklyWorksheet = spreadsheet.worksheet(
        property='title', value=f"{user}_WEEKLY")
    weeklyWorksheet.set_dataframe(weekDf, 'A1')
    return weekDf


def pull_mfp_data(event: "dict", context: "google.cloud.functions.Context"):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    # Add logging config
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout)

    # Set logger
    logger = logging.getLogger(__name__)

    # Get user from pub/sub message
    USER = base64.b64decode(event['data']).decode('utf-8')
    logger.info(f"USER from pub/sub message: {USER}")
    # Create client for communication with myfitnesspal
    mfpClient = initialize_mfp_client(USER)
    # Initialize Google Sheets Client
    gsClient = initialize_gsheet_client()

    # Copy target macro if it has changed
    # TODO: Copy taget macros

    # Daily update from MFP
    daily_mfp_data_update(user=USER, mfpClient=mfpClient, gsClient=gsClient)

    # Copy last week to the WEEKLY worksheet
    copy_weekly_view(user=USER, gsClient=gsClient)
