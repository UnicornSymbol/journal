from django import forms

class ChangepwdForm(forms.Form):
    oldpassword = forms.CharField(
        required=True,
        label="原密码",
        error_messages={'required': '请输入原密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':"原密码",
                'class': 'form-control',
                'style': 'width:250px'
            }
        ),
    ) 
    newpassword1 = forms.CharField(
        required=True,
        min_length=8,
        label="新密码",
        error_messages={'required': '请输入新密码', 'min_length': '新密码至少需要8个字符'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':"新密码",
                'class': 'form-control',
                'style': 'width:250px'
            }
        ),
    )
    newpassword2 = forms.CharField(
        required=True,
        #min_length=8,
        label="确认密码",
        error_messages={'required': '请再次输入新密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder':"确认密码",
                'class': 'form-control',
                'style': 'width:250px'
            }
        ),
    )
    def clean(self):
        if not self.is_valid():
            if len(self.cleaned_data.keys()) == 2:
                raise forms.ValidationError("新密码长度不符")
            else:
                raise forms.ValidationError("所有项都为必填项")
        elif self.cleaned_data['newpassword1'] != self.cleaned_data['newpassword2']:
            raise forms.ValidationError("两次输入的新密码不一样")
        else:
            cleaned_data = super(ChangepwdForm, self).clean()
        return cleaned_data
