from django.test import TestCase
from .models import CarryService, CarryServicePotentialBuyer
from django.contrib.auth.models import User
from accounts.models import Profile
from django.urls import reverse

# You must run collectstatic before running the tests

def create_carry_service(seller, buyer=None, seller_trade_outcome=None, buyer_trade_outcome=None):
    """
    Create a carry service with the given seller and buyer.
    """
    return CarryService.objects.create(seller=seller, buyer=buyer, price=1, currency="test", seller_trade_outcome=seller_trade_outcome, buyer_trade_outcome=buyer_trade_outcome)

def create_user(username, email, password):
    """
    Create a user with given username, email and password.
    """
    return User.objects.create(username=username, email=email, password=password)

def create_carry_service_potential_buyer(carry_service, user):
    """
    Create a potential buyer with given carry service and user.
    """
    return CarryServicePotentialBuyer.objects.create(carry_service=carry_service, buyer=user)

def log_in_with_user(self):
    self.client.force_login(create_user('test_user', 'test_user@example.com', 'password'))

class CarryServiceCreateViewTests(TestCase):
    def test_create(self):
        """
        User should be able to create a carry service.
        """
        log_in_with_user(self)
        response = self.client.post(reverse('carry_services:carry-service-create'), data={'price': 100, 'currency': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.count(), 1)

    def test_create_limit(self):
        """
        User should be able to only have 5 carry services open at the same time.
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        for _ in range(0,5):
            create_carry_service(test_user)
        response = self.client.post(reverse('carry_services:carry-service-create'), data={'price': 100, 'currency': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You may not have more than')

class CarryServiceListViewTests(TestCase):
    def setUp(self):
        log_in_with_user(self)
        return super().setUp()

    def test_list_carry_services(self):
        """
        All the carry services are shown on the list view.
        """
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        carry_service1 = create_carry_service(user1)
        carry_service2 = create_carry_service(user2)
        response = self.client.get(reverse('carry_services:carry-service-list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            [carry_service2, carry_service1],
            ordered=False
        )

    def test_search_by_seller(self):
        """
        Searching by seller for user 1 should only show user 1's carry services on the list view.
        """
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        carry_service1 = create_carry_service(user1)
        carry_service2 = create_carry_service(user1)
        create_carry_service(user2)
        response = self.client.get(reverse('carry_services:carry-service-list') + "?searchby=seller&search=" + user1.username)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            [carry_service2, carry_service1],
            ordered=False
        )

    def test_search_by_buyer(self):
        """
        Searching by buyer for user 1 should only show carry services where user 1 is buyer on the list view.
        """
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        carry_service1 = create_carry_service(user2, user1)
        carry_service2 = create_carry_service(user2, user1)
        create_carry_service(user2, user3)
        create_carry_service(user3)
        response = self.client.get(reverse('carry_services:carry-service-list') + "?searchby=buyer&search=" + user1.username)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['object_list'],
            [carry_service2, carry_service1],
            ordered=False
        )

class CarryServiceDetailViewTests(TestCase):

    def test_carry_service_detail_view_should_show_seller_potential_buyers(self):
        """
        CarryService detail view should show seller and potential buyers
        """
        log_in_with_user(self)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        carry_service = create_carry_service(user1)
        create_carry_service_potential_buyer(carry_service, user2)
        create_carry_service_potential_buyer(carry_service, user3)
        response = self.client.get(reverse('carry_services:carry-service-detail', kwargs={'pk': carry_service.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            map(lambda x: x.buyer, response.context['object'].potential_buyers),
            [user2, user3],
            ordered=False
        )
        self.assertEqual(
            response.context['object'].seller,
            user1
        )
        self.assertEqual(
            response.context['object'].buyer,
            None
        )

class CarryServiceSelectBuyerViewTests(TestCase):

    def test_select_buyer_view(self):
        """
        Seller should be able to open the view
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        carry_service = create_carry_service(test_user)
        user = create_user('test1', 'test1@example.com', 'password')
        create_carry_service_potential_buyer(carry_service, user)
        response = self.client.get(reverse('carry_services:carry-service-select-buyer', kwargs={'pk': carry_service.pk}))
        self.assertEqual(response.status_code, 200)

    def test_seller_should_be_able_to_select_potential_buyer(self):
        """
        Seller should be able to select a potential buyer
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        carry_service = create_carry_service(test_user)
        user = create_user('test1', 'test1@example.com', 'password')
        create_carry_service_potential_buyer(carry_service, user)
        response = self.client.post(reverse('carry_services:carry-service-select-buyer', kwargs={'pk': carry_service.pk}), data={'buyer': user.username})
        self.assertEqual(response.status_code, 302)
        carry_service = CarryService.objects.get(pk=carry_service.pk)
        self.assertEqual(carry_service.buyer, user)

    def test_seller_should_not_be_able_to_select_user_who_is_not_potential_buyer(self):
        """
        Seller should not be able to select a user who is not potential buyer
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        carry_service = create_carry_service(test_user)
        user = create_user('test1', 'test1@example.com', 'password')
        response = self.client.post(reverse('carry_services:carry-service-select-buyer', kwargs={'pk': carry_service.pk}), data={'buyer': user.username})
        self.assertEqual(response.status_code, 200)
        carry_service = CarryService.objects.get(pk=carry_service.pk)
        self.assertEqual(carry_service.buyer, None)

    def test_seller_cannot_change_buyer_after_it_has_been_set(self):
        """
        Seller should not be able to change the buyer
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        carry_service = create_carry_service(test_user, user1)
        create_carry_service_potential_buyer(carry_service, user2)
        response = self.client.post(reverse('carry_services:carry-service-select-buyer', kwargs={'pk': carry_service.pk}), data={'buyer': user2.username})
        self.assertEqual(response.status_code, 403)
        carry_service = CarryService.objects.get(pk=carry_service.pk)
        self.assertEqual(carry_service.buyer, user1)

    def test_other_users_cannot_select_buyer(self):
        """
        Other users cannot select buyer
        """
        log_in_with_user(self)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        carry_service = create_carry_service(user1)
        create_carry_service_potential_buyer(carry_service, user2)
        response = self.client.post(reverse('carry_services:carry-service-select-buyer', kwargs={'pk': carry_service.pk}), data={'buyer': user2.username})
        self.assertEqual(response.status_code, 403)
        carry_service = CarryService.objects.get(pk=carry_service.pk)
        self.assertEqual(carry_service.buyer, None)

class CarryServiceDeleteViewTests(TestCase):

    def test_seller_should_be_able_to_open_delete_view(self):
        """
        Seller should be able to open the delete view
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        carry_service = create_carry_service(test_user)
        response = self.client.get(reverse('carry_services:carry-service-delete', kwargs={'pk': carry_service.pk}))
        self.assertEqual(response.status_code, 200)

    def test_seller_should_be_able_to_delete_open_carry_service(self):
        """
        Seller should be able to delete their carry service
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        carry_service = create_carry_service(test_user)
        response = self.client.post(reverse('carry_services:carry-service-delete', kwargs={'pk': carry_service.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(carry_service.pk, CarryService.objects.all().values('pk'))

    def test_seller_should_not_be_able_to_delete_closed_carry_service(self):
        """
        Seller should not be able to delete their carry service when buyer is selected
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user = create_user('test1', 'test1@example.com', 'password')
        carry_service = create_carry_service(test_user, user)
        response = self.client.post(reverse('carry_services:carry-service-delete', kwargs={'pk': carry_service.pk}))
        self.assertEqual(response.status_code, 403)
        carry_service = CarryService.objects.get(pk=carry_service.pk)
        self.assertIn(carry_service, CarryService.objects.all())

    def test_no_one_else_should_be_able_to_delete_open_carry_service(self):
        """
        No one else should be able to delete their carry service
        """
        log_in_with_user(self)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        carry_service = create_carry_service(user1)
        create_carry_service_potential_buyer(carry_service, user2)
        response = self.client.post(reverse('carry_services:carry-service-delete', kwargs={'pk': carry_service.pk}))
        self.assertEqual(response.status_code, 403)
        carry_service = CarryService.objects.get(pk=carry_service.pk)
        self.assertIn(carry_service, CarryService.objects.all())

class AddCarryServicePotentialBuyerViewTests(TestCase):

    def test_add_potential_buyer(self):
        """
        Add potential buyer view should add user to carry service's potential buyers
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        carry_service = create_carry_service(user1)
        create_carry_service_potential_buyer(carry_service, user2)
        create_carry_service_potential_buyer(carry_service, user3)
        self.client.post(reverse('carry_services:carry-service-add-potential-buyer', kwargs={'pk': carry_service.pk}))
        response = self.client.get(reverse('carry_services:carry-service-detail', kwargs={'pk': carry_service.pk}))
        self.assertQuerysetEqual(
            map(lambda x: x.buyer, response.context['object'].potential_buyers),
            [test_user, user2, user3],
            ordered=False
        )

    def test_seller_cannot_be_potential_buyer(self):
        """
        CarryService's seller cannot be potential buyer
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        carry_service = create_carry_service(test_user)
        post_response = self.client.post(reverse('carry_services:carry-service-add-potential-buyer', kwargs={'pk': carry_service.pk}))
        self.assertEqual(post_response.status_code, 403)
        response = self.client.get(reverse('carry_services:carry-service-detail', kwargs={'pk': carry_service.pk}))
        self.assertQuerysetEqual(
            map(lambda x: x.buyer, response.context['object'].potential_buyers),
            [],
            ordered=False
        )

    def test_cannot_add_potential_buyer_when_carry_service_is_closed(self):
        """
        Cannot add potential buyer if carry service is closed
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        carry_service = create_carry_service(user1, user2)
        create_carry_service_potential_buyer(carry_service, user2)
        create_carry_service_potential_buyer(carry_service, user3)
        response = self.client.post(reverse('carry_services:carry-service-add-potential-buyer', kwargs={'pk': carry_service.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertQuerysetEqual(
            map(lambda x: x.buyer, CarryService.objects.get(pk=carry_service.pk).potential_buyers),
            [user2, user3],
            ordered=False
        )

class RemoveCarryServicePotentialBuyerViewTests(TestCase):

    def test_remove_potential_buyer(self):
        """
        Remove potential buyer view should remove user from carry service's potential buyers
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        carry_service = create_carry_service(user1)
        create_carry_service_potential_buyer(carry_service, user2)
        create_carry_service_potential_buyer(carry_service, user3)
        create_carry_service_potential_buyer(carry_service, test_user)
        self.client.post(reverse('carry_services:carry-service-remove-potential-buyer', kwargs={'pk': carry_service.pk}))
        response = self.client.get(reverse('carry_services:carry-service-detail', kwargs={'pk': carry_service.pk}))
        self.assertQuerysetEqual(
            map(lambda x: x.buyer, response.context['object'].potential_buyers),
            [user2, user3],
            ordered=False
        )

    def test_cannot_add_potential_buyer_when_carry_service_is_closed(self):
        """
        Cannot remove potential buyer if carry service is closed
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        carry_service = create_carry_service(user1, user2)
        create_carry_service_potential_buyer(carry_service, user2)
        create_carry_service_potential_buyer(carry_service, user3)
        create_carry_service_potential_buyer(carry_service, test_user)
        response = self.client.post(reverse('carry_services:carry-service-remove-potential-buyer', kwargs={'pk': carry_service.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertQuerysetEqual(
            map(lambda x: x.buyer, CarryService.objects.get(pk=carry_service.pk).potential_buyers),
            [test_user, user2, user3],
            ordered=False
        )

class CarryServiceSellerTradeOutcomeViewTests(TestCase):

    def test_seller_should_be_able_to_open_seller_trade_outcome_view(self):
        """
        Seller should be able to open seller trade outcome view
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        carry_service = create_carry_service(test_user, user1)
        response = self.client.get(reverse('carry_services:carry-service-seller-outcome', kwargs={'pk': carry_service.pk}))
        self.assertEqual(response.status_code, 200)

    def test_positive_trade_outcome(self):
        """
        Positive trade outcome should set seller outcome true
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        carry_service = create_carry_service(test_user, user1)
        response = self.client.post(reverse('carry_services:carry-service-seller-outcome', kwargs={'pk': carry_service.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.get(pk=carry_service.pk).seller_trade_outcome, True)

    def test_negative_trade_outcome(self):
        """
        Negative trade outcome should set seller outcome false
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        carry_service = create_carry_service(test_user, user1)
        response = self.client.post(reverse('carry_services:carry-service-seller-outcome', kwargs={'pk': carry_service.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.get(pk=carry_service.pk).seller_trade_outcome, False)

    def test_seller_trade_cannot_be_closed_by_someone_else(self):
        """
        Seller side of the trade cannot be closed by someone else
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        carry_service = create_carry_service(user1, test_user)
        response = self.client.post(reverse('carry_services:carry-service-seller-outcome', kwargs={'pk': carry_service.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(CarryService.objects.get(pk=carry_service.pk).seller_trade_outcome, None)

    def test_seller_cannot_close_their_side_of_the_trade_twice(self):
        """
        Seller cannot close their side of the trade twice
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        carry_service = create_carry_service(test_user, user1, seller_trade_outcome=True)
        response = self.client.post(reverse('carry_services:carry-service-seller-outcome', kwargs={'pk': carry_service.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(CarryService.objects.get(pk=carry_service.pk).seller_trade_outcome, True)

    def test_open_carry_service_cannot_be_closed(self):
        """
        Open carry service cannot be closed by seller
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        carry_service = create_carry_service(test_user)
        response = self.client.post(reverse('carry_services:carry-service-seller-outcome', kwargs={'pk': carry_service.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(CarryService.objects.filter(pk=carry_service.pk).count(), 1)

    def test_carry_service_outcome_closed_by_buyer(self):
        """
        Carry service that is already closed by buyer when closed by seller should change the reputations and delete the carry service
        """
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        user4 = create_user('test4', 'test4@example.com', 'password')
        user5 = create_user('user5', 'user5@example.com', 'password')
        user6 = create_user('user6', 'user6@example.com', 'password')
        user7 = create_user('user7', 'user7@example.com', 'password')
        user8 = create_user('user8', 'user8@example.com', 'password')
        carry_service1 = create_carry_service(user1, user2, buyer_trade_outcome=True)
        carry_service2 = create_carry_service(user3, user4, buyer_trade_outcome=True)
        carry_service3 = create_carry_service(user5, user6, buyer_trade_outcome=False)
        carry_service4 = create_carry_service(user7, user8, buyer_trade_outcome=False)

        self.client.force_login(user1)
        response = self.client.post(reverse('carry_services:carry-service-seller-outcome', kwargs={'pk': carry_service1.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.filter(pk=carry_service1.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user1).reputation, 1)
        self.assertEqual(Profile.objects.get(user=user2).reputation, 1)

        self.client.force_login(user3)
        response = self.client.post(reverse('carry_services:carry-service-seller-outcome', kwargs={'pk': carry_service2.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.filter(pk=carry_service2.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user3).reputation, 1)
        self.assertEqual(Profile.objects.get(user=user4).reputation, -1)

        self.client.force_login(user5)
        response = self.client.post(reverse('carry_services:carry-service-seller-outcome', kwargs={'pk': carry_service3.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.filter(pk=carry_service3.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user5).reputation, -1)
        self.assertEqual(Profile.objects.get(user=user6).reputation, 1)

        self.client.force_login(user7)
        response = self.client.post(reverse('carry_services:carry-service-seller-outcome', kwargs={'pk': carry_service4.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.filter(pk=carry_service4.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user7).reputation, -1)
        self.assertEqual(Profile.objects.get(user=user8).reputation, -1)

class CarryServiceBuyerTradeOutcomeViewTests(TestCase):

    def test_buyer_should_be_able_to_open_buyer_trade_outcome_view(self):
        """
        Buyer should be able to open buyer trade outcome view
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        carry_service = create_carry_service(user1, test_user)
        response = self.client.get(reverse('carry_services:carry-service-buyer-outcome', kwargs={'pk': carry_service.pk}))
        self.assertEqual(response.status_code, 200)

    def test_positive_trade_outcome(self):
        """
        Positive trade outcome should set buyer outcome true
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')

        carry_service = create_carry_service(user1, test_user)
        response = self.client.post(reverse('carry_services:carry-service-buyer-outcome', kwargs={'pk': carry_service.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.get(pk=carry_service.pk).buyer_trade_outcome, True)

    def test_negative_trade_outcome(self):
        """
        Negative trade outcome should set buyer outcome false
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        carry_service = create_carry_service(user1, test_user)
        response = self.client.post(reverse('carry_services:carry-service-buyer-outcome', kwargs={'pk': carry_service.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.get(pk=carry_service.pk).buyer_trade_outcome, False)

    def test_buyer_cannot_close_their_side_of_the_trade_twice(self):
        """
        Buyer cannot close their side of the trade twice
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        carry_service = create_carry_service(user1, test_user, buyer_trade_outcome=True)
        response = self.client.post(reverse('carry_services:carry-service-buyer-outcome', kwargs={'pk': carry_service.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(CarryService.objects.get(pk=carry_service.pk).buyer_trade_outcome, True)

    def test_buyer_trade_cannot_be_closed_by_someone_else(self):
        """
        Buyer side of the trade cannot be closed by someone else
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        carry_service = create_carry_service(test_user, user1)
        response = self.client.post(reverse('carry_services:carry-service-buyer-outcome', kwargs={'pk': carry_service.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(CarryService.objects.get(pk=carry_service.pk).buyer_trade_outcome, None)

    def test_carry_service_outcome_closed_by_seller(self):
        """
        Carry service that is already closed by seller when closed by buyer should change the reputations and delete the carry service
        """
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        user4 = create_user('test4', 'test4@example.com', 'password')
        user5 = create_user('user5', 'user5@example.com', 'password')
        user6 = create_user('user6', 'user6@example.com', 'password')
        user7 = create_user('user7', 'user7@example.com', 'password')
        user8 = create_user('user8', 'user8@example.com', 'password')
        carry_service1 = create_carry_service(user1, user2, seller_trade_outcome=True)
        carry_service2 = create_carry_service(user3, user4, seller_trade_outcome=True)
        carry_service3 = create_carry_service(user5, user6, seller_trade_outcome=False)
        carry_service4 = create_carry_service(user7, user8, seller_trade_outcome=False)

        self.client.force_login(user2)
        response = self.client.post(reverse('carry_services:carry-service-buyer-outcome', kwargs={'pk': carry_service1.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.filter(pk=carry_service1.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user1).reputation, 1)
        self.assertEqual(Profile.objects.get(user=user2).reputation, 1)

        self.client.force_login(user4)
        response = self.client.post(reverse('carry_services:carry-service-buyer-outcome', kwargs={'pk': carry_service2.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.filter(pk=carry_service2.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user3).reputation, -1)
        self.assertEqual(Profile.objects.get(user=user4).reputation, 1)

        self.client.force_login(user6)
        response = self.client.post(reverse('carry_services:carry-service-buyer-outcome', kwargs={'pk': carry_service3.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.filter(pk=carry_service3.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user5).reputation, 1)
        self.assertEqual(Profile.objects.get(user=user6).reputation, -1)

        self.client.force_login(user8)
        response = self.client.post(reverse('carry_services:carry-service-buyer-outcome', kwargs={'pk': carry_service4.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarryService.objects.filter(pk=carry_service4.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user7).reputation, -1)
        self.assertEqual(Profile.objects.get(user=user8).reputation, -1)