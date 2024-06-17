from django.urls import path

from app.views import IndexView, RegisterAccount, ConfirmAccount, LoginAccount, KnowledgeBaseView, LogoutAccount, \
    KnowledgeBaseArticle, CreatingKnowledgeBaseArticle, ForumView, ForumArticleView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('user/registration/', RegisterAccount.as_view(), name='user-registration'),
    path('user/registration/confirm/', ConfirmAccount.as_view(), name='user-registration-confirm'),
    path('user/login/', LoginAccount.as_view(), name='user-login'),
    path('user/logout/', LogoutAccount.as_view(), name='user-logout'),
    path('knowledgebase/', KnowledgeBaseView.as_view(), name='knowledgebase'),
    path('knowledgebase/create/', CreatingKnowledgeBaseArticle.as_view(), name='knowledgebase-create'),
    path('knowledgebase/<int:pk>/', KnowledgeBaseArticle.as_view(), name='knowledgebase-article'),
    path('forum/', ForumView.as_view(), name='forum'),
    path('forum/create/', CreatingKnowledgeBaseArticle.as_view(), name='forum-create'),
    path('forum/<int:pk>/', ForumArticleView.as_view(), name='forum-article'),
]