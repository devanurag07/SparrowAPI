from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from accounts.models import User, LoginOtp
import random
from sparrow.utils import required_data, resp_fail, resp_success, get_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OtpTempData
from .services import send_otp,verify_otp
# Create your views here.


class AuthAPI(ViewSet):

    @action(methods=["POST"], detail=False, url_path="send_otp")
    def send_otp(self, request, *args, **kwargs):
        data=request.data
        success,req_data=required_data(data,["mobile"])
        if(not success):
            return Response(resp_fail("Mobile No. Required "))
        
        mobile,=req_data
        try:
            #Verification Goes Here
            mobile=int(mobile)
        except Exception as e:
            return Response(resp_fail("Mobile No Not Valid.."))

        users_list=User.objects.filter(mobile=mobile)
        user_exist=users_list.exists()

        return send_otp(user_exist,mobile,data)


    @action(methods=["POST"], detail=False, url_path="verify_otp")
    def verify_otp(self, request, *args, **kwargs):
        data = request.data
        success, req_data = required_data(data, ["mobile", "otp"])

        if(not success):
            return Response(resp_fail("[mobile,otp] Is Required ..."))

        mobile, otp = req_data
        users_list=User.objects.filter(mobile=mobile)

        return verify_otp(users_list,mobile,otp)