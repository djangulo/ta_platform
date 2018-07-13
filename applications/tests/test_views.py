from django.test import TestCase


class ApplicationViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='alice',
                                             email='alice@wonderland.com')


    