from api.serializers import CustomUserCreateSerializer
from users.models import User
from rest_framework import viewsets


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer
