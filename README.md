* 此plugin用于业务的存活检测，比如端口检测portCheck，业务接口检测httpCheck，进程pid重启报警pidCheck
* plugin可以复用，但配置需要按需修改其值
* port有多个端口的，可以用","逗号隔开
* 有多个业务的，配置文件中的section直接使用a ~ z即可，metric可以拿来区分业务
* httpCheck里面，无论是GET还是POST，data这个key对应的value是需要传递的数据，无数据的话，直接写"data="，也就是值为空即可
* uri需要写完整
* 下面的配置仅仅是示范
* 关于返回值：返回值value=1表示正常，value=0表示服务不正常，value=2表示进程重启过
* 按照此规范填写配置即可，保存到配置文件conf.ini
* 其实falcon自带的proc.num和net.port.listen
```
[a]
action = portCheck
host = 127.0.0.1
port = 53,80
metric = dnsPortCheck
[b]
action = httpCheck
host = 127.0.0.1
port = 80
method = GET
metric = dnsHttpCheck
uri = /httpdns
data = dn=www.baidu.com&ttl=1&cip=222.76.241.146
[c]
action = httpCheck
host = www.baidu.com
port = 80
method = POST
metric = noticeHttpCheck
uri = /send_mail
data = receiver=10086@qq.com&subject=test&content=hahaha
[d]
action = portCheck
host = 192.168.1.1
port = 8899
metric = dnsPortCheck
[e]
action = pidCheck
process = nginx
metric = nginxPidCheck
[f]
action = pidCheck
process = php-fpm
metric = phpPidCheck
```
