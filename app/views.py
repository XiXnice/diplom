from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.request import Request
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from app.models import ConfirmEmailToken, User, KnowledgeBase, Forum, MessageForum, Patterns, MessagePatterns
from app.serializers import UserSerializer, KnowledgeBaseArticleSerializer, TokenSerializer, ForumSerializer, \
    PatternsSerializer
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

    def put(self, request, *args, **kwargs):
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
                    data_user = Token.objects.get(key=token).user_id
                    request.session['user_id'] = data_user
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
    def get(self, request, *args, **kwargs):
        forum = Forum.objects.all()
        ser = ForumSerializer(forum, many=True)
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
                serializer = Forum.objects.create(theme=request.data['theme'], user_id=data_user)
                serializer.save()
                return redirect('forum')
            else:
                return render(request, 'pages/creating_forum.html',
                              {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
        else:
            return render(request, 'pages/creating_forum.html',
                          {'Status': False, 'Errors': 'Вы не авторизованы'})


class ForumPageView(ListAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer()

    def get(self, request, pk, *args, **kwargs):
        try:
            try:
                token = request.session['user_token']
            except:
                token = None
            serializer = Forum.objects.filter(id=pk)
            data_mes = MessageForum.objects.filter(forum_id=pk)
            data_user = User.objects.all()
            return render(request, 'pages/page_forum.html',
                          {'data_mes': data_mes, 'data_user': data_user, 'data_forum': serializer[0]})
        except MessageForum.DoesNotExist:
            return render(request, 'pages/page_forum.html', {'error': status.HTTP_404_NOT_FOUND})

    def post(self, request, pk,*args, **kwargs):
        try:
            token = request.session['user_token']
        except:
            token = None
        if token is not None:
            if {'text'}.issubset(request.data):
                data_user = Token.objects.get(key=token).user_id
                serializer = MessageForum.objects.create(text=request.data['text'], user_id=data_user, forum_id=pk)
                serializer.save()
                return redirect('forum')
            else:
                return render(request, 'pages/page_forum.html',
                              {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
        else:
            return render(request, 'pages/page_forum.html',
                          {'Status': False, 'Errors': 'Вы не авторизованы'})


class ProfileView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer()

    def get(self, request, pk, *args, **kwargs):
        try:
            token = request.session['user_token']
        except:
            token = None
        if token is not None:
            data_user_id = Token.objects.get(key=token).user_id
            forum = Forum.objects.filter(user_id=data_user_id)
            pattern = Patterns.objects.filter(user_id=data_user_id)
            base = KnowledgeBase.objects.filter(user_id=data_user_id)
            return render(request, 'pages/profile.html', {'forum': forum, 'pattern': pattern, 'base': base})
        else:
            return render(request, 'pages/profile.html',
                          {'Status': False, 'Errors': 'Вы не авторизованы'})

    def post(self, request, pk, *args, **kwargs):
        if {'last_name', 'first_name', 'patronymic', 'email'}.issubset(request.data):
            data_user_id = Token.objects.get(key=request.session['user_token']).user_id
            forum = Forum.objects.filter(user_id=data_user_id)
            pattern = Patterns.objects.filter(user_id=data_user_id)
            base = KnowledgeBase.objects.filter(user_id=data_user_id)
            user = User.objects.get(id=pk)
            user.last_name = request.data['last_name']
            user.first_name = request.data['first_name']
            user.patronymic = request.data['patronymic']
            user.email = request.data['email']
            user.save()
            return render(request, 'pages/profile.html', {'forum': forum, 'pattern': pattern, 'base': base})
        return render(request, 'pages/profile.html',
                      {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class PatternView(APIView):
    def get(self, request, *args, **kwargs):
        forum = Patterns.objects.all()
        ser = PatternsSerializer(forum, many=True)
        return render(request, 'pages/patterns.html', {'ser': ser.data})


class PatternCreateView(APIView):
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
                serializer = Forum.objects.create(theme=request.data['theme'], user_id=data_user)
                serializer.save()
                return redirect('forum')
            else:
                return render(request, 'pages/creating_forum.html',
                              {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
        else:
            return render(request, 'pages/creating_forum.html',
                          {'Status': False, 'Errors': 'Вы не авторизованы'})


class PatternPageView(ListAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer()

    def get(self, request, pk, *args, **kwargs):
        try:
            try:
                token = request.session['user_token']
            except:
                token = None
            serializer = Forum.objects.filter(id=pk)
            data_mes = MessageForum.objects.filter(forum_id=pk)
            data_user = User.objects.all()
            return render(request, 'pages/page_forum.html',
                          {'data_mes': data_mes, 'data_user': data_user, 'data_forum': serializer[0]})
        except MessageForum.DoesNotExist:
            return render(request, 'pages/page_forum.html', {'error': status.HTTP_404_NOT_FOUND})

    def post(self, request, pk,*args, **kwargs):
        try:
            token = request.session['user_token']
        except:
            token = None
        if token is not None:
            if {'text'}.issubset(request.data):
                data_user = Token.objects.get(key=token).user_id
                serializer = MessageForum.objects.create(text=request.data['text'], user_id=data_user, forum_id=pk)
                serializer.save()
                return redirect('forum')
            else:
                return render(request, 'pages/page_forum.html',
                              {'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
        else:
            return render(request, 'pages/page_forum.html',
                          {'Status': False, 'Errors': 'Вы не авторизованы'})