from django.urls import path
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('blogposts/', views.blogposts, name = 'blogposts'),
    path('blogposts/<int:pk>/', views.post_details, name = 'post_details'), #post+kom, brisanje, menjanje

    path('blogposts/<int:pk>/comments/', views.comments, name = 'comments'), #citam sve komentare i dodajem novi
    path('comments/<int:id>/', views.comments_details, name = 'comments_details'),

    path('register_user/', views.register_user, name = 'register_user'),
    path('login_user/', views.login_user, name = 'login_user'),
    path('logout_user/', views.logout_user, name = 'logout_user'),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]