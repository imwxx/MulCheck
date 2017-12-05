#!/usr/bin/env python

# -*- coding:utf-8 -*-

__author__="imwuxuxing@gmail.com"

import sys, os
import socket
import time
import json
import commands
import ConfigParser
import httplib

filename = sys.argv[0]
dirname = os.path.dirname(filename)
workSpace = os.path.abspath(dirname)
configFile = workSpace + "/conf.ini"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
endpoint = socket.gethostname()
ip = socket.gethostbyname(endpoint)
jsonFile = workSpace + "/JSON"

TMPMSGDIC = {}
DEADDIC = {}

def PidCheck(command, metricName):
    (status, output) = commands.getstatusoutput(command)
    value = 1
    tags = '%s%s%s' % ("status=running,", "ip=", ip)
    if status != 0:
        value = 0
        tags = '%s%s%s' % ("status=dead,", "ip=", ip)
    timestamp = int(time.time())
    metric = metricName
    counterType = "GAUGE"
    step = 60
    msg = {'endpoint': endpoint, 'tags': tags, 'timestamp': timestamp, 'metric': metric, 'value': value, 'counterType': counterType, 'step': step}
    if status !=0:
        DEADDIC[metricName] = msg

    TMPMSGDIC[metricName] = output
    return msg

def JudgeSockPort(host, port):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.settimeout(2)
    tags = "status=failed"
    value = 0
    try:
        soc.connect((host, port))
        tags = "status=successed,port=" + str(port)
        value = 1
    except Exception:
        tags = "status=failed,port=" + str(port)
    finally:
        if soc:
            soc.close()
    return {"tags": tags, "value": value}

def JudgeHttpService(host, port, method, uri, data=None):
    httpClient = None
    value = 0
    status = 'failed'
    tags = ''
    if method == "GET":
        try:
            httpClient = httplib.HTTPConnection(host, port, timeout=30)
            Uri = None
            if data != None:
                Uri = uri + "?" + data
            httpClient.request('GET', Uri)
            response = httpClient.getresponse()
            statusCode = response.status
            if statusCode == 200:
                value = 1
                status = 'successed'
        except Exception, e:
            value = 2
            status = str(e)
        finally:
            if httpClient:
                httpClient.close()
        tags = 'method=' + method + ',status=' + status + ',port=' + str(port)
    elif method == "POST":
        try:
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            httpClient = httplib.HTTPConnection(host, port, timeout=30)
            httpClient.request("POST", uri, data, headers)
            response = httpClient.getresponse()
            statusCode = response.status
            if statusCode == 200:
                value = 1
                status = 'successed'
        except Exception, e:
            values = 2
            status = e
        finally:
            if httpClient:
                httpClient.close()
        tags = 'method=' + method + ',status=' + status + ',port=' + str(port)
    return {'value': value, 'tags': tags}

def MakeMoney():
    if not os.path.isfile(configFile):
        sys.exit(1)
    config = ConfigParser.ConfigParser()
    config.readfp(open(configFile, "rb"))
    MSG = []
    for section in config.sections():
        action = config.get(section, "action")
        timestamp = int(time.time())
        counterType = "GAUGE"
        step = 60
        if action == "portCheck":
            host = config.get(section, "host")
            port = config.get(section, "port")
            metric = config.get(section, "metric")
            for port in port.split(','):
                res = JudgeSockPort(host, int(port))
                tags = res['tags']
                value = res['value']
                msg = {
                    'endpoint': endpoint, 
                    'tags': tags, 
                    'timestamp': timestamp, 
                    'metric': metric, 
                    'value': value, 
                    'counterType': counterType, 
                    'step': step
                    }
                MSG.append(msg)
        elif action == "httpCheck":
            host = config.get(section, "host")
            port = config.get(section, "port")
            metric = config.get(section, "metric")
            Data = None
            method = config.get(section, "method")
            uri = config.get(section, "uri")
            data = config.get(section, "data")
            Data = data
            for port in port.split(','):
                res = JudgeHttpService(host, port, method, uri, Data)
                msg = {
                    'endpoint': endpoint,
                    'tags': res['tags'],
                    'timestamp': timestamp,
                    'metric': metric,
                    'value': res['value'],
                    'counterType': counterType,
                    'step': step
                    }
                MSG.append(msg)
        elif action == "pidCheck":
            process = config.get(section, "process")
            metric = config.get(section, "metric")
            command = 'pidof ' + process
            pidofRes = PidCheck(command, metric)
            if os.path.exists(jsonFile):
                fileObject = open(jsonFile, 'r')
                try:
                    content = fileObject.read()
                    if content != "" and not DEADDIC:
                        text = json.loads(content)
                        newRes = TMPMSGDIC[metric]
                        oldRes = text[metric]
                        for new in newRes.split(" "):
                            if new not in oldRes.split(" "):
                                pidofRes["value"] = 2
                                pidofRes['tags'] = '%s%s%s' % ("status=restarted,", "ip=", ip)
                finally:
                    fileObject.close()
            if DEADDIC:
                for k, v in DEADDIC.items():
                    if k == metric:
                        MSG.append(v)
                    else:
                        MSG.append(pidofRes)
            else:
                MSG.append(pidofRes)

    fileObject = open(jsonFile, 'w')
    try:
        fileObject.write(json.dumps(TMPMSGDIC))
    finally:
        fileObject.close()

    print(json.dumps(MSG))

if __name__ == '__main__':
    MakeMoney()
