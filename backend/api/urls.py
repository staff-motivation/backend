from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from .views import CustomUserViewSet, TaskViewSet, ShortUserProfileViewSet, UserNotificationsViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'notifications', UserNotificationsViewSet, basename='user-notifications')

app_name = 'api'

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('curent_user_info/', ShortUserProfileViewSet.as_view({'get': 'list'}), name='user_profile_info'),
    path('users/my_notifications/', UserNotificationsViewSet.as_view({'get': 'list'}), name='user-notifications'),
    path('tasks/accept_task/<int:pk>/', TaskViewSet.as_view({'post': 'accept_task'}), name='accept_task'),
    path('/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('/swagger/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger'),
]
