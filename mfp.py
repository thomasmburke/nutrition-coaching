from collections import OrderedDict
import logging
import myfitnesspal
import os


def initialize_mfp_client() -> "<class 'myfitnesspal.client.Client'>":
    """
    Summary: Create client for communication with myfitnesspal
    """
    return myfitnesspal.Client(
        os.getenv('MFP_USERNAME'), password=os.getenv('MFP_PASSWORD'))


def get_ordered_mfp_dict(mfpClient: "<class 'myfitnesspal.client.Client'>", day: "datetime.date") -> "OrderedDict":
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
