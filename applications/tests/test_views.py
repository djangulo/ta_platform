from django.http import HttpRequest
from django.urls import resolve
from django.test import TestCase

from recruitment.views import home

class HomePageViewTests(TestCase):

    def test_root_url_resolves_to_home_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_home_page_returns_correct_markup(self):
        request = HttpRequest()
        res = home(request)
        html = res.content.decode('utf8')
        self.assertIn('<title>Company Name | Home</title>', html)


class ApplicationViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='alice',
                                             email='alice@wonderland.com')


    