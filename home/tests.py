from django.test import TestCase

# Create your tests here.


class HomeViewTest(TestCase):
    def test_home_view_statud_code(self):
        response = self.client.get('/')
        checkStatus = str(response.status_code)
        self.assertEqual(checkStatus, '200')
        pass

    def test_home_view_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home/homepage.html')


class UnderConstructionTest(TestCase):
    def test_under_construction_previous_url(self):
        response = self.client.get('/under_construction/', HTTP_REFERER='/about/')
        a = str(response.status_code)
        print(f"Ответ сервера: {a}")
        checkUrl = response.context['previous_url']
        self.assertEqual(checkUrl, '/about/')
        pass
