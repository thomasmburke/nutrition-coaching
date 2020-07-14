import pygsheets
import logging
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']


def initialize_gsheet_client() -> "<class 'pygsheets.client.Client'>":
    '''
    Summary: Initialize Google Sheets Client
    '''
    return pygsheets.authorize(service_file=os.getenv('MFP_SA_PATH'), scopes=SCOPES)
