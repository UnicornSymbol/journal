from django import forms
from query.models import Sheet,Journal

class JournalForm(forms.ModelForm):
    class Meta:
        model = Journal
        fields = ('sheet', 'date', 'time', 'department', 'people', 'problem', 'handler', 'result', 'status', 'end_time')
        labels = {
            'sheet': '所属表格',
            'date': '日期',
            'time': '报障时间',
            'department': '报障部门',
            'people': '报障人',
            'problem': '报障内容',
            'handler': '处理人',
            'result': '处理结果',
            'status': '处理状态',
            'end_time': '结束时间',

        }
        widgets = {
            'sheet': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'readonly': True}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'readonly': True}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'people': forms.TextInput(attrs={'class': 'form-control'}),
            'problem': forms.Textarea(attrs={'class': 'form-control'}),
            'handler': forms.TextInput(attrs={'class': 'form-control'}),
            'result': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'readonly': True}),
            #'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date', 'value': '1997-01-01'}),
            #'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date', 'value': '1997-01-01'}),
        }
