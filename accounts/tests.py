from accounts.models import Profile
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

# You must run collectstatic before running the tests

def create_user(username, email, password):
    """
    Create a user with given username, email and password.
    """
    return User.objects.create(username=username, email=email, password=password)

def log_in_with_user(self):
    self.client.force_login(create_user('test_user', 'test_user@example.com', 'password'))

class UserUpdateViewTests(TestCase):

    def test_user_should_see_the_view(self):
        """
        Logged in user should be able to see the view
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        response = self.client.get(reverse('accounts:user-update'))
        self.assertEqual(response.status_code, 200)

    def test_user_should_be_able_to_change_usename_and_email(self):
        """
        User should be able to change username and email
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        new_name = "new_test_user"
        new_email = "new_email@example.com"
        response = self.client.post(reverse('accounts:user-update'), data={'username': new_name, 'email': new_email})
        self.assertEqual(response.status_code, 302)
        test_user = User.objects.get(pk=test_user.pk)
        self.assertEqual(test_user.username, new_name)
        self.assertEqual(test_user.email, new_email)

class ProfileDetailViewTests(TestCase):

    def setUp(self):
        log_in_with_user(self)
        return super().setUp()

    def test_user_should_see_the_view(self):
        """
        User should be able to see the view
        """
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)

class RegistrationViewTests(TestCase):

    def test_anyone_should_be_able_to_see_the_view(self):
        """
        Anyone should be able to see the view
        """
        response = self.client.get(reverse('accounts:registration'))
        self.assertEqual(response.status_code, 200)

class CustomLogOutViewTests(TestCase):

    def test_anyone_should_be_able_to_see_the_view(self):
        """
        Anyone should be able to see the view
        """
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 200)

class CustomLogInViewTests(TestCase):

    def test_anyone_should_be_able_to_see_the_view(self):
        """
        Anyone should be able to see the view
        """
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

class CustomPasswordChangeViewTests(TestCase):
    def setUp(self):
        log_in_with_user(self)
        return super().setUp()

    def test_user_should_see_the_view(self):
        """
        User should be able to see the view
        """
        response = self.client.get(reverse('accounts:password-change'))
        self.assertEqual(response.status_code, 200)

class CustomPasswordChangeDoneViewTests(TestCase):
    def setUp(self):
        log_in_with_user(self)
        return super().setUp()

    def test_user_should_see_the_view(self):
        """
        User should be able to see the view
        """
        response = self.client.get(reverse('accounts:password-change-done'))
        self.assertEqual(response.status_code, 200)

class ProfileUpdateViewTests(TestCase):

    def test_user_should_see_the_view(self):
        """
        User should be able to see the view
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        response = self.client.get(reverse('accounts:character-name-change'))
        self.assertEqual(response.status_code, 200)

    def test_user_should_be_able_to_change_character_name(self):
        """
        User should be able to change character name
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        new_name = "new name"
        response = self.client.post(reverse('accounts:character-name-change'), data={'character_name': new_name})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Profile.objects.get(user=test_user).character_name, new_name)