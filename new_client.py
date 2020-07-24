import sys
import os
sys.path.insert(0, 'src')
from googlesheets import initialize_gsheet_client
import argparse
import pygsheets
import re


def add_new_client(user: "str", email: "str") -> "pygsheets.Spreadsheet":
    gsClient = initialize_gsheet_client()
    # Create a new spreadsheet for the new user
    # Folder in Margaux's Drive
    gsClient.create(title=user, folder="1ayQ9ERDdEdIgiG8AWHrJ7lbtiJtCLRdk")
    # Get a reference to the newly created spreadsheet
    spreadsheet = gsClient.open(title=user)
    # Add expected worksheets
    spreadsheet.sheet1.title = f"{user}_WEEKLY"
    spreadsheet.add_worksheet(title=f"{user}_NUTRITION_HISTORY")
    # TODO: Add column headers to the nutrition history view

    # Share the spreadsheet with the new user's email
    spreadsheet.share(email_or_domain=email, role='reader', type='user',
                      emailMessage="Welcome to Margaux Carle's nutrition coaching program!\n\nWe will use this Google Sheet to track your nutrition info you provide in MyFitnessPal.")
    return spreadsheet


# def validate_email():
#     return


class EmailType(object):
    """
    Supports checking email agains different patterns. The current available patterns is:
    RFC5322 (http://www.ietf.org/rfc/rfc5322.txt)
    """

    patterns = {
        'RFC5322': re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"),
    }

    def __init__(self, pattern):
        if pattern not in self.patterns:
            raise KeyError('{} is not a supported email pattern, choose from:'
                           ' {}'.format(pattern, ','.join(self.patterns)))
        self._rules = pattern
        self._pattern = self.patterns[pattern]

    def __call__(self, value):
        if not self._pattern.match(value):
            raise argparse.ArgumentTypeError(
                "'{}' is not a valid email - does not match {} rules".format(value, self._rules))
        return value


def main():
    # Gather args and validate them
    parser = argparse.ArgumentParser()
    parser.add_argument('--user')
    parser.add_argument('--email', type=EmailType('RFC5322'))
    args = parser.parse_args()
    USER = args.user.upper()
    EMAIL = args.email

    # Set env vars
    # This should call function from another file that will be in the .gitignore

    # redeploy function

    # create new scheduler job

    # Create, format and share spreadsheet
    # add_new_client(user=USER, email=EMAIL)


if __name__ == '__main__':
    # usage: python3 new_client.py --user tburke --email info@example.com
    main()
