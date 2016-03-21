# coding:utf8
'''
Created on 2015-12-02

@author: xuemengwang
'''

import json
import threading
import time
import logging
import datetime
import public
import data_mgr
from onlinecard_mgr import  models

def getProduct_cards(data):
    """
    liujichao
    获取未发布上线单内容
    """

    now = public.str2datetime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), "%Y-%m-%d %H:%M:%S")
    retData={}
    try:
        jsdata=json.loads(data)
        endDate=jsdata['endDate'] #结束时间
        listData=jsdata['listData']

        for tmp in listData:
            info=tmp['info']
            groups = data_mgr.models.Group.objects.filter(ckpak=info['ckPak'])
            m=models.ProductCard.objects.filter(op_card_id=tmp['id'])
            if 0==len(groups):
                print "groups 表中不存在的分组",info['ckPak']
            if 0 != len(groups):
                if 0 == len(m):
                    s=models.ProductCard()
                    taskName=tmp['task_name'] #是否过测试
                    if u"不过测试" in taskName:
                        s.need_qa=0
                    else:
                        s.qa_owner=info['testMan']
                        s.test_result=info['addData_ret']
                        s.need_qa=1
                    s.endDate=endDate
                    s.op_card_id=tmp['id']
                    s.rd_owner=info['devMan'] #研发负责人
                    if not info.has_key("publish_mode"):
                        count=""
                        module =info['modName']
                        for temp in module:
                            if temp !="":
                                count=count+temp+","
                        s.module_name=count
                    else:
                        s.module_name=info['publish_mode']  #模块名称
                    s.card_type=info['publish_type'] #提测单类型
                    s.pm_owner=info['goodsMan']#产品负责人
                    if not info.has_key('addData_req'):
                        s.content=info['projectName']
                    else:
                        s.content=info['addData_req'] #提测单的内容
                    s.online_suggestion=info['addData_mymemo'] #上线意见
                    s.group_id = groups[0].id
                    s.save()
        retData['code']="0"
        retData['message']="success"
        return retData
    except Exception as err:
        retData['code']="-1"
        retData['message']="fail"
        return retData


def save_push_status(data):
    """
    liujichao
    存储上线状态 数据
    """
    try:
        retData={}
        jsonReq = json.loads(data);
        if len(jsonReq) ==0:
            retData['code']="1"
            retData['message']="暂无数据"
            return retData
        now = public.str2datetime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
        for tmp in jsonReq:
            if "BJ" in tmp:
                area="BJ"
            elif "DFZ" in tmp:
                area="DFZ"
            else:
                area="GZ"
            s=models.Pushstatus.objects.filter(nowTime__gt=now,area=area,version=jsonReq[tmp]['version'])
            if len(s):
                if s[0].endFlag != jsonReq[tmp]['endflag']:
                    s[0].endFlag=jsonReq[tmp]['endflag']
                    s.update(endFlag=jsonReq[tmp]['endflag'])
            else:
                m = models.Pushstatus()
                m.nowTime = now
                m.endFlag = jsonReq[tmp]['endflag']
                m.update_Time=jsonReq[tmp]['updated_at']
                m.area=area
                m.version=jsonReq[tmp]['version']
                m.save()
        retData['code']="0"
        retData['message']="success"
        return retData
    except Exception as err:
        print err
        retData['code']="-1"
        retData['message']="fail"
        return retData

def get_push_status(data):
    """
    liujichao
    根据时间、小模块、地区上线状态，
    返回数据endFlag、code、message
    """
    location=data['area']
    model=data['module']
    date=data['time']
    # date2=int(date)+100000
    # timeArray=datetime.datetime.fromtimestamp(float(date))
    # timeArray2=datetime.datetime.fromtimestamp(float(date2))
    # start=timeArray.strftime('%Y-%m-%d 00:00:01')
    # endTime=timeArray2.strftime('%Y-%m-%d 00:00:01')
    m = models.Pushstatus.objects.filter(version=model,area=location)
    print "version",model
    print "area",location
    print len(m)
    returnData={}
    if len(m):
        boolean=0;
        for tmp in m:
            if model in tmp.version:
                returnData["code"]="0"
                returnData["message"]=u"成功"
                returnData["status"]=tmp.endFlag
                boolean=1
        if boolean == 0:
            returnData["code"]="-1"
            returnData["message"]=u"数据不存在"
            returnData["status"]="0"
    else:
        returnData["code"]="-1"
        returnData["message"]=u"数据不存在"
        returnData["status"]="0"

    return returnData

def get_group_name(data):
    groupName=data_mgr.models.Group.objects.all()
    return groupName



def testsave(data):
    rt={}
    now = public.str2datetime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    m = models.Pushstatus()
    m.nowTime = now
    rt['nowtime']=m.nowTime
    m.endFlag = "0"
    rt['nowtime']=m.endFlag
    m.update_Time=now
    rt['update_Time']=m.update_Time
    m.area="GZ"
    rt['area']=m.area
    m.version="RB_groupon_20160121_153921"
    rt['version']=m.version
    m.save()
    return rt
