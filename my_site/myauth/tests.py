from django.test import TestCase
from django.urls import reverse


class GetCookieViewTestCase(TestCase):
    def test_get_cookie_view(self):
        response = self.client.get(reverse('myauth:get_cookie'))
        self.assertContains(response, "Cookie value")


class JsonViewTestCase(TestCase):
    def test_json_view(self):
        response = self.client.get(reverse('myauth:json_view'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        expected_data = {"test": "test", "test2": "test2"}
        self.assertJSONEqual(response.content, expected_data)
