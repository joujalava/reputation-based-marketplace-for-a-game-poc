from django.test import TestCase
from .models import Classification, Craft, CraftPotentialBuyer
from django.contrib.auth.models import User
from accounts.models import Profile
from django.urls import reverse

# You must run collectstatic before running the tests

def create_classification(name):
    """
    Create a classification with name.
    """
    return Classification.objects.create(name=name, has_crafts=True)

def create_craft(classification, seller, buyer=None, seller_trade_outcome=None, buyer_trade_outcome=None):
    """
    Create a craft with the given classification, seller and buyer.
    """
    return Craft.objects.create(classification=classification, seller=seller, buyer=buyer, amount=1, price=1, currency="test", seller_trade_outcome=seller_trade_outcome, buyer_trade_outcome=buyer_trade_outcome)

def create_user(username, email, password):
    """
    Create a user with given username, email and password.
    """
    return User.objects.create(username=username, email=email, password=password)

def create_craft_potetial_buyer(craft, user):
    """
    Create a potential buyer with given craft and user.
    """
    return CraftPotentialBuyer.objects.create(craft=craft, buyer=user)

def log_in_with_user(self):
    self.client.force_login(create_user('test_user', 'test_user@example.com', 'password'))

class CraftCreateViewTests(TestCase):
    def test_create(self):
        """
        User should be able to create a craft.
        """
        log_in_with_user(self)
        classification = create_classification('test')
        response = self.client.post(reverse('crafts:craft-create'), data={'classification': classification.pk, 'amount': 1, 'price': 100, 'currency': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.count(), 1)

    def test_create_limit(self):
        """
        User should be able to only have 5 crafts open at the same time.
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        classification = create_classification('test')
        for _ in range(0,5):
            create_craft(classification, test_user)
        response = self.client.post(reverse('crafts:craft-create'), data={'classification': classification.pk, 'amount': 1, 'price': 100, 'currency': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You may not have more than')

class CraftDetailViewTests(TestCase):

    def test_craft_detail_view_should_show_seller_potential_buyers(self):
        """
        Craft detail view should show seller and potential buyers
        """
        log_in_with_user(self)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1)
        create_craft_potetial_buyer(craft, user2)
        create_craft_potetial_buyer(craft, user3)
        response = self.client.get(reverse('crafts:craft-detail', kwargs={'pk': craft.pk}))
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

class CraftSelectBuyerViewTests(TestCase):

    def test_select_buyer_view(self):
        """
        Seller should be able to open the view
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        classification = create_classification('test1')
        craft = create_craft(classification, test_user)
        user = create_user('test1', 'test1@example.com', 'password')
        create_craft_potetial_buyer(craft, user)
        response = self.client.get(reverse('crafts:craft-select-buyer', kwargs={'pk': craft.pk}))
        self.assertEqual(response.status_code, 200)

    def test_seller_should_be_able_to_select_potential_buyer(self):
        """
        Seller should be able to select a potential buyer
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        classification = create_classification('test1')
        craft = create_craft(classification, test_user)
        user = create_user('test1', 'test1@example.com', 'password')
        create_craft_potetial_buyer(craft, user)
        response = self.client.post(reverse('crafts:craft-select-buyer', kwargs={'pk': craft.pk}), data={'buyer': user.username})
        self.assertEqual(response.status_code, 302)
        craft = Craft.objects.get(pk=craft.pk)
        self.assertEqual(craft.buyer, user)

    def test_seller_should_not_be_able_to_select_user_who_is_not_potential_buyer(self):
        """
        Seller should not be able to select a user who is not potential buyer
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        classification = create_classification('test1')
        craft = create_craft(classification, test_user)
        user = create_user('test1', 'test1@example.com', 'password')
        response = self.client.post(reverse('crafts:craft-select-buyer', kwargs={'pk': craft.pk}), data={'buyer': user.username})
        self.assertEqual(response.status_code, 200)
        craft = Craft.objects.get(pk=craft.pk)
        self.assertEqual(craft.buyer, None)

    def test_seller_cannot_change_buyer_after_it_has_been_set(self):
        """
        Seller should not be able to change the buyer
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, test_user, user1)
        create_craft_potetial_buyer(craft, user2)
        response = self.client.post(reverse('crafts:craft-select-buyer', kwargs={'pk': craft.pk}), data={'buyer': user2.username})
        self.assertEqual(response.status_code, 403)
        craft = Craft.objects.get(pk=craft.pk)
        self.assertEqual(craft.buyer, user1)

    def test_other_users_cannot_select_buyer(self):
        """
        Other users cannot select buyer
        """
        log_in_with_user(self)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1)
        create_craft_potetial_buyer(craft, user2)
        response = self.client.post(reverse('crafts:craft-select-buyer', kwargs={'pk': craft.pk}), data={'buyer': user2.username})
        self.assertEqual(response.status_code, 403)
        craft = Craft.objects.get(pk=craft.pk)
        self.assertEqual(craft.buyer, None)

class CraftDeleteViewTests(TestCase):

    def test_seller_should_be_able_to_open_delete_view(self):
        """
        Seller should be able to open the delete view
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        classification = create_classification('test1')
        craft = create_craft(classification, test_user)
        response = self.client.get(reverse('crafts:craft-delete', kwargs={'pk': craft.pk}))
        self.assertEqual(response.status_code, 200)

    def test_seller_should_be_able_to_delete_open_craft(self):
        """
        Seller should be able to delete their craft
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        classification = create_classification('test1')
        craft = create_craft(classification, test_user)
        response = self.client.post(reverse('crafts:craft-delete', kwargs={'pk': craft.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(craft.pk, Craft.objects.all().values('pk'))

    def test_seller_should_not_be_able_to_delete_closed_craft(self):
        """
        Seller should not be able to delete their craft when buyer is selected
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user = create_user('test1', 'test1@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, test_user, user)
        response = self.client.post(reverse('crafts:craft-delete', kwargs={'pk': craft.pk}))
        self.assertEqual(response.status_code, 403)
        craft = Craft.objects.get(pk=craft.pk)
        self.assertIn(craft, Craft.objects.all())

    def test_no_one_else_should_be_able_to_delete_open_craft(self):
        """
        No one else should be able to delete their craft
        """
        log_in_with_user(self)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1)
        create_craft_potetial_buyer(craft, user2)
        response = self.client.post(reverse('crafts:craft-delete', kwargs={'pk': craft.pk}))
        self.assertEqual(response.status_code, 403)
        craft = Craft.objects.get(pk=craft.pk)
        self.assertIn(craft, Craft.objects.all())

class AddCraftPotentialBuyerViewTests(TestCase):

    def test_add_potential_buyer(self):
        """
        Add potential buyer view should add user to craft's potential buyers
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1)
        create_craft_potetial_buyer(craft, user2)
        create_craft_potetial_buyer(craft, user3)
        self.client.post(reverse('crafts:craft-add-potential-buyer', kwargs={'pk': craft.pk}))
        response = self.client.get(reverse('crafts:craft-detail', kwargs={'pk': craft.pk}))
        self.assertQuerysetEqual(
            map(lambda x: x.buyer, response.context['object'].potential_buyers),
            [test_user, user2, user3],
            ordered=False
        )

    def test_seller_cannot_be_potential_buyer(self):
        """
        Craft's seller cannot be potential buyer
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        classification = create_classification('test1')
        craft = create_craft(classification, test_user)
        post_response = self.client.post(reverse('crafts:craft-add-potential-buyer', kwargs={'pk': craft.pk}))
        self.assertEqual(post_response.status_code, 403)
        response = self.client.get(reverse('crafts:craft-detail', kwargs={'pk': craft.pk}))
        self.assertQuerysetEqual(
            map(lambda x: x.buyer, response.context['object'].potential_buyers),
            [],
            ordered=False
        )

    def test_cannot_add_potential_buyer_when_craft_is_closed(self):
        """
        Cannot add potential buyer if craft is closed
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1, user2)
        create_craft_potetial_buyer(craft, user2)
        create_craft_potetial_buyer(craft, user3)
        response = self.client.post(reverse('crafts:craft-add-potential-buyer', kwargs={'pk': craft.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertQuerysetEqual(
            map(lambda x: x.buyer, Craft.objects.get(pk=craft.pk).potential_buyers),
            [user2, user3],
            ordered=False
        )

class RemoveCraftPotentialBuyerViewTests(TestCase):

    def test_remove_potential_buyer(self):
        """
        Remove potential buyer view should remove user from craft's potential buyers
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1)
        create_craft_potetial_buyer(craft, user2)
        create_craft_potetial_buyer(craft, user3)
        create_craft_potetial_buyer(craft, test_user)
        self.client.post(reverse('crafts:craft-remove-potential-buyer', kwargs={'pk': craft.pk}))
        response = self.client.get(reverse('crafts:craft-detail', kwargs={'pk': craft.pk}))
        self.assertQuerysetEqual(
            map(lambda x: x.buyer, response.context['object'].potential_buyers),
            [user2, user3],
            ordered=False
        )

    def test_cannot_add_potential_buyer_when_craft_is_closed(self):
        """
        Cannot remove potential buyer if craft is closed
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1, user2)
        create_craft_potetial_buyer(craft, user2)
        create_craft_potetial_buyer(craft, user3)
        create_craft_potetial_buyer(craft, test_user)
        response = self.client.post(reverse('crafts:craft-remove-potential-buyer', kwargs={'pk': craft.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertQuerysetEqual(
            map(lambda x: x.buyer, Craft.objects.get(pk=craft.pk).potential_buyers),
            [test_user, user2, user3],
            ordered=False
        )

class CraftSellerTradeOutcomeViewTests(TestCase):

    def test_seller_should_be_able_to_open_seller_trade_outcome_view(self):
        """
        Seller should be able to open seller trade outcome view
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, test_user, user1)
        response = self.client.get(reverse('crafts:craft-seller-outcome', kwargs={'pk': craft.pk}))
        self.assertEqual(response.status_code, 200)

    def test_positive_trade_outcome(self):
        """
        Positive trade outcome should set seller outcome true
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, test_user, user1)
        response = self.client.post(reverse('crafts:craft-seller-outcome', kwargs={'pk': craft.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.get(pk=craft.pk).seller_trade_outcome, True)

    def test_negative_trade_outcome(self):
        """
        Negative trade outcome should set seller outcome false
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, test_user, user1)
        response = self.client.post(reverse('crafts:craft-seller-outcome', kwargs={'pk': craft.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.get(pk=craft.pk).seller_trade_outcome, False)

    def test_seller_trade_cannot_be_closed_by_someone_else(self):
        """
        Seller side of the trade cannot be closed by someone else
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1, test_user)
        response = self.client.post(reverse('crafts:craft-seller-outcome', kwargs={'pk': craft.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Craft.objects.get(pk=craft.pk).seller_trade_outcome, None)

    def test_seller_cannot_close_their_side_of_the_trade_twice(self):
        """
        Seller cannot close their side of the trade twice
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, test_user, user1, seller_trade_outcome=True)
        response = self.client.post(reverse('crafts:craft-seller-outcome', kwargs={'pk': craft.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Craft.objects.get(pk=craft.pk).seller_trade_outcome, True)

    def test_open_craft_cannot_be_closed(self):
        """
        Open craft cannot be closed by seller
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        classification = create_classification('test1')
        craft = create_craft(classification, test_user)
        response = self.client.post(reverse('crafts:craft-seller-outcome', kwargs={'pk': craft.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Craft.objects.filter(pk=craft.pk).count(), 1)

    def test_craft_outcome_closed_by_buyer(self):
        """
        Craft that is already closed by buyer when closed by seller should change the reputations and delete the craft
        """
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        user4 = create_user('test4', 'test4@example.com', 'password')
        user5 = create_user('user5', 'user5@example.com', 'password')
        user6 = create_user('user6', 'user6@example.com', 'password')
        user7 = create_user('user7', 'user7@example.com', 'password')
        user8 = create_user('user8', 'user8@example.com', 'password')
        classification = create_classification('test1')
        craft1 = create_craft(classification, user1, user2, buyer_trade_outcome=True)
        craft2 = create_craft(classification, user3, user4, buyer_trade_outcome=True)
        craft3 = create_craft(classification, user5, user6, buyer_trade_outcome=False)
        craft4 = create_craft(classification, user7, user8, buyer_trade_outcome=False)

        self.client.force_login(user1)
        response = self.client.post(reverse('crafts:craft-seller-outcome', kwargs={'pk': craft1.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.filter(pk=craft1.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user1).reputation, 1)
        self.assertEqual(Profile.objects.get(user=user2).reputation, 1)

        self.client.force_login(user3)
        response = self.client.post(reverse('crafts:craft-seller-outcome', kwargs={'pk': craft2.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.filter(pk=craft2.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user3).reputation, 1)
        self.assertEqual(Profile.objects.get(user=user4).reputation, -1)

        self.client.force_login(user5)
        response = self.client.post(reverse('crafts:craft-seller-outcome', kwargs={'pk': craft3.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.filter(pk=craft3.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user5).reputation, -1)
        self.assertEqual(Profile.objects.get(user=user6).reputation, 1)

        self.client.force_login(user7)
        response = self.client.post(reverse('crafts:craft-seller-outcome', kwargs={'pk': craft4.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.filter(pk=craft4.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user7).reputation, -1)
        self.assertEqual(Profile.objects.get(user=user8).reputation, -1)

class CraftBuyerTradeOutcomeViewTests(TestCase):

    def test_buyer_should_be_able_to_open_buyer_trade_outcome_view(self):
        """
        Buyer should be able to open buyer trade outcome view
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1, test_user)
        response = self.client.get(reverse('crafts:craft-buyer-outcome', kwargs={'pk': craft.pk}))
        self.assertEqual(response.status_code, 200)

    def test_positive_trade_outcome(self):
        """
        Positive trade outcome should set buyer outcome true
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1, test_user)
        response = self.client.post(reverse('crafts:craft-buyer-outcome', kwargs={'pk': craft.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.get(pk=craft.pk).buyer_trade_outcome, True)

    def test_negative_trade_outcome(self):
        """
        Negative trade outcome should set buyer outcome false
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1, test_user)
        response = self.client.post(reverse('crafts:craft-buyer-outcome', kwargs={'pk': craft.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.get(pk=craft.pk).buyer_trade_outcome, False)

    def test_buyer_cannot_close_their_side_of_the_trade_twice(self):
        """
        Buyer cannot close their side of the trade twice
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, user1, test_user, buyer_trade_outcome=True)
        response = self.client.post(reverse('crafts:craft-buyer-outcome', kwargs={'pk': craft.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Craft.objects.get(pk=craft.pk).buyer_trade_outcome, True)

    def test_buyer_trade_cannot_be_closed_by_someone_else(self):
        """
        Buyer side of the trade cannot be closed by someone else
        """
        test_user = create_user('test_user', 'test_user@example.com', 'password')
        self.client.force_login(test_user)
        user1 = create_user('test1', 'test1@example.com', 'password')
        classification = create_classification('test1')
        craft = create_craft(classification, test_user, user1)
        response = self.client.post(reverse('crafts:craft-buyer-outcome', kwargs={'pk': craft.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Craft.objects.get(pk=craft.pk).buyer_trade_outcome, None)

    def test_craft_outcome_closed_by_seller(self):
        """
        Craft that is already closed by seller when closed by buyer should change the reputations and delete the craft
        """
        user1 = create_user('test1', 'test1@example.com', 'password')
        user2 = create_user('test2', 'test2@example.com', 'password')
        user3 = create_user('test3', 'test3@example.com', 'password')
        user4 = create_user('test4', 'test4@example.com', 'password')
        user5 = create_user('user5', 'user5@example.com', 'password')
        user6 = create_user('user6', 'user6@example.com', 'password')
        user7 = create_user('user7', 'user7@example.com', 'password')
        user8 = create_user('user8', 'user8@example.com', 'password')
        classification = create_classification('test1')
        craft1 = create_craft(classification, user1, user2, seller_trade_outcome=True)
        craft2 = create_craft(classification, user3, user4, seller_trade_outcome=True)
        craft3 = create_craft(classification, user5, user6, seller_trade_outcome=False)
        craft4 = create_craft(classification, user7, user8, seller_trade_outcome=False)

        self.client.force_login(user2)
        response = self.client.post(reverse('crafts:craft-buyer-outcome', kwargs={'pk': craft1.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.filter(pk=craft1.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user1).reputation, 1)
        self.assertEqual(Profile.objects.get(user=user2).reputation, 1)

        self.client.force_login(user4)
        response = self.client.post(reverse('crafts:craft-buyer-outcome', kwargs={'pk': craft2.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.filter(pk=craft2.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user3).reputation, -1)
        self.assertEqual(Profile.objects.get(user=user4).reputation, 1)

        self.client.force_login(user6)
        response = self.client.post(reverse('crafts:craft-buyer-outcome', kwargs={'pk': craft3.pk}), data={'outcome': 'True'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.filter(pk=craft3.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user5).reputation, 1)
        self.assertEqual(Profile.objects.get(user=user6).reputation, -1)

        self.client.force_login(user8)
        response = self.client.post(reverse('crafts:craft-buyer-outcome', kwargs={'pk': craft4.pk}), data={'outcome': 'False'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Craft.objects.filter(pk=craft4.pk).count(), 0)
        self.assertEqual(Profile.objects.get(user=user7).reputation, -1)
        self.assertEqual(Profile.objects.get(user=user8).reputation, -1)