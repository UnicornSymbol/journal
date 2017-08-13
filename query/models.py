from django.db import models

status = (
    (1, "处理中"),
    (2, "处理完成"),
)

# Create your models here.
class Sheet(models.Model):
    title = models.CharField(max_length=128, unique=True, verbose_name='标题')

    class Meta:
        db_table = 'sheet'
        default_permissions  = ()
        permissions = (
            ('view_sheet', '查看表格'),
            ('edit_sheet', '管理表格'),
        )
    def __str__(self):
        return self.title

class Journal(models.Model):
    sheet = models.ForeignKey(Sheet, verbose_name='所属表格', default=1)
    position = models.CharField(max_length=64, verbose_name='位置', default='')
    #date = models.DateField(null=True, blank=True, auto_now_add=True, editable=True, verbose_name='日期')
    date = models.DateField(null=True, blank=True, verbose_name='日期')
    time = models.TimeField(null=True, blank=True, verbose_name='报障时间')
    department = models.CharField(null=True, blank=True, max_length=64, verbose_name='报障部门')
    people = models.CharField(null=True, blank=True, max_length=64, verbose_name='报障人')
    problem = models.TextField(null=True, blank=True, verbose_name='报障内容')
    handler = models.CharField(null=True, blank=True, max_length=64, verbose_name='处理人')
    result = models.TextField(null=True, blank=True, verbose_name='处理结果')
    status = models.IntegerField(choices=status, blank=True, null=True,verbose_name='处理状态', default=1)
    end_time = models.TimeField(null=True, blank=True, verbose_name='处理结束时间')
    sign = models.CharField(null=True, blank=True, max_length=64, verbose_name='主管签名')
    comment = models.TextField(null=True, blank=True, verbose_name='主管备注')
    
    class Meta:
        db_table = 'journal'
        default_permissions  = ()
        permissions = (
            ('approve', '审批'),
        )
    def __str__(self):
        return self.problem
