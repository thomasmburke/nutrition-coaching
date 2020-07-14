import myfitnesspal
import pygsheets
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import datetime
import os
from collections import OrderedDict

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          "https://www.googleapis.com/auth/drive"]
USER = "mcarle"
# Get yesterday's date
yesterday = dt.date(dt.now() - timedelta(1))
# Create client for communication with myfitnesspal
mfpClient = myfitnesspal.Client(
    os.getenv('MFP_USERNAME'), password=os.getenv('MFP_PASSWORD'))
# Initialize Google Sheets Client
gsClient = pygsheets.authorize(
    service_file=os.getenv('MFP_SA_PATH'), scopes=SCOPES)

# /Users/tburke/Desktop/nutrition-coaching-credentials.json


def get_ordered_mfp_dict(mfpClient, day):
    mfpData = OrderedDict()
    # Add the day the data is associated with
    dayData = mfpClient.get_date(day)
    dayTotals = dayData.totals
    weight = mfpClient.get_measurements('Weight', day)
    meals = dayData.meals
    # Add values in order to the mfpData dict
    mfpData['Date'] = day
    mfpData['calories'] = dayTotals.get('calories')
    mfpData['protein'] = dayTotals.get('protein')
    mfpData['carbohydrates'] = dayTotals.get('carbohydrates')
    mfpData['fat'] = dayTotals.get('fat')
    mfpData['fiber'] = dayTotals.get('fiber')
    mfpData['sodium'] = dayTotals.get('sodium')
    mfpData['weight'] = weight.get(day)
    for meal in meals:
        mfpData[meal.name] = [entry.name for entry in meal.entries]
    return mfpData


# Get all ordered information for a particular day
mfpData = get_ordered_mfp_dict(mfpClient, yesterday)

spreadsheet = gsClient.open_by_key(
    "1dgwN6dEDscQTOGpIE0tuEt4uvSPb3aQciGuizrxm9iI")
worksheet = spreadsheet.worksheet(property='title', value=USER)

mfpDf = pd.DataFrame([mfpData], columns=mfpData.keys())
# Insert column into df
# dailyTotalsDf.insert(loc=0, column='Date', value=[yesterday])
print(mfpDf)
# Inserts a row underneath the column headers
worksheet.insert_rows(row=1, number=1, values=None)
# Inserts dailyTotalsDf in worksheet starting from A2
# worksheet.set_dataframe(mfpDf, 'A2')

# In case it is needed to load the service account key as a dict
# service_account_info = json.loads(secret_dict)
# my_credentials = service_account.Credentials.from_service_account_info(
#     service_account_info, scopes=SCOPES)
# gc = pygsheets.authorize(custom_credentials=my_credentials)
