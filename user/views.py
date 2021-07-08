import json
import uuid

from django.http import HttpResponseRedirect


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.template.loader import render_to_string
from random import choices
import string
from .serializers import *
from .models import *
from rest_framework import generics




class UserUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        userData = json.loads(request.data['userData'])
        serializer = UserSerializer(user, data=userData)
        if userData.get('pass') != '':
            user.set_password(userData.get('pass'))
            user.save()
        if serializer.is_valid():
            serializer.save()
            for f in request.FILES.getlist('avatar'):
                user.avatar = f
                user.save(force_update=True)
            return Response(status=200)
        else:
            return Response(status=400)


class GetUser(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user
    # def get(self, request):
    #     user = request.user
    #     serializer = UserSerializer(user, many=False)
    #     return Response(serializer.data)


class UserRecoverPassword(APIView):
    def post(self,request):
        user = None
        print(request.data['email'])
        try:
            user = User.objects.get(email=request.data['email'])
        except:
            user = None
        if user:
            password=''.join(choices(string.digits, k=8))
            print(password)
            user.set_password(password)
            user.save()
            msg_html = render_to_string('new_password.html', {'pass': password})
            send_mail('Ваш новый пароль docsuniform.ru', None, 'noreply@docsuniform.ru',
                      [user.email,'dimon.skiborg@gmail.com'],
                      fail_silently=False, html_message=msg_html)
            return Response({'result': True, 'email': user.email}, status=200)


        else:
            return Response({'result': False}, status=200)
