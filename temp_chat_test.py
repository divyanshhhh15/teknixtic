import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django

django.setup()
from django.test import Client
from unittest.mock import patch


class FakeResp:
    choices = [type('Msg', (), {'message': type('Content', (), {'content': 'Test answer'})()})]


class FakeClient:
    def __init__(self):
        self.chat = type('Chat', (), {
            'completions': type('Completions', (), {
                'create': lambda self, **kwargs: FakeResp()
            })()
        })()


with patch('app.views.client', FakeClient()):
    r = Client().post('/chatbot/', data='{"message": "hello"}', content_type='application/json')
    print('STATUS', r.status_code)
    print('BODY', r.json())
