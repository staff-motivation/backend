import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Task

User = get_user_model()

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def team_leader_user():
    return User.objects.create_user(username='team_leader', password='password', role='team_leader')

@pytest.fixture
def normal_user():
    return User.objects.create_user(username='user', password='password', role='normal')

@pytest.fixture
def task_data():
    return {
        'title': 'Sample Task',
        'description': 'This is a sample task description',
        'status': 'created',
        # other fields...
    }

@pytest.mark.django_db
def test_create_task_team_leader(client, team_leader_user, task_data):
    client.force_authenticate(user=team_leader_user)
    response = client.post('/api/tasks/', task_data)
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_task_normal_user(client, normal_user, task_data):
    client.force_authenticate(user=normal_user)
    response = client.post('/api/tasks/', task_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_edit_task_team_leader(client, team_leader_user):
    task = Task.objects.create(title='Sample Task', status='created', creator=team_leader_user)
    client.force_authenticate(user=team_leader_user)
    response = client.patch(f'/api/tasks/{task.id}/', {'status': 'in_progress'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'in_progress'

@pytest.mark.django_db
def test_edit_task_normal_user(client, normal_user):
    task = Task.objects.create(title='Sample Task', status='created', creator=normal_user)
    client.force_authenticate(user=normal_user)
    response = client.patch(f'/api/tasks/{task.id}/', {'status': 'in_progress'})
    assert response.status_code == status.HTTP_403_FORBIDDEN
