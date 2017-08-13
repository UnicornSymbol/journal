#!/usr/bin/env python
#coding=utf-8

from __future__ import print_function
import httplib2
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import argparse
from functools import partial, wraps
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from com.properties import SheetProperties, GridProperties
from com.request_properties import DuplicateSheetRequest, DeleteSheetRequest

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'SpreadSheets'

class GoogleSheet(object):
    def __init__(self, scopes=None, application_name=None, flags=None):
        self.scopes = SCOPES if scopes is None else scopes
        self.application_name = APPLICATION_NAME if application_name is None else application_name
        self.spreadsheets = None
        self.flags = flags if flags else argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        self._init_spreadsheets()

    def get_credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, self.scopes)
            flow.user_agent = self.application_name
            credentials = tools.run_flow(flow, store, self.flags)
            print('Storing credentials to ' + credential_path)
        return credentials

    def _init_spreadsheets(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('sheets', 'v4', http=http)
        self.spreadsheets = service.spreadsheets()

    def get_spreadsheet_by_id(self, spreadsheet_id, **kwargs):
        spreadsheet = self.spreadsheets.get(spreadsheetId=spreadsheet_id, **kwargs)
        return SpreadSheet(self, spreadsheet, self.spreadsheets)

def parse_response_replies(name):
    def wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            response = func(self, *args, **kwargs)
            #print(response)
            properties = dict()
            for item in response['replies']:
                if name in item:
                    properties.update(item[name]['properties'])
            return Sheet(self, self.google_spreadsheets, spreadsheetId=response['spreadsheetId'], **properties)
        return inner
    return wrapper

class SpreadSheet(object):
    def __init__(self, parent, spreadsheet, google_spreadsheets):
        self.spreadsheet = spreadsheet
        self.parent = parent
        self.google_spreadsheets = google_spreadsheets

        self._parse_spreadsheet()
        self._partial_parent_with_spreadsheet_id()

    def _partial_parent_with_spreadsheet_id(self):
        self.batchUpdate = partial(self.google_spreadsheets.batchUpdate, spreadsheetId=self.spreadsheetId)

    def _parse_spreadsheet(self):
        self.data = self.spreadsheet.execute()
        self.title = self.data['properties']['title']
        self.spreadsheetId = self.data['spreadsheetId']

    def get_sheet_id_by_sheet_name(self, sheet_name):
        for sheet in self.data['sheets']:
            if sheet_name == sheet['properties']['title']:
                return sheet['properties']['sheetId']

    def get_sheet_index_by_sheet_name(self, sheet_name):
        for sheet in self.data['sheets']:
            if sheet_name == sheet['properties']['title']:
                return sheet['properties']['index']

    def get_one_sheet_by_name(self, sheet_name):
        """
        Get one sheet by name, the name must be string type and if the name not in this spreadsheet, it will case a
        Exception.
        """
        for sheet in self.data['sheets']:
            if sheet_name == sheet['properties']['title']:
                return Sheet(self, self.google_spreadsheets, spreadsheetId=self.spreadsheetId, **sheet['properties'])

    def get_one_sheet_by_id(self, sheet_id):
        for sheet in self.data['sheets']:
            if sheet_id == sheet['properties']['sheetId ']:
                return Sheet(self, self.google_spreadsheets, spreadsheetId=self.spreadsheetId, **sheet['properties'])

    @parse_response_replies('addSheet')
    def create_new_sheet(self, **kwargs):
        requests = list()
        requests.append({
            'addSheet': {
                'properties': SheetProperties(**kwargs).to_dict()
            }
        })

        return self.batch_update(requests=requests)

    def update_cells(self, sheetid, raw, color):
        """
            UpdateCellsRequests
        """
        values = []
        for _ in range(11):
            values.append({
              "userEnteredFormat": {
                "backgroundColor": color,
                "wrapStrategy": "WRAP",    # 换行策略
              },
            })
        requests = [
          {
            "updateCells": {
              "range": {
                "sheetId": sheetid,
                "startRowIndex": raw,  #从零开始
                "endRowIndex": raw+1,
                "startColumnIndex": 0,
                "endColumnIndex": 12,
              },
              "fields": "*",
              "rows": [    # 如果多行需要添加多个RowData，values的长度不能超过columnindex之间的范围
                {
                  "values": values
                },
              ],
      	   },
          }
        ]
        self.batch_update(requests=requests)

    def update_dimension_properties(self,sheetid,start,end,size):
        requests = [
          {
            "updateDimensionProperties": {
              "range": {
                "sheetId": sheetid,
                "dimension": "COLUMNS",
                "startIndex": start,
                "endIndex": end,
              },
              "properties": {
                "pixelSize": size,
              },
              "fields": "*",
            },
          }
        ]
        self.batch_update(requests=requests)

    def update_sheet_properties(self,sheetid,title,index):
        requests = [
          {
            "updateSheetProperties": {
              "properties": {
                "sheetId": sheetid,
                "title": title,
                "index": index,
                "gridProperties": {
                  "rowCount": 1000,
                  "columnCount": 26,
                },
              },
              "fields": "*",
            },
          }
        ]
        self.batch_update(requests=requests)

    def delete_one_sheet(self, sheetId):
        requests = list()
        requests.append({
            'deleteSheet': DeleteSheetRequest(sheetId=sheetId).to_dict()
        })
        return self.batch_update(requests)

    def get_all_sheets(self):
        """
        Get current all sheet info from current spreadsheet, each item type SingleSheet
        :return:
        """
        sheets = list()
        for sheet in self.data['sheets']:
            sheets.append(Sheet(self, self.google_spreadsheets, **sheet['properties']))

        return sheets

    def batch_update(self, requests):
        body = {
            'requests': requests
        }
        # response = self.batchUpdate(body=body).execute()
        # return response
        try:
            response = self.batchUpdate(body=body).execute()
        except Exception as e:
            raise e
        else:
            #self.change_flag = True
            self._parse_spreadsheet()
            return response


def execute(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).execute()
    return wrapper

class Sheet(object):
    def __init__(self, parent, google_spreadsheets, **kwargs):
        self.parent = parent
        self.google_spreadsheets = google_spreadsheets

        self._parse_params(**kwargs)

    def _parse_params(self, **kwargs):
        if 'gridProperties' in kwargs:
            self.__dict__['gridProperties'] = GridProperties(**kwargs.pop('gridProperties'))
        for key, value in kwargs.items():
            self.__dict__[key] = value

    def __getattr__(self, item):
        if hasattr(self.google_spreadsheets.values(), item):
            return partial(getattr(self.google_spreadsheets.values(), item),
                           spreadsheetId=self.spreadsheetId)

    def _get_range_name(self, source_range):

        if not source_range:
            return self.title
        elif self.title in source_range:
            return source_range
        else:
            return '{}!{}'.format(self.title, source_range)

    get_range_name = _get_range_name

    @execute
    def update_values(self, range_name, valueInputOption='RAW', **kwargs):
        return self.update(range=self._get_range_name(range_name), valueInputOption=valueInputOption, **kwargs)

    @execute
    def get_values(self, range_name, **kwargs):
        return self.get(range=self._get_range_name(range_name), **kwargs)

    def get_cell_position_by_value(self, check, range_name=''):
        res = self.get_cells(range_name=range_name)

        for i, raw in enumerate(res['values']):
            for j, col in enumerate(raw):
                if col == check:
                    return i, j

def main():
    google_sheet = GoogleSheet()
    #spreadsheetId = '1SODobpb-yCGGzC8Q4HruxhQiktpE49Et8QQcnjv1rDg'
    spreadsheetId = '1adBeW2sJDvKv6NLoqrkvHXKUK0l1QnbMIsQjTOlhXEQ'
    spreadsheet = google_sheet.get_spreadsheet_by_id(spreadsheetId)
    #spreadsheet.delete_one_sheet("57351355")

    def create_new_sheet():
        #sheet = spreadsheet.create_new_sheet(title='test')
        sheet = spreadsheet.get_one_sheet_by_name('2016年3月')
        body = {
            'values': [
                ['', ''],
                ['SPECMAN_BB_CRS_UPSWITCH_PLOT_TPC_ON_7', 'Command dpadcli returned false'],
                ['SPECMAN_BB_CRS_UPSWITCH_PLOT_TPC_ON_7', 'Command dpadcli returned false'],
                ['SPECMAN_BB_CRS_UPSWITCH_PLOT_TPC_ON_7', 'Command dpadcli returned false'],
                ['SPECMAN_BB_CRS_UPSWITCH_PLOT_TPC_ON_7', 'Command dpadcli returned false'],
                ['SPECMAN_BB_CRS_UPSWITCH_PLOT_TPC_ON_7', 'Command dpadcli returned false'],
                ['SPECMAN_BB_CRS_UPSWITCH_PLOT_TPC_ON_7', 'Command dpadcli returned false'],
                ['', ''],
                ['a', ''],
            ]
        }

        #sheet.update_values('A1:B', body=body)
        print(sheet.get_values('A9:k9'))
    #create_new_sheet()
    sheetid = spreadsheet.get_sheet_id_by_sheet_name('2017年8月')
    spreadsheet.update_cells(sheetid,18,{"green":1})
    #spreadsheet.update_dimension_properties(sheetid,4,5,305)
    #spreadsheet.update_sheet_properties(sheetid,"test1")
    #range_name = 'A1:K'

if __name__ == '__main__':
    main()

