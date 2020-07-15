import pygsheets
import logging
import os
from datetime import datetime as dt

# Set logger
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']


def initialize_gsheet_client() -> "<class 'pygsheets.client.Client'>":
    '''
    Summary: Initialize Google Sheets Client
    '''
    logger.info('Initializing Google Sheet Client...')
    return pygsheets.authorize(service_file=os.getenv('MFP_SA_PATH'), scopes=SCOPES)


def get_latest_date_in_sheet(worksheet: "<class 'pygsheets.worksheet.Worksheet'>") -> "<class 'datetime.date'>":
    """
    Summary: Gets the latest date for a given worksheet. Assumes that the latest date is the first in the date column
    """
    latestDateString = worksheet.get_value('A2')
    try:
        latestDate = dt.date(dt.strptime(latestDateString, "%Y-%m-%d"))
        logger.info(f"latest date in sheet: {latestDate}")
        return latestDate
    except Exception as e:
        logger.error(
            f"Was not able to convert latestDateString: {latestDateString} to a datetime.date()")
        raise ValueError(str(e))
