import pygsheets
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import datetime
import logging
from mfp import *
from googlesheets import *

USER = "mcarle"
# Get yesterday's date
yesterday = dt.date(dt.now() - timedelta(1))
# Create client for communication with myfitnesspal
mfpClient = initialize_mfp_client()
# Initialize Google Sheets Client
gsClient = initialize_gsheet_client()
# Get all ordered information for a particular day
mfpData = get_ordered_mfp_dict(mfpClient, yesterday)
# Get a reference to the nutrition coaching spreadsheet
spreadsheet = gsClient.open_by_key(
    "1dgwN6dEDscQTOGpIE0tuEt4uvSPb3aQciGuizrxm9iI")
# Select a specific worksheet from the spreadsheet
worksheet = spreadsheet.worksheet(property='title', value=USER)
# Load OrderedDict into a Dataframe
mfpDf = pd.DataFrame([mfpData], columns=mfpData.keys())
print(mfpDf)
# Inserts a row underneath the column headers
worksheet.insert_rows(row=1, number=1, values=None)
# Inserts dailyTotalsDf in worksheet starting from A2
worksheet.set_dataframe(mfpDf, 'A2', copy_head=False)
