import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from query.models import Sheet, Journal
from googleapi.googleapi import GoogleSheet
from query.forms import JournalForm

RED = {"red": 1}
GREEN = {"green": 1}
BLUE = {"blue": 1}
WHITE = {"red": 1, "green": 1, "blue": 1}

# Create your views here.
def get_spreadsheet():
    google_sheet = GoogleSheet()
    #spreadsheetId = '1SODobpb-yCGGzC8Q4HruxhQiktpE49Et8QQcnjv1rDg'
    spreadsheetId = '1adBeW2sJDvKv6NLoqrkvHXKUK0l1QnbMIsQjTOlhXEQ'
    spreadsheet = google_sheet.get_spreadsheet_by_id(spreadsheetId)
    return spreadsheet

@login_required
def journal_list(request):
    title = request.GET.get('title', '')
    keyword = request.GET.get('keyword', '')
    #current = datetime.datetime.now().date().strftime('%m/%d/%Y')
    date = request.GET.get('date', '')
    if date:
        date = datetime.datetime.strptime(date,'%m/%d/%Y')
    if keyword and date:
        journals = Journal.objects.filter(problem__icontains=keyword).filter(date=date).order_by('-id')
    elif keyword:
        journals = Journal.objects.filter(problem__icontains=keyword).order_by('-id')
    elif date:
        journals = Journal.objects.filter(date=date).order_by('-id')
    else:
        journals = Journal.objects.order_by('-id')
    if title:
        sheet = Sheet.objects.get(title=title)
        journals = Journal.objects.filter(sheet=sheet)
    paginator = Paginator(journals, 20)
    page = request.GET.get('page')
    try:
        journals = paginator.page(page)
    except PageNotAnInteger:
        journals = paginator.page(1)
    except EmptyPage:
        journals = paginator.page(paginator.num_pages)
    return render(request, 'journal_list.html', locals())

def update_sheet(spreadsheet, journal):
    body = {
        'values': [
            [
                None if not journal.date else journal.date.strftime("%Y-%m-%d"),
                None if not journal.time else journal.time.strftime("%H:%M"),
                journal.department,
                journal.people,
                journal.problem,
                journal.handler,
                journal.result,
                journal.get_status_display(),
                None if not journal.end_time else journal.end_time.strftime("%H:%M"),
            ],
        ]
    }
    sheet = spreadsheet.get_one_sheet_by_name(journal.sheet.title)
    sheet.update_values('A{0}:I{0}'.format(journal.position), body=body)

@login_required
def journal_manage(request, id=None):
    spreadsheet = get_spreadsheet()
    if id:
        journal = get_object_or_404(Journal, pk=id)
        action = 'edit'
        page_name = '编辑日志'
    else:
        journal = Journal()
        date = datetime.datetime.now()
        year = date.year
        month = date.month
        title = '{}年{}月'.format(year,month)
        # 设置下拉框默认值为最新表格
        try:
            journal.sheet = Sheet.objects.get(title=title)
        except ObjectDoesNotExist:
            journal.sheet = Sheet.objects.last()
        action = 'add'
        page_name = '添加日志'
    if request.method == 'POST':
        form = JournalForm(request.POST, instance=journal)
        #print(request.POST)
        if form.is_valid():
            #print(form.cleaned_data)
            j = form.save(commit=False)
            if action == "add":
                sheet = request.POST.get('sheet')
                count = Journal.objects.filter(sheet=sheet).count()
                j.position = str(count+2)
                sheetid = spreadsheet.get_sheet_id_by_sheet_name(j.sheet.title)
                raw = count+1  #从零开始
                spreadsheet.update_cells(sheetid, raw, WHITE)
            j.save()
            update_sheet(spreadsheet, j)
            return redirect(reverse('journal_list'))
        else:
            return render(request, 'journal_manage.html', locals())
    form = JournalForm(instance=journal)
    return render(request, 'journal_manage.html', locals())

def approve_commit(journal, sign, comment):
    body = {
        'values': [
            [   
                sign,
                comment,
            ],
        ]
    }
    spreadsheet = get_spreadsheet()
    sheet = spreadsheet.get_one_sheet_by_name(journal.sheet.title)
    sheet.update_values('J{0}:K{0}'.format(journal.position), body=body)

@login_required
def approve(request):
    #print(request.POST)
    id = request.POST.get('id','')
    sign = request.POST.get('sign','')
    comment = request.POST.get('comment','')
    journal = get_object_or_404(Journal, pk=id)
    journal.sign = sign
    journal.comment = comment
    journal.save()
    approve_commit(journal, sign, comment)
    return JsonResponse({})

@login_required
def sheet_list(request):
    sheets = Sheet.objects.order_by('-id')
    paginator = Paginator(sheets, 20)
    page = request.GET.get('page')
    try:                  
        sheets = paginator.page(page)
    except PageNotAnInteger:
        sheets = paginator.page(1)
    except EmptyPage:    
        sheets = paginator.page(paginator.num_pages)
    return render(request, 'sheet_list.html', locals())

def create_sheet(spreadsheet, title):
    body = {
        'values': [
            [
                '日期',
                '报障时间',
                '报障部门',
                '报障人',
                '报障内容',
                '处理人',
                '处理结果',
                '处理状态',
                '处理结束时间',
                '主管确认签名',
                '主管备注',
            ],
        ]
    }
    spreadsheet.create_new_sheet(title=title, index=0)
    sheetid = spreadsheet.get_sheet_id_by_sheet_name(title)
    spreadsheet.update_cells(sheetid, 0, GREEN)
    spreadsheet.update_dimension_properties(sheetid,4,5,300)
    spreadsheet.update_dimension_properties(sheetid,6,7,300)
    spreadsheet.update_dimension_properties(sheetid,10,11,200)
    sheet = spreadsheet.get_one_sheet_by_name(title)
    sheet.update_values('A1:K1', body=body)
    

@login_required
def sheet_manage(request):
    spreadsheet = get_spreadsheet()
    if request.method =='GET':
        delete = request.GET.get('delete', None)
        title = request.GET.get('title')
        if delete:
            # 删除数据库记录
            sheet = get_object_or_404(Sheet, title=title)
            sheet.delete()
            # 删除google表格
            sheetid = spreadsheet.get_sheet_id_by_sheet_name(title)
            spreadsheet.delete_one_sheet(sheetid)
            return JsonResponse({"message": "删除成功"})
    if request.method == 'POST':
        id = request.POST.get("id", None)
        title = request.POST.get("title")
        #print(title)
        #print("hello id: {}".format(id))
        if not title:
            return JsonResponse({"status":"失败","error": "标题不能为空"})
        if id:
            sheet = get_object_or_404(Sheet, pk=id)
            old_title = sheet.title
            #print(old_title)
            try:
                Sheet.objects.get(title=title)
            except ObjectDoesNotExist:
                sheet.title = title
                sheet.save()
                sheetid = spreadsheet.get_sheet_id_by_sheet_name(old_title)
                index = spreadsheet.get_sheet_index_by_sheet_name(old_title)
                spreadsheet.update_sheet_properties(sheetid,title,index)
                return JsonResponse({"status":"成功","message": "更新成功"})
            else:
                return JsonResponse({"status":"失败","error": "表格‘{}’已经存在".format(title)})
        try:
            Sheet.objects.get(title=title)
        except ObjectDoesNotExist:
            Sheet.objects.create(title=title)
            create_sheet(spreadsheet, title)
            return JsonResponse({"status":"成功","message": "添加成功"})
            #return redirect(reverse('sheet_list'))
        else:
            return JsonResponse({"status":"失败","error": "表格‘{}’已经存在".format(title)})
