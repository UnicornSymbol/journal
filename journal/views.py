from django.shortcuts import render,render_to_response,redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from journal.forms import ChangepwdForm

# Create your views here.
def login(request):
    if request.user.is_authenticated():
        return redirect(reverse("journal_list"))
    if request.method == 'POST':
        #print(request.POST)
        username=request.POST.get("username",'')
        password=request.POST.get("password",'')
        user=auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect(reverse("journal_list"))
        else:
            return render(request, "login.html", {'error':'用户名或密码错误'})
    return render(request, "login.html", {})
        
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

@login_required
def changepwd(request):
    if request.method == 'GET':
        form = ChangepwdForm()
        return render(request, 'changepwd.html', {'form': form,})
    else:
        form = ChangepwdForm(request.POST)
        #print(request.POST)
        if form.is_valid():
            username = request.user.username
            oldpassword = request.POST.get('oldpassword', '')
            user = auth.authenticate(username=username, password=oldpassword)
            if user is not None and user.is_active:
                newpassword = request.POST.get('newpassword1', '')
                user.set_password(newpassword)
                user.save()
                auth.login(request,user)
                return redirect(reverse("journal_list"))
            else:
                return render(request, 'changepwd.html', {'form': form,'error':'原密码错误'})
        else:
            #print(form.errors)
            return render(request, 'changepwd.html', {'form': form,'error':form.errors.get('__all__').data[0].message})
