import pygsheets
import logging
import os

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
