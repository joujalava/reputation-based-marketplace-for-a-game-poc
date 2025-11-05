from django.test import TestCase
from .models import Classification
from crafts.models import Craft
from django.contrib.auth.models import User
from django.urls import reverse

def create_classification(name, parent=None):
    """
    Create a classification with name.
    """
    return Classification.objects.create(name=name, parent=parent)

def create_craft(classification, seller, buyer=None):
    """
    Create a craft with the given classification, seller and buyer.
    """
    return Craft.objects.create(classification=classification, seller=seller, buyer=buyer, amount=1, price=1, currency="test")

def create_user(username, email, password):
    """
    Create a user with given username, email and password.
    """
    return User.objects.create(username=username, email=email, password=password)

def log_in_with_user(self):
    self.client.force_login(create_user('test_user', 'test_user@example.com', 'password'))

class ClassificationListViewTests(TestCase):

    def setUp(self):
        log_in_with_user(self)
        return super().setUp()

    def test_show_classifications(self):
        """
        All root classifications are shown on the list view.
        """
        classification1 = create_classification('test1')
        classification2 = create_classification('test2')
        create_classification('test3', classification1)
        response = self.client.get(reverse('classifications:classification-list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            [classification2, classification1],
            ordered=False
        )

class ClassificationDetailViewTests(TestCase):

    def setUp(self):
        log_in_with_user(self)
        return super().setUp()

    def test_show_child_classifications_and_crafts(self):
        """
        All the crafts are shown on the list view.
        """
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        classification1 = create_classification('test1')
        classification2 = create_classification('test2', classification1)
        classification3 = create_classification('test3', classification1)
        craft1 = create_craft(classification1, user1)
        craft2 = create_craft(classification1, user2)
        response = self.client.get(reverse('classifications:classification-detail', args=[classification1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['classification_list'],
            [classification3, classification2],
            ordered=False
        )
        self.assertQuerysetEqual(
            response.context['craft_list'],
            [craft2, craft1],
            ordered=False
        )

    def test_search_by_seller(self):
        """
        Searching by seller for user 1 should only show user 1's crafts on the craft list.
        """
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        classification1 = create_classification('test1')
        classification2 = create_classification('test2', classification1)
        craft1 = create_craft(classification1, user1)
        craft2 = create_craft(classification1, user1)
        create_craft(classification1, user2)
        response = self.client.get(reverse('classifications:classification-detail', args=[classification1.pk]) + "?searchby=seller&search=" + user1.username)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['classification_list'],
            [classification2],
            ordered=False
        )
        self.assertQuerysetEqual(
            response.context['craft_list'],
            [craft2, craft1],
            ordered=False
        )

    def test_search_by_buyer(self):
        """
        Searching by buyer for user 1 should only show crafts where user 1 is buyer on the crafts list.
        """
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        classification1 = create_classification('test1')
        classification2 = create_classification('test2', classification1)
        craft1 = create_craft(classification1, user2, user1)
        craft2 = create_craft(classification1, user2, user1)
        create_craft(classification1, user2, user3)
        create_craft(classification1, user3)
        response = self.client.get(reverse('classifications:classification-detail', args=[classification1.pk]) + "?searchby=buyer&search=" + user1.username)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['classification_list'],
            [classification2],
            ordered=False
        )
        self.assertQuerysetEqual(
            response.context['craft_list'],
            [craft2, craft1],
            ordered=False
        )