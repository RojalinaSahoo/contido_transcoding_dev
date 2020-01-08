from .models import *
import sys
from django.utils import timezone
import datetime
import time
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from utils.decorators import *
from django.contrib.sessions.models import Session
from django.shortcuts import HttpResponse, render_to_response, HttpResponseRedirect,render
from django.http import JsonResponse
from Contido_Transcode.models import UserInfo
from transcode.models import Transcode
from decouple import config
from rest_framework.response import Response
from rest_framework import views
from jwt import (
    JWT,
    jwk_from_dict,
    jwk_from_pem,
)

from .helperFunctions import *
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.permissions import IsAuthenticated
import json
from Contido_Transcode.views import LoginApi
from rest_framework.renderers import JSONRenderer
from Contido_Transcode.views import is_token_required



class TranscodeData(views.APIView):
    
    def post(self, request, *args, **kwargs):
        
        if not request.data:
            return Response({'Error': "Please provide data"}, status="400")
        try:
            job_action = request.data['action']
            commands = request.data['commands']
            location = request.data['location']
            master_file_path= request.data['master_file_path']
            timecode = request.data['timecode']
            archive_path = request.data['archive_path']
            output_format = request.data['output_format']
            input_file_path= request.data['input_file_path']
            upload_from = request.data['upload_from']
            upload_type = request.data['upload_type']
            content_type = request.data['content_type']
            shape_wav_id = request.data['shape_wav_id']
            shape_app_id = request.data['shape_app_id']
            shape_web_id = request.data['shape_web_id']
            is_mxf = request.data['is_mxf']
            shape_master_id = request.data['shape_master_id']
            shape_hls_id = request.data['shape_hls_id']
            thumbnail = request.data['thumbnail']
            thumbnail_preview = request.data['thumbnail_preview']
            partial_clipping = request.data['partial_clipping']
            input_file_path_mp4= request.data['input_file_path_mp4']
            audio_tracks= request.data['audio_tracks']
            print(audio_tracks)
        except Exception as e:
            print(e)
            return Response({'Error': "Invalid parameter"}, status="400")

        try:
            transcode_data= Transcode()
            current_time = int(datetime.datetime.now().timestamp())
            data_current_time=datetime.datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S")
            transcode_data.creation= data_current_time
            print(transcode_data.creation)
            job_id= generate_job_id()
            print("Job Id:",job_id)
            transcode_data.job_id = job_id 
            transcode_data.job_action= job_action
            transcode_data.commands = commands
            transcode_data.location = location
            transcode_data.master_file_path = master_file_path
            transcode_data.timecode = timecode                      
            transcode_data.archive_path = archive_path
            transcode_data.output_format = output_format
            transcode_data.input_file_path = input_file_path
            transcode_data.upload_from = upload_from
            transcode_data.upload_type = upload_type
            transcode_data.asset_type = content_type
            transcode_data.shape_wav_id = shape_wav_id
            transcode_data.shape_app_id = shape_app_id
            transcode_data.shape_web_id = shape_web_id
            transcode_data.is_mxf = is_mxf
            transcode_data.shape_master_id = shape_master_id
            transcode_data.shape_hls_id = shape_hls_id
            transcode_data.thumbnail = thumbnail
            transcode_data.thumbnail_preview = thumbnail_preview
            transcode_data.partial_clipping = partial_clipping
            transcode_data.input_file_path_mp4 = input_file_path_mp4
            transcode_data.audio_tracks = audio_tracks
            transcode_data.save()
            job_status=transcode_data.job_status
            print("data added Successfully")
            return Response({'message': "success","Job ID":job_id,"Job_status":job_status}, status="200")
        except Exception as e:
            print(e)
            return Response({"error":"Invalid data"},status="400")

class TranscodeDetail(views.APIView):

    def post(self, request, *args, **kwargs):
    
        if not request.data:
            return Response({'Error': "Please provide data"}, status="400")
        try:
            email = request.data['email']
            organisation = request.data['organisation']
            job_id = request.data['job_id']
        except Exception as e:
            print(e)
            return Response({'Error': "Invalid parameter"}, status="400")
        try:
            user = UserInfo.objects.filter(username=email)

            for user_data in user:
                 username = user_data.username
                 project_title = user_data.project_title

            if project_title != organisation:
                 return Response({'Error': "project title not associated with user"}, status="400")
        except Exception as e:
            print(e)
            return Response({'Error': "Your profile doesn't exist with us."}, status="400")

        try:
            job_data = Transcode.objects.get(job_id=job_id)
            job_id = job_data.job_id
            job_status = job_data.job_status
            job_starttime= job_data.job_starttime
            print("job startime:",job_starttime)
            print("job_id:",job_id)
            print("job_status:",job_status)
        except Exception as e:
            print(e)
            return Response({'Error': "Job id doesn't exists"}, status="400")

        return Response({"message": "success","job_id":job_id,"job_status":job_status,"job_starttime":job_starttime},status="200")
        
