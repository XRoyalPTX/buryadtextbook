from django.test import TestCase

# Create your tests here.


class HomeViewTest(TestCase):
    def test_home_view_statud_code(self):
        response = self.client.get('/')
        checkStatus = str(response.status_code)
        self.assertEqual(checkStatus, '200')

    def test_home_view_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home/homepage.html')


class UnderConstructionTest(TestCase):
    def test_under_construction_previous_url(self):
        response = self.client.get('/under_construction/', HTTP_REFERER='/about/')
        a = str(response.status_code)
        checkUrl = response.context['previous_url']
        self.assertEqual(checkUrl, '/about/')


class about_view_test(TestCase):
    def test_about_view_template(self):
        response = self.client.get('/about/')
        self.assertTemplateUsed(response, 'home/about.html')