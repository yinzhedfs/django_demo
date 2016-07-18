#coding:utf-8
import sys
from django.http import HttpResponse
from django.core.paginator import Paginator
from models import Message,UserMessage
import simplejson

# Create your views here.

def send_msg(request):
    response = {}
    info = ""
    try:
        if request.method == 'POST':
            req = request.POST
            recv_user = req.get('recv_user')
            send_user = req.get('send_user')
            title = req.get('title')
            content = req.get('content')
            msg = Message(title=title, content=content)
            # 发送者ID为1则是系统信息
            if send_user == 1:
                msg.category = 1
            msg.save()
            user_msg = UserMessage(recv_user=recv_user,send_user=send_user,message=msg)
            user_msg.save()
            response['status'] = user_msg.status

    except:
        info = "%s || %s" % (sys.exc_info()[0], sys.exc_info()[1])
        return HttpResponse(info)

    response_json = simplejson.dumps(response)
    return HttpResponse(response_json)

def get_msgs(request,user_id):
    response = {}
    msgs = []
    page_msgs = []
    try:
        if request.method == 'GET':
            req = request.GET
            readed = req.get('readed')
            page = req.get('page') or 1
            amount = req.get('amount') or 20

            if readed == 'True':
                readed_bool = True
            elif readed == 'False':
                readed_bool = False
            else:
                readed_bool = None
            # 默认已读未读都显示
            if readed_bool == None:
                user_msgs = UserMessage.objects.filter(recv_user=user_id)
            else:
                user_msgs = UserMessage.objects.filter(recv_user=user_id,readed=readed_bool)

            for user_msg in user_msgs:
                if user_msg.message.status == 1:
                    continue
                print user_msg.status
                msg = {}
                msg['titile'] = user_msg.message.title
                msg['content'] = user_msg.message.content
                msg['category'] = user_msg.message.category
                msg['send_user'] = user_msg.send_user
                msg['readed'] = user_msg.readed
                msg['status'] = user_msg.message.status
                msg['create_time'] = user_msg.create_time.strftime('%Y-%m-%d %H:%M:%S')
                msgs.append(msg)

            # 默认每页显示20条信息
            paginator = Paginator(msgs, amount)

            if page > paginator.num_pages:
                page = paginator.num_pages
            object = paginator.page(page)
            for page_msg in object.object_list:
                page_msgs.append(page_msg)

    except:
        pass
    response['msgs'] = page_msgs
    response_json=simplejson.dumps(response)
    return HttpResponse(response_json)

def del_msg(request,msg_id):
    info = ""
    try:
        if request.method == 'GET':
            msg = Message.objects.get(id=msg_id)
            if msg.status == 1:
                info = "message have been deleted..."
            else:
                msg.status = 1
                msg.save()
                user_msgs = UserMessage.objects.filter(message=msg)
                for user_msg in user_msgs:
                    user_msg.status = 1
                    user_msg.save()
                info = "message delete successfully！"

    except:
        info= "%s || %s" % (sys.exc_info()[0], sys.exc_info()[1])
    return HttpResponse(info)