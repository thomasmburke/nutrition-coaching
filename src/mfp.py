from collections import OrderedDict
import logging
import myfitnesspal
import os
from datetime import timedelta
from time import sleep
import random

# Set logger
logger = logging.getLogger(__name__)


def initialize_mfp_client(user: "str") -> "<class 'myfitnesspal.client.Client'>":
    """
    Summary: Create client for communication with myfitnesspal
    """
    logger.info(f'Initializing MFP Client for {user}...')
    return myfitnesspal.Client(
        os.getenv(f"{user}_USERNAME"), password=os.getenv(f"{user}_PASSWORD"))


def get_ordered_mfp_dict(mfpClient: "<class 'myfitnesspal.client.Client'>", day: "datetime.date") -> "OrderedDict":
    """
    Summary: Gather MFP data for a particular day
    """
    mfpData = OrderedDict()
    # Add the day the data is associated with
    # Surround requests with exponential backoff in case of issues with mfp data request
    for n in range(0, 10):
        try:
            dayData = mfpClient.get_date(day)
            weight = mfpClient.get_measurements('Weight', day)
            break
        except Exception as e:
            if(n == 9):
                logger.error(
                    'exponential timeout did not resolve the issue')
                # Send SNS message
                raise ValueError(
                    f'{mfpClient.effective_username} had an MFP data pull issue for {day} yielding the following error={str(e)}')
            else:
                sleep((2 ** n) + random.random())  # exponential backoff
                logger.info(f'exponential backoff retry {n}')

    dayTotals = dayData.totals
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
    logger.info(f"MFP data for {day}: \n{mfpData}")
    return mfpData


def get_multiple_mfp_dicts(mfpClient: "<class 'myfitnesspal.client.Client'>", day: "datetime.date", numDays: "int" = 1) -> "[OrderedDict]":
    """
    Summary: Get multiple days of MFP data starting at a particular day and pulling for numDays in the past
    """
    mfpDataList = []
    for x in range(numDays):
        # First time in loop we are subtracting 0 days from day
        currDay = day - timedelta(x)
        mfpDataList.append(get_ordered_mfp_dict(
            mfpClient=mfpClient, day=currDay))
    return mfpDataList
