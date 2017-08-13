#coding=utf-8

import os,sys
import django
import datetime
#sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "googleapi"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "journal.settings")
django.setup()
from googleapi.googleapi import GoogleSheet
from query.models import Sheet,Journal

RED = {"red": 1}
GREEN = {"green": 1}
BLUE = {"blue": 1}
WHITE = {"red": 1, "green": 1, "blue": 1}
INDEX = {0:"date", 1:"time", 2:"department", 3:"people", 4:"problem", 5:"handler", 6:"result", 7:"status", 8:"end_time", 9:"sign", 10:"comment"}
mapping = {
    'date': lambda x: None if not x else datetime.datetime.strptime(x, '%Y-%m-%d'),
    'time': lambda x: None if not x else datetime.datetime.strptime(x, '%H:%M'),
	 'status': lambda x: None if not x else 1 if x=="处理中" else 2,
    'end_time': lambda x: None if not x else datetime.datetime.strptime(x, '%H:%M'),
}


def init_sheet(spreadsheet):
    #print(spreadsheet.data)
    titles = []
    for sheet in reversed(spreadsheet.data["sheets"]):
        title=sheet["properties"]["title"]
        titles.append(title)
        #print(title)
        Sheet.objects.create(title=title)
    return titles

def parse(value):
    params = {}
    for i in range(11):
        k = INDEX[i]
        try:
            params[k] = mapping.get(k, lambda x: x)(value[i])
        except IndexError:
            params[k] = None
        except ValueError:
            print(value)
    return params

def init_journal(spreadsheet, titles):
    for title in titles:
        count = 1
        sheet = spreadsheet.get_one_sheet_by_name(title)
        result = sheet.get_values('A1:K')
        values = result.get("values", [])
        #print(values[1:])
        for value in values[1:]:
            count += 1
            params = parse(value)
            params["sheet"] = Sheet.objects.get(title=title)
            #params["position"] = "A{0}:K{0}".format(count)
            params["position"] = str(count)
            #print(params)
            Journal.objects.create(**params)
        #break

def main():
    google_sheet = GoogleSheet()
    spreadsheetId = '1SODobpb-yCGGzC8Q4HruxhQiktpE49Et8QQcnjv1rDg'
    #spreadsheetId = '1adBeW2sJDvKv6NLoqrkvHXKUK0l1QnbMIsQjTOlhXEQ'
    spreadsheet = google_sheet.get_spreadsheet_by_id(spreadsheetId)
    #for i in Sheet.objects.order_by("-id"):
    #    spreadsheet.create_new_sheet(title=i.title)
    titles = init_sheet(spreadsheet)
    init_journal(spreadsheet,titles)

if __name__ == '__main__':
    main()