@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})

@api_view(['POST'])
@is_token_required
def transcode_data(request):

    params= json.loads(request.body)
    print(request.META['HTTP_HOST'])
    server_hostname= request.META['HTTP_HOST']
    if not params:
        return Response({'message': "Please provide data",'data':None,'status':400})

    try:
        job_action = params.get('action')
        commands = params.get('commands')
        location = params.get('location')
        master_file_path= params.get('master_file_path')
        timecode = params.get('timecode')
        archive_path = params.get('archive_path')
        output_format = params.get('output_format')
        input_file_path= params.get('input_file_path')
        upload_from = params.get('upload_from')
        upload_type = params.get('upload_type')
        content_type = params.get('content_type')
        shape_wav_id = params.get('shape_wav_id')
        shape_app_id = params.get('shape_app_id')
        shape_web_id = params.get('shape_web_id')
        is_mxf = params.get('is_mxf')
        shape_master_id = params.get('shape_master_id')
        shape_hls_id = params.get('shape_hls_id')
        thumbnail = params.get('thumbnail')
        thumbnail_preview = params.get('thumbnail_preview')
        partial_clipping = params.get('partial_clipping')
        input_file_path_mp4= params.get('input_file_path_mp4')
        audio_tracks= params.get('audio_tracks')
        #data = params.get('data',None)
        audio_house_format = params.get('audio_house_format',None)
        mediainfo = params.get('mediainfo',None)
    except Exception as e:
        print(e)
        return Response({'message': "Invalid parameter",'data':None,'status':401})

    try:
        transcode_data= Transcode()
        current_time = int(datetime.datetime.now().timestamp())
        data_current_time=datetime.datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S")
        transcode_data.creation= data_current_time
        print(transcode_data.creation)
        job_id= generate_job_id()
        print("Job Id:",job_id)
        transcode_data.job_id = job_id 
        transcode_data.job_action= job_action
        transcode_data.commands = commands
        transcode_data.location = location
        transcode_data.master_file_path = master_file_path
        transcode_data.timecode = timecode                      
        transcode_data.archive_path = archive_path
        transcode_data.output_format = output_format
        transcode_data.input_file_path = input_file_path
        transcode_data.upload_from = upload_from
        transcode_data.upload_type = upload_type
        transcode_data.asset_type = content_type
        transcode_data.shape_wav_id = shape_wav_id
        transcode_data.shape_app_id = shape_app_id
        transcode_data.shape_web_id = shape_web_id
        transcode_data.is_mxf = is_mxf
        transcode_data.shape_master_id = shape_master_id
        transcode_data.shape_hls_id = shape_hls_id
        transcode_data.thumbnail = thumbnail
        transcode_data.thumbnail_preview = thumbnail_preview
        transcode_data.partial_clipping = partial_clipping
        transcode_data.input_file_path_mp4 = input_file_path_mp4
        transcode_data.audio_tracks = audio_tracks
        #transcode_data.data = data
        #transcode_data.originalMessage = params
        transcode_data.audio_house_format = audio_house_format
        transcode_data.mediainfo = mediainfo
        transcode_data.save()
        job_status = transcode_data.job_status
        job_id = transcode_data.job_id
        _id = transcode_data.id
        print(_id)
        job_starttime = transcode_data.job_starttime
        job_endtime = transcode_data.job_endtime
        transcode_data.response_formatter = [{  'end_point':server_hostname+'/api/transcode/update/job/status/','request_type':'POST','parameter':{'job_status':job_status,'job_id':job_id,'transcode_db_id':str(_id),'job_start_time':job_starttime,'job_end_time':job_endtime}}]
        transcode_data.update(response_formatter=transcode_data.response_formatter)
        response_formatter= transcode_data.response_formatter
        response_formatter_list=[]
        for response_formatter_data in response_formatter:
            response_formatter_list.append(response_formatter_data)
        #print ("abcd", response_formatter_list)
        re= response_formatter_list[0]
        param=re['parameter']
        print(param)
        print("data added Successfully")
        
        return JsonResponse ({"message": "success", "data" : param, "status":200})
    except Exception as e:
        print(e)
        return Response({"message":"Invalid data",'data':None,'status':403})
