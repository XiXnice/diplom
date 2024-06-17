from distutils.util import strtobool

from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.request import Request
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from requests import get
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from ujson import loads as load_json
from yaml import load as load_yaml, Loader

from app.models import ConfirmEmailToken, User, KnowledgeBase, Forum
from app.serializers import UserSerializer, KnowledgeBaseArticleSerializer, TokenSerializer, ForumSerializer
from app.signals import new_user_registered


class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


class RegisterAccount(APIView):

    def get(self, request, *args, **kwargs):
        return render(request, 'pages/registration.html')

    def post(self, request, *args, **kwargs):
        if {'last_name', 'first_name', 'patronymic', 'email', 'password', 'password2'}.issubset(request.data):
            if request.data['password'] == request.data['password2']:
                sad = 'asd'
                try:
                    validate_password(request.data['password'])
                except Exception as password_error:
                    error_array = []
                    # noinspection PyTypeChecker
                    for item in password_error:
                        error_array.append(item)
                    return render(request, 'pages/registration.html', {'Status': False, 'Errors': error_array})
                else:
                    # проверяем данные для уникальности имени пользователя

                    user_serializer = UserSerializer(data=request.data)
                    if user_serializer.is_valid():
                        # сохраняем пользователя
                        user = user_serializer.save()
                        user.set_password(request.data['password'])
                        user.save()
                        return redirect('user-registration-confirm')
                    else:
                        return render(request, 'pages/registration.html',
                                      {'Status': False, 'Errors': user_serializer.errors})
            else:
                return render(request, 'pages/registration.html', {'Status': False, 'Errors': 'Пароли не совпадают'})

        return render(request, 'pages/registration.html',
                      {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class ConfirmAccount(APIView):
    """
    Класс для подтверждения почтового адреса
    """

    def get(self, request, *args, **kwargs):
        return render(request, 'pages/confirm_email.html')

    # Регистрация методом POST
    def post(self, request, *args, **kwargs):
        """
                Подтверждает почтовый адрес пользователя.

                Args:
                - request (Request): The Django request object.

                Returns:
                - JsonResponse: The response indicating the status of the operation and any errors.
                """
        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return redirect('user-login')
            else:
                return render(request, 'pages/confirm_email.html',
                              {'Status': False, 'Errors': 'Неправильно указан токен или email'})

        return render(request, 'pages/confirm_email.html',
                      {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class LoginAccount(APIView):

    def get(self, request, *args, **kwargs):
        return render(request, 'pages/authorization.html')

    def post(self, request, *args, **kwargs):
        """
                Authenticate a user.

                Args:
                    request (Request): The Django request object.

                Returns:
                    JsonResponse: The response indicating the status of the operation and any errors.
                """
        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user is not None:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    request.session['user_token'] = token.key
                    return redirect('index')

            return render(request, 'pages/authorization.html', {'Status': False, 'Errors': 'Не удалось авторизовать'})

        return render(request, 'pages/authorization.html',
                      {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class KnowledgeBaseArticle(ListAPIView):
    queryset = KnowledgeBase.objects.all()
    serializer_class = KnowledgeBaseArticleSerializer()

    def get(self, request, pk, *args, **kwargs):
        try:
            data = KnowledgeBase.objects.get(id=pk)
            return render(request, 'pages/knowledge_base_article.html',
                          {'data': KnowledgeBaseArticleSerializer(data).data})
        except KnowledgeBase.DoesNotExist:
            return render(request, 'pages/knowledge_base_article.html', {'error': status.HTTP_404_NOT_FOUND})


class CreatingKnowledgeBaseArticle(APIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'pages/creating_knowledge_base_article.html')

    def post(self, request, *args, **kwargs):
        try:
            token = request.session['user_token']
        except:
            token = None
        if token is not None:
            if {'theme', 'text'}.issubset(request.data):
                data_user = Token.objects.get(key=token).user_id
                serializer = KnowledgeBase.objects.create(theme=request.data['theme'], text=request.data['text'], user_id=data_user)
                serializer.save()
                return redirect('knowledgebase')
            else:
                return render(request, 'pages/creating_knowledge_base_article.html',
                              {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
        else:
            return render(request, 'pages/creating_knowledge_base_article.html',
                          {'Status': False, 'Errors': 'Вы не авторизованы'})


class KnowledgeBaseView(APIView):
    def get(self, request: Request, *args, **kwargs):
        knowledge_base = KnowledgeBase.objects.all()
        ser = KnowledgeBaseArticleSerializer(knowledge_base, many=True)
        return render(request, 'pages/knowledge_base.html', {'ser': ser.data})


class LogoutAccount(APIView):
    def get(self, request, *args, **kwargs):
        del request.session['user_token']
        return redirect('index')


class ForumView(APIView):
    def get(self, request: Request, *args, **kwargs):
        knowledge_base = Forum.objects.all()
        ser = ForumSerializer(knowledge_base, many=True)
        return render(request, 'pages/forum.html', {'ser': ser.data})


class ForumCreateView(APIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'pages/creating_forum.html')

    def post(self, request, *args, **kwargs):
        try:
            token = request.session['user_token']
        except:
            token = None
        if token is not None:
            if {'theme'}.issubset(request.data):
                data_user = Token.objects.get(key=token).user_id
                serializer = KnowledgeBase.objects.create(theme=request.data['theme'], user_id=data_user)
                serializer.save()
                return redirect('forum')
            else:
                return render(request, 'pages/creating_forum.html',
                              {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
        else:
            return render(request, 'pages/creating_forum.html',
                          {'Status': False, 'Errors': 'Вы не авторизованы'})

class ForumArticleView(APIView):
    def get(self, request: Request, *args, **kwargs):
        knowledge_base = Forum.objects.all()
        ser = ForumSerializer(knowledge_base, many=True)
        return render(request, 'pages/page_forum.html', {'ser': ser.data})