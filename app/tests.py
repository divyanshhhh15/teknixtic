from django.test import TestCase
from unittest.mock import patch

from app.models import ChatSession


class ChatbotApiTests(TestCase):
    def test_chatbot_returns_ai_response(self):
        class FakeResponse:
            class Choice:
                class Message:
                    content = "Test answer"

                message = Message()

            choices = [Choice()]

        class FakeClient:
            def __init__(self):
                self.chat = type(
                    'Chat',
                    (),
                    {
                        'completions': type(
                            'Completions',
                            (),
                            {'create': lambda self, **kwargs: FakeResponse()}
                        )()
                    }
                )()

        with patch('app.views.client', FakeClient()):
            response = self.client.post(
                '/chatbot/',
                {'message': 'hello'},
                content_type='application/json'
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Test answer', response.json()['response'])


class HomeHistoryTests(TestCase):
    def test_home_page_shows_only_recent_sessions(self):
        for index in range(6):
            ChatSession.objects.create(title=f'Chat {index}')

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['sessions']), 5)