#from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@is_token_required
def transcode_detail(request):

    params= json.loads(request.body)
    #print(request.META['HTTP_HOST'])
    #print(request.META['HTTP_AUTHORIZATION'])
    if not params:
        return Response({'message': "Please provide data",'data':None,'status':400})
    try:
        email= params.get("email",None)
        organisation = params.get("organisation",None)
        job_id = params.get("job_id",None)
    except Exception as e:
        print(e)
        return Response({'message': "Invalid parameter",'data':None,'status':401})
    #try:
    #    user = UserInfo.objects.filter(username=email)

    #    for user_data in user:
    #         username = user_data.username
    #         project_title = user_data.project_title

    #    if project_title != organisation:
    #         return Response({'message': "project title not associated with user",'data':None,'status':403})
    #except Exception as e:
    #    print(e)
    #    return Response({'message': "Your profile doesn't exist with us.",'data':None,'status':403})

    try:
        job_data = Transcode.objects.get(job_id=job_id)
        job_id = job_data.job_id
        job_status = job_data.job_status
        job_starttime= job_data.job_starttime
        audio_tracks = job_data.audio_tracks
        #mediainfo = job_data.mediainfo
        print("job startime:",job_starttime)
        print("job_id:",job_id)
        print("job_status:",job_status)
        print("audio_tracks:",audio_tracks)
        data= {"job_id":job_id,"job_status":job_status,"job_starttime":job_starttime,}
        #print("mediainfo:",mediainfo)
    except Exception as e:
        print(e)
        return Response({'message': "Job id doesn't exists",'data':None,'status':403})

    return Response({"message": "success","data":data,"status":200})
    
def transcode_detail_webapi(request):

    transcode_data = Transcode.objects.filter(asset_type="show",location="hyd_hub")
    transcode=[]
    for data in transcode_data:
        
        transcode.append({'job_id':data.job_id,'job_status':data.job_status,'job_starttime':data.job_starttime})
    
    return JsonResponse ({"data":transcode})

@api_view(['POST'])
@is_token_required
def transcode_job_update(request):

    params= json.loads(request.body)
    if not params:
        return Response({'message': "Please provide data",'data':None,'status':400})
    try:
        job_id= params.get("job_id",None)
        job_status = params.get("job_status",None)
    except Exception as e:
        print(e)
        return Response({'message': "Invalid parameter","data":None,"status":401})
    try:
        data = Transcode.objects.filter(job_id=job_id)

        for transcode_data in data:
            #job_status_updated = transcode_data.job_status
            transcode_data.update(job_status=job_status)
            transcode_data.save()
             
    except Exception as e:
        print(e)
        return Response({'message': "Job id doesn't exists","data":None,"status":403})
    signals.post_save.connect(Transcode.post_save, sender=Transcode)
    return JsonResponse({'data':"OK","message":"success","status":200})

#{"job_status":0,
#"job_id":0,
#"transcode_db_id":"11",
#"job_start_time":"2020-01-03T12:38:48.255Z",
#"job_end_time":"2020-01-03T12:45:48.255Z"
#}

@api_view(['POST'])
@is_token_required
def transcode_job_update_status(request):
    params= json.loads(request.body)
    if not params:
        return Response({'message': "Please provide data",'data':None,'status':400})
    try:
        job_status= params.get("job_status",None)
        job_id= params.get("job_id",None)
        transcode_db_id = params.get("transcode_db_id",None)
        job_starttime = params.get("job_start_time",None)
        job_endtime = params.get("job_end_time",None)
    except Exception as e:
        print(e)
        return Response({'message': "Invalid parameter",'data':None,'status':402})
    try:
        start_datetime = datetime.datetime.strptime(job_starttime, "%Y-%m-%dT%H:%M:%S")
        end_datetime= datetime.datetime.strptime(job_endtime, "%Y-%m-%dT%H:%M:%S")
    except:
        return Response({"message":"Invalid datetime format",'data':None,'status':403})
    modified_at = datetime.datetime.now()

    try:
        transcode = Transcode.objects.filter(id=transcode_db_id,job_id=job_id)

        for transcode_data in transcode:
            transcode_data.update(job_status=job_status)
            #transcode_data.update(job_id=job_id)
            transcode_data.update(job_starttime=start_datetime)
            transcode_data.update(job_endtime=end_datetime)
            transcode_data.update(modified_at=modified_at)
        print(transcode_data.job_id)
        print(transcode_data.id)
        data = {'job_id':transcode_data.job_id, 'transcode_id': str(transcode_data.id)}
    except Exception as e:
        print(e)
        return Response({'message': "Transcode id doesn't exists",'data':None,'status':403})

    return Response({"message": "updated","data":data,'status':200})


