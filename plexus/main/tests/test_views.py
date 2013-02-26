from django.test import TestCase
from django.test.client import Client


class SimpleTest(TestCase):
    def setUp(self):
        self.c = Client()

    def tearDown(self):
        pass

    def test_root(self):
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)

    def test_smoketest(self):
        """ just run the smoketests. we don't care if they pass/fail """
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)

    def test_add_server_form(self):
        response = self.c.get("/add_server/")
        self.assertEquals(response.status_code, 200)

    def test_add_application_form(self):
        response = self.c.get("/add_application/")
        self.assertEquals(response.status_code, 200)
