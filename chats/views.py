import datetime
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import ConversationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import Conversation, Message, GroupChat
from sparrow.utils import resp_fail, resp_success
from django.db.models import Q
from sparrow.utils import required_data
from .serializers import MessageSerializer, ImageSerializer, DocumentSerializer
from accounts.models import User
from rest_framework.decorators import action
from rest_framework import status
from sparrow.utils import phone_format
from .models import DeletedConversation
from .utils import get_conv_messages
# Create your views here.


class ConversationAPI(ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        conversation_list = Conversation.objects.filter(
            Q(user1=user) | Q(user2=user))
        return conversation_list

    def create(self, request, *args, **kwargs):
        return Response(resp_fail("Methdod Not Allowed"))

    def list(self, request, *args, **kwargs):
        conversations = self.get_queryset()

        data = ConversationSerializer(conversations,
                                      many=True,
                                      context={
                                          "request": request
                                      }).data
        return Response(
            resp_success("Conversations Fetched Successfully", {"data": data}))

    def retrieve(self, request, pk=None, *args, **kwargs):
        if (not pk):
            return Response(resp_fail("Conversation ID Required.."))

        conv = self.get_queryset().filter(pk=pk)
        if (not conv.exists()):
            return Response(resp_fail("Conversation Does Not Exist..."))
        conv = conv.first()

        user = self.request.user

        class ConvSerializer(serializers.ModelSerializer):
            messages = serializers.SerializerMethodField(
                read_only=True)
            receiver_info = serializers.SerializerMethodField(read_only=True)
            avatar = serializers.SerializerMethodField(read_only=True)

            def get_receiver_info(self, instance):
                receiver_user = None
                current_user = self.context["request"].user
                if (current_user == instance.user1):
                    receiver_user = instance.user2
                else:
                    receiver_user = instance.user1

                data = {
                    "receiver_name":
                    receiver_user.first_name + " " + receiver_user.last_name,
                    "bio":
                    receiver_user.bio,
                    "mobile":
                    receiver_user.mobile
                }
                return data

            def get_avatar(self, instance):
                current_user = request.user
                print(current_user)

                if (current_user == instance.user1):
                    return '/media/' + instance.user2.profile_pic.name
                else:
                    return '/media/' + instance.user1.profile_pic.name

            def get_messages(self, instance):

                messages = get_conv_messages(instance, user)
                return MessageSerializer(messages, many=True).data

            class Meta:
                model = Conversation
                fields = "__all__"

        conv_data = ConvSerializer(conv,
                                   many=False,
                                   context={
                                       "request": request
                                   }).data
        return Response(
            resp_success("Conversation Fetched Successfully.", conv_data))

    def update(self, request, *args, **kwargs):
        return Response(resp_fail("Methdod Not Allowed"))

    def destroy(self, request, pk=None, *args, **kwargs):
        if (pk):
            queryset = self.get_queryset()
            convs = queryset.filter(pk=int(pk))
            if (convs.exists()):
                # convs.delete()
                conv = convs.first()
                deleted_conv, created = DeletedConversation.objects.get_or_create(
                    user=self.request.user, conv=conv)

                if (created):
                    pass
                else:
                    deleted_conv.deleted_at = datetime.datetime.now()
                    deleted_conv.save()

                return Response(resp_success("Conversation Deleted"))

            return Response(resp_fail("Conversation Not Found..."))

        return Response(resp_fail("Conversation ID Required."))

    @action(methods=["POST"], detail=False, url_path="get_available_users")
    def get_available_users(self, request):
        data = request.data
        success, req_data = required_data(data, ["numbers_list"])
        if (not success):

            errors = req_data
            return Response(resp_fail("Invalid Data Provided", data=errors))

        numbers_list, = req_data
        if (type(numbers_list) == list):
            avail_users = []
            for number in numbers_list:
                number_unchanged = number
                formatted = phone_format(number)
                if (not (len(formatted) == 10)):
                    continue

                number = int("".join(formatted.split("-")))

                users = User.objects.filter(mobile=int(number))

                available = users.exists()
                if (available):
                    user = users.first()
                    avail_users.append({
                        "mobile": number_unchanged,
                        "exists": True,
                        "bio": user.bio,
                        "profile_pic": '/media/'+str(user.profile_pic)
                    })

                else:
                    avail_users.append({"mobile": number, "exists": False})

            return Response(
                resp_success("Fetched Available Users", avail_users))

        elif (str(numbers_list).isnumeric()):
            number = numbers_list
            formatted = phone_format(number)
            if (not (len(formatted) == 10)):
                return Response(
                    resp_success("Success",
                                 data=[[]]))

            number = int("".join(formatted.split("-")))

            users = User.objects.filter(mobile=int(number))
            available = users.exists()

            if (available):
                user = users.first()
                return Response(
                    resp_success("Success",
                                 data=[{
                                     "exists": True,
                                     "mobile": numbers_list,
                                     "bio": user.bio,
                                     "profile_pic": '/media/' + str(user.profile_pic)
                                 }]))

            else:
                return Response(
                    resp_success(
                        "Success",
                        data=[{
                            "exists": False,
                            "mobile": numbers_list,
                            #  "profile_pic": user.profile_pic
                        }]))

        else:
            return Response(resp_fail("Invalid Mobile Numbers...."))

    @action(methods=["POST"], detail=False, url_path="get_conv")
    def get_conv(self, request):

        class ConvSerializer(serializers.ModelSerializer):
            messages = MessageSerializer(many=True)
            receiver_info = serializers.SerializerMethodField(read_only=True)
            avatar = serializers.SerializerMethodField(read_only=True)

            def get_receiver_info(self, instance):
                receiver_user = None
                current_user = self.context["request"].user
                if (current_user == instance.user1):
                    receiver_user = instance.user2
                else:
                    receiver_user = instance.user1

                data = {
                    "receiver_name":
                    receiver_user.first_name + " " + receiver_user.last_name,
                    "bio":
                    receiver_user.bio,
                    "mobile":
                    receiver_user.mobile
                }
                return data

            def get_avatar(self, instance):
                current_user = request.user
                print(current_user)

                if (current_user == instance.user1):
                    return '/media/' + instance.user2.profile_pic.name
                else:
                    return '/media/' + instance.user1.profile_pic.name

            class Meta:
                model = Conversation
                fields = "__all__"

        data = request.data
        success, req_data = required_data(data, ["mobile"])
        if (not success):
            errors = req_data
            return Response(resp_fail("Invalid Data Provided", data=errors))

        mobile, = req_data
        convs = Conversation.objects.filter(
            Q(user1__mobile=int(mobile)) | Q(user2__mobile=int(mobile)))

        if (convs.exists()):
            conv = convs.first()
            data = ConvSerializer(conv,
                                  many=False,
                                  context={
                                      "request": request
                                  }).data

            return Response(
                resp_success("Conv Fetched...",
                             data={
                                 "exists": True,
                                 "conv": data
                             }))
        return Response(
            resp_success("Response Doesn't Exists...", data={"exists": False}))


class ChatAPI(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.filter(sender=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        return Response("Method Not Allowed",
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        data = request.data
        success, req_data = required_data(
            data, ["mobile", "message"])
        if (not success):
            return Response(resp_fail("[Mobile , Message] Required.."))

        mobiles, message = req_data
        if len(mobiles) == 1:
            user = request.user
            receivers = User.objects.filter(mobile=mobiles[0])
            if (receivers.exists()):
                reciever = receivers.first()
            else:
                return Response(resp_fail("Reciever Doesn't Exist"))

            conv = Conversation.objects.filter(
                Q(user1=user, user2=reciever) | Q(user1=reciever, user2=user))

            if (conv.exists()):
                created = False
                conv = conv.first()
            else:
                created = True
                conv = Conversation.objects.create(user1=user, user2=reciever)

            message = Message(conversation=conv,
                              sender=user,
                              reciever=reciever,
                              message=message,
                              replyOf=data['replyof']
                              )
            message.save()

            data = MessageSerializer(message, many=False).data
            data["created"] = created
            return Response(resp_success("Msg Sent...", data))

        else:
            user = request.user
            receivers = User.objects.filter(mobile=mobiles)
            if (receivers.exists()):
                reciever = receivers.first()
            else:
                return Response(resp_fail("Reciever Doesn't Exist"))

            conv = Conversation.objects.filter(
                Q(user1=user, user2=reciever) | Q(user1=reciever, user2=user))

            group = GroupChat.objects.filter(created_by=user)
            if (conv.exists()):
                created = False
                conv = conv.first()
            else:
                created = True
                conv = Conversation.objects.create(user1=user, user2=reciever)

            message = Message(conversation=conv,
                              sender=user,
                              reciever=reciever,
                              message=message,
                              replyOf=data['replyof']
                              )
            message.save()

            data = MessageSerializer(message, many=False).data
            data["created"] = created
            return Response(resp_success("Msg Sent...", data))

    def update(self, request, *args, **kwargs):
        return Response(
            resp_success("Stared",
                         request.data))

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(methods=["POST"], detail=False, url_path="star_message")
    def star_message(self, request):
        try:
            message = Message.objects.filter(
                id=int(request.data['message_id']))[0]

            message.isStarred = request.data['isStarred']

            message.save()
            message = MessageSerializer(
                message, many=False)

            return Response(
                resp_success("Message Starred",
                             message.data))
        except Exception:
            return Response(
                resp_fail("Failed To Star Message",
                          {"errors": ''})
            )

    @action(methods=["POST"], detail=False, url_path="message_status")
    def message_status(self, request):
        try:
            message = Message.objects.filter(
                id=int(request.data['message_id']))[0]

            statusDict = {
                'sent': 0,
                'delivered': 1,
                'seen': 2
            }

            message.status = statusDict[request.data['status']]

            message.save()
            message = MessageSerializer(
                message, many=False)

            return Response(
                resp_success("Message Status Changed",
                             message.data))
        except Exception:
            return Response(
                resp_fail("Failed To Change Message Status",
                          {"errors": ''}))

    @action(methods=["POST"], detail=False, url_path="send_file")
    def send_image(self,  request):
        # request.data["status"] = request.user.id
        if request.data['isImageFile'] == 'true':

            image_form = ImageSerializer(
                data=request.data)
            if (image_form.is_valid()):
                image_form.save()
                return Response(
                    resp_success("Image Send Successfully",
                                 {"data": image_form.data}))
            else:
                return Response(
                    resp_fail("Failed To Send Image",
                              {"errors": image_form.errors}))
        else:
            document_form = DocumentSerializer(
                data=request.data)
            if (document_form.is_valid()):
                document_form.save()
                return Response(
                    resp_success("Document Send Successfully",
                                 {"data": document_form.data}))
            else:
                return Response(
                    resp_fail("Failed To Send Image",
                              {"errors": document_form.errors}))
