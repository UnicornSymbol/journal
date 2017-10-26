# journal
通过api管理Google sheet，由于在Google表格中一个月一个日志表格，导致日志查询困难，此项目将所有日志集中起来统一管理，方便查询，以便遇到问题快速处理。
###### 值班日志格式
![值班日志](/images/值班日志.png)
###### 日志管理
![日志管理](/images/journal.png)
###### 表格管理
![表格管理](/images/sheets.png)
###### 日志添加
![日志添加](/images/日志添加.png)
# 部署
###### mysql授权
```Bash
create database journal default charset utf8;
grant all privileges on journal.* to szop@"localhost" identified by 'szop';
grant all privileges on journal.* to szop@"localhost" identified by 'szop';
```
###### 安装依赖
```Bash
pip install -r requirements.txt
```
###### 初始化
```Bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
###### nginx配置
```Bash
server
{
    listen 80;
    #server_name 192.168.229.128;
    server_name 172.30.9.39;

    location / {
        root /root/worksapce/journal;

        ## uwsgi配置的端口
        uwsgi_pass 127.0.0.1:9000;
        include uwsgi_params;
        uwsgi_param UWSGI_CHDIR  /root/workspace/journal;
        uwsgi_param UWSGI_SCRIPT wsgi;
    }
    location ~ .*\.(log|php|pl|py|sh|cgi)$ {
        return 403;
    }
    location /static/ {
        # root /root/workspace/journal/;
        alias /root/workspace/journal/collectstatic/;
        access_log off;
    }
    #location ~ .*\.(gif|jpg|png|htm|html|css|js|flv|ico|swf)(.*) {
        # root /root/workspace/journal/;
        # alias /root/workspace/journal/collectstatic/;
        # expires 30d;
    #}
    #location ~ .*\.(js|css)?(.*) {
        # root /root/workspace/journal/;
        # alias /root/workspace/journal/collectstatic/;
        # expires      12h;
    #}
}
```
###### uwsgi安装配置
```Bash
pip install uwsgi
cat /etc/uwsgi.ini
[uwsgi]
socket = 0.0.0.0:9000
master = true
pidfile = /var/run/uwsgi.pid
processes = 8
chdir = /root/workspace/journal
home = /root/.pyenv/versions/spider
module = journal.wsgi
profiler = true
memory-report=true
enable-threads=true
logdate=true
vacuum = true
limit-as=6048
chmod-socket = 664
daemonize=/var/log/django.log
```
###### 启动nginx
```Bash
/etc/init.d/nginx start
```
###### 启动uwsgi
```Bash
uwsgi --ini /etc/uwsgi.ini
```
