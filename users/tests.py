from django.test import TestCase
from .models import MyUser

# Create your tests here.


class MyUserModelTest(TestCase):
    def test_user_str(self):
        user = MyUser.objects.create_user(
            username="xroyalptx",
            first_name="Владислав",
            last_name="Архинчеев",
            email="vladik@ya.ru",
            password="clown"
        )
        checkItem = str(user)
        self.assertEqual(checkItem, "Логин: xroyalptx\nРоль: Студент\nИмя: Владислав\nФамилия: Архинчеев\nЭлектронная почта: vladik@ya.ru")


class RegisterViewTest(TestCase):
    def test_register_view_create_correct_user(self):
        response = self.client.post(path='/register/', data={
            'username': 'xroyalptx',
            'first_name': 'влАдислав',
            'last_name': 'архинЧЕев',
            'email': 'vladik@ya.ru',
            'password1': 'clown1000',
            'password2': 'clown1000',
        })

        self.assertEqual(response.status_code, 302) #проверка Reidrect
        self.assertEqual(MyUser.objects.count(), 1)

        new_user = MyUser.objects.first()
        self.assertEqual(new_user.username, 'xroyalptx')
        self.assertEqual(new_user.first_name, 'Владислав')
        self.assertEqual(new_user.last_name, 'Архинчеев')
        self.assertEqual(new_user.email, 'vladik@ya.ru')


    def test_register_view_get_request(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)


    def test_register_view_authenticated_user(self):
        test_user = MyUser.objects.create_user(
            username='xroyalptx', 
            password='clown1000'
        )
        self.client.force_login(user=test_user)
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 302)


class LoginViewTest(TestCase):
    def test_login_view_authenticated_user(self):
        test_user = MyUser.objects.create_user(
            username='xroyalptx',
            password='clown1000',
        )
        self.client.force_login(user=test_user)
        response = self.client.get('/login/')

        self.assertEqual(response.status_code, 302)

    def test_login_view_correct_user(self):
        test_user = MyUser.objects.create_user(
            username = 'xroyalptx',
            password = 'clown1000',
        )

        response = self.client.post('/login/', data={
            'username': 'xroyalptx',
            'password': 'clown1000',
        })

        self.assertEqual(response.status_code, 302)

    def test_login_view_incorrect_user(self):
        test_user = MyUser.objects.create_user(
            username = 'xroyalptx',
            password = 'clown1000',
        )

        response = self.client.post('/login/', data={
            'username': 'xroyalptx',
            'password': 'clown1111',
        })

        self.assertEqual(response.status_code, 200)

    def test_login_view_get_request(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(TestCase):
    def test_logout(self):
        test_user = MyUser.objects.create_user(
            username = 'xroyalptx',
            password = 'clown1000',
        )

        self.client.force_login(user=test_user)
        response = self.client.get('/logout/')

        self.assertEqual(response.status_code, 302)


class DeleteUserViewTest(TestCase):
    def test_delete_user_get_request(self):
        test_user = MyUser.objects.create_user(
            username = 'xroyalptx',
            password = 'clown1000',
        )

        self.client.force_login(user=test_user)
        is_created = MyUser.objects.count()

        self.assertEqual(is_created, 1)

        response = self.client.get('/delete_user/')
        self.assertEqual(response.status_code, 302)

    def test_delete_user_post_request(self):
        test_user = MyUser.objects.create_user(
            username = 'xroyalptx',
            password = 'clown1000',
        )

        self.client.force_login(user=test_user)
        is_created = MyUser.objects.count()
        self.assertEqual(is_created, 1)

        response = self.client.post('/delete_user/')
        self.assertEqual(response.status_code, 302)

        is_deleted = MyUser.objects.count()
        self.assertEqual(is_deleted, 0)

        self.assertFalse('_auth_user_id' in self.client.session)


class ProfileViewTest(TestCase):
    def test_profile_view_not_authenticated_user(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)

    def test_profile_view_authenticated_user(self):
        test_user = MyUser.objects.create_user(
            username = 'xroyalptx',
            password = 'clown1000',
        )
        self.client.force_login(user=test_user)

        response = self.client.get('/profile/')
        self.assertTemplateUsed(response, 'users/profile.html')

        self.assertIn('random_buryad_word', response.context)


class UpdateUserViewTest(TestCase):
    def test_update_user_view_get_request(self):
        test_user = MyUser.objects.create(
            username = 'xroyalptx',
            password = 'clown1000',
        )
        self.client.force_login(user=test_user)

        response = self.client.get('/update_user/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/update_user.html')

    def test_update_user_view_post_request_changed_data(self):
        test_user = MyUser.objects.create(
            username = 'xroyalptx',
            first_name = 'Владислав',
            last_name = 'Архинчеев',
            email = 'vladik@ya.ru',
            password = 'clown1000',
        )
        self.client.force_login(user=test_user)

        response = self.client.post('/update_user/', data={
            'username': 'royal',
            'first_name': 'Владислав',
            'last_name': 'Архинчеев',
            'email': 'vlad@ya.ru',
        })
        test_user.refresh_from_db()
        
        self.assertEqual(test_user.username, 'royal')
        self.assertEqual(test_user.email, 'vlad@ya.ru')
        self.assertEqual(response.status_code, 302)

    def test_update_user_view_post_request_not_changed_data(self):
        test_user = MyUser.objects.create(
            username = 'xroyalptx',
            first_name = 'Владислав',
            last_name = 'Архинчеев',
            email = 'vladik@ya.ru',
            password = 'clown1000',
        )
        self.client.force_login(user=test_user)

        response = self.client.post('/update_user/', data={
            'username': 'xroyalptx',
            'first_name': 'Владислав',
            'last_name': 'Архинчеев',
            'email': 'vladik@ya.ru',
        })

        self.assertEqual(response.status_code, 200)
        print(f"Контекст у response: {response.content}")
        form = response.context['form']
        self.assertIn('Вы не ввели никаких изменений.', form.non_field_errors())


class UpdatePasswordViewTest(TestCase):
    def test_update_password_view_get_request(self):
        test_user = MyUser.objects.create_user(
            username = 'xroyalptx',
            password = 'clown1000',
        )

        self.client.force_login(user=test_user)
        response = self.client.get('/update_password/')

        self.assertIs(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/update_password.html')

    def test_update_password_view_post_request(self):
        test_user = MyUser.objects.create_user(
            username = 'xroyalptx',
            password = 'clown1000',
        )

        self.client.force_login(user=test_user)
        response = self.client.post('/update_password/', data={
            'old_password': 'clown1000',
            'new_password1': 'clown1001',
            'new_password2': 'clown1001',
        })

        test_user.refresh_from_db()
        self.assertTrue('_auth_user_id' in self.client.session)
        self.assertTrue(test_user.check_password('clown1001'))
        self.assertEqual(response.status_code, 302)