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


def add_new_client(user: "str", email: "str") -> "pygsheets.Spreadsheet":
    """
    Summary: Creates & configures all nutrition sheets needed for a new user.
        Creates spreadsheet, worksheets, adds headers, styles headers,
        & shares with the new client
    """
    gsClient = initialize_gsheet_client()
    # Create a new spreadsheet for the new user
    # Folder in Margaux's Drive
    logger.info(f'creating new Google spreadsheet named: {user}')
    gsClient.create(title=user, folder="1ayQ9ERDdEdIgiG8AWHrJ7lbtiJtCLRdk")
    # Get a reference to the newly created spreadsheet
    spreadsheet = gsClient.open(title=user)
    # Add expected worksheets
    logger.info('renaming and adding necessary worksheets...')
    spreadsheet.sheet1.title = f"{user}_WEEKLY"
    spreadsheet.add_worksheet(title=f"{user}_NUTRITION_HISTORY")
    # Add headers to worksheets
    add_headers(gsClient=gsClient, newWorksheet=spreadsheet.worksheet(
        property='title', value=f"{user}_WEEKLY"))
    add_headers(gsClient=gsClient, newWorksheet=spreadsheet.worksheet(
        property='title', value=f"{user}_NUTRITION_HISTORY"))
    # Style column headers on both nutrition worksheets
    style_col_headers(worksheet=spreadsheet.worksheet(
        property='title', value=f"{user}_NUTRITION_HISTORY"))
    style_col_headers(worksheet=spreadsheet.worksheet(
        property='title', value=f"{user}_WEEKLY"))
    # Style Weekly worksheet
    style_weekly_worksheet(worksheet=spreadsheet.worksheet(
        property='title', value=f"{user}_WEEKLY"))
    # Share the spreadsheet with the new user's email
    spreadsheet.share(email_or_domain=email, role='reader', type='user',
                      emailMessage="Welcome to Margaux Carle's nutrition coaching program!\n\nWe will use this Google Sheet to track your nutrition info you provide in MyFitnessPal.")
    return spreadsheet


def add_headers(gsClient: "<class 'pygsheets.client.Client'>", newWorksheet: "<class 'pygsheets.worksheet.Worksheet'>") -> "<class 'pygsheets.worksheet.Worksheet'>":
    """
    Summary: Copy headers from Margaux's worksheet and add them to the new worksheet
    """
    logger.info('adding headers to new worksheet...')
    # Get a reference to Margaux's worksheet
    margauxSpreadsheet = gsClient.open(title="MCARLE")
    # Get a reference to the MCARLE nutrition history worksheet
    margauxWorksheet = margauxSpreadsheet.worksheet(
        property='title', value="MCARLE_NUTRITION_HISTORY")
    # Copy top row of headers
    headerDf = margauxWorksheet.get_as_df(
        start='A1', end=(1, margauxWorksheet.cols))
    # Set headers in new worksheet
    newWorksheet.set_dataframe(headerDf, 'A1')
    return newWorksheet


def style_col_headers(worksheet: "<class 'pygsheets.worksheet.Worksheet'>") -> "<class 'pygsheets.Cell' >":
    """
    Summary: Styles column headers for a particular nutrition worksheet.
        Adds height to header row, bolds text, center aligns text, and sets background color.
    """
    logger.info('styling column headers...')
    worksheet.adjust_row_height(start=1, end=1, pixel_size=40)
    modelCell = worksheet.cell('A1')
    modelCell.set_text_format('bold', True)
    modelCell.color = (0.427, 0.62, 0.922)  # a soft blue
    modelCell.horizontal_alignment = pygsheets.custom_types.HorizontalAlignment.CENTER
    modelCell.vertical_alignment = pygsheets.custom_types.VerticalAlignment.MIDDLE
    worksheet.range('A1:L1', returnas='range').apply_format(modelCell)
    return modelCell


def style_weekly_worksheet(worksheet: "<class 'pygsheets.worksheet.Worksheet'>") -> "<class 'pygsheets.Cell' >":
    """
    Summary: Styles weekly worksheet. Widens meal columns, wraps text,
        and centers vertically and horizontally.
    """
    logger.info('styling WEEKLY worksheet...')
    # Widen meal columns to quarter of the screen
    worksheet.adjust_column_width(start=9, end=12, pixel_size=285)
    # Draft model cell with proper alignment and wrap strategy
    modelCell = worksheet.cell('A1')
    modelCell.wrap_strategy = 'WRAP'
    modelCell.horizontal_alignment = pygsheets.custom_types.HorizontalAlignment.CENTER
    modelCell.vertical_alignment = pygsheets.custom_types.VerticalAlignment.MIDDLE
    worksheet.range('A1:L8', returnas='range').apply_format(modelCell)
    worksheet.range('A1:L8', returnas='range').update_borders(
        top=True, right=True, bottom=True, left=True, inner_horizontal=True, inner_vertical=True, style='SOLID')
    return modelCell


def folder_id_dict(client):
    """
    Summary: Get all folders shared with the service account and create a mapping between their name and id
    """
    folders = {}
    meta_list = client.drive.list()
    for file_meta in meta_list:
        if file_meta['mimeType'] == 'application/vnd.google-apps.folder':
            folders[file_meta['name']] = file_meta['id']
    return folders
