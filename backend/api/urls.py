from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'tasks', TaskViewSet, basename='tasks')

app_name = 'api'

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include(router.urls)),
    path('auth/tasks/accept_task/<int:pk>/', TaskViewSet.as_view({'post': 'accept_task'}), name='accept_task'),
]