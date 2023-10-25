from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from api.views import UserNotificationsViewSet
from tasks.views import TaskViewSet
from users.views import CustomDjUserViewSet, ShortUserProfileViewSet

router = DefaultRouter()
router.register(r'users', CustomDjUserViewSet, basename='users')
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(
    r'notifications', UserNotificationsViewSet, basename='user-notifications'
)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls.authtoken')),
    path(
        'curent_user_info/',
        ShortUserProfileViewSet.as_view({'get': 'list'}),
        name='user_profile_info',
    ),
    path(
        'user/my_notifications/',
        UserNotificationsViewSet.as_view({'get': 'list'}),
        name='user-notifications',
    ),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'swagger/',
        SpectacularSwaggerView.as_view(url_name='api:schema'),
        name='swagger',
    ),
]
