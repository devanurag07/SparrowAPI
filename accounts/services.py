from .models import User,LoginOtp,OtpTempData
import random
from rest_framework.response import Response
from sparrow.utils import resp_fail,resp_success,required_data
from rest_framework_simplejwt.tokens import RefreshToken

def delete_otps(user_exist,mobile):
    if(user_exist):
        LoginOtp.objects.filter(mobile=mobile).delete()
    else:
        OtpTempData.objects.filter(mobile=mobile).delete()

def send_otp(user_exist,mobile,data):
    delete_otps(user_exist,mobile)
    if(user_exist):
        #Login
        otp=random.randint(10000,99999)
        otp_obj=LoginOtp(otp=otp,mobile=mobile)
        otp_obj.save()
        return Response(resp_success("OTP Sent Successfully!",{"otp":otp,"mobile":mobile}))
    else:
        #SignUP
        success,req_data=required_data(data,["first_name","last_name"])
        if(not success):
            return Response(resp_fail("[first_name,last_name] Required..."))
        
        first_name,last_name=req_data
        otp=random.randint(10000,99999)

        otp_obj=OtpTempData(first_name=first_name,last_name=last_name,otp=otp,mobile=mobile)
        otp_obj.save()

        return Response(resp_success("OTP Sent Successfully!",{"otp":otp,"mobile":mobile}))

def verify_otp(users_list,mobile,otp):
    action=""
    user_exist=users_list.exists()
    if(user_exist):
        user_otp = LoginOtp.objects.filter(mobile=mobile)
        user=users_list.first()
        action="Login"
    else:
        action="SignUp"
        user_otp=OtpTempData.objects.filter(mobile=mobile)

    if(user_otp.exists()):
        user_otp = user_otp.first()
        if(user_otp.otp == int(otp)):
            if(not user_exist):
                user=User.objects.create(first_name=user_otp.first_name,last_name=user_otp.last_name,mobile=mobile)
            
            delete_otps(user_exist,mobile)
            token = RefreshToken.for_user(user)
            return Response(resp_success(f"Token Fetched Successfully [{action}]", {
                "refresh": str(token),
                "token": str(token.access_token)
            }))

        else:
            attempts = 5-user_otp.attempts
            user_otp.attempts += 1
            user_otp.save()
            if(attempts <= 0):
                if(user_exist):
                    LoginOtp.objects.filter(mobile=mobile).delete()
                else:
                    OtpTempData.objects.filter(mobile=mobile).delete()

                return Response(resp_fail("No OTP Found.."))
            return Response(resp_fail(f"Wrong OTP Attempts - {attempts} LEFT"))

    else:
        return Response(resp_fail("No OTP Found.."))
