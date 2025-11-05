import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from classifications.models import Classification

class Craft(models.Model):
    def validate_greater_than_zero(value):
        if value < 1:
            raise ValidationError(
                ('Quantity %(value)s is not allowed'),
                params={'value': value}
            )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE, related_name='craft', limit_choices_to={'has_crafts': True})
    amount = models.IntegerField(validators=[validate_greater_than_zero])
    price = models.IntegerField(validators=[validate_greater_than_zero])
    currency = models.CharField(max_length=100)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    buyer = models.ForeignKey(User, default=None, null=True, blank=True, on_delete=models.SET_DEFAULT, related_name='+')
    seller_trade_outcome = models.BooleanField(default=None, null=True)
    buyer_trade_outcome = models.BooleanField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(buyer=models.F('seller')),
                name='craft_buyer_and_seller_can_not_be_same'
            )
        ]

    @property
    def potential_buyers(self):
        return CraftPotentialBuyer.objects.filter(craft=self)

    def is_seller(self, user):
        return self.seller == user

    def is_potential_buyer(self, user):
        return self.potential_buyers.filter(buyer=user).count() > 0

    def is_buyer(self, user):
        return self.buyer == user

    def get_absolute_url(self):
        return reverse("crafts:craft-detail", args=(self.pk, ))

class CraftPotentialBuyer(models.Model):
    craft = models.ForeignKey(Craft, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['craft', 'buyer'], name='craft_and_buyer_must_be_unique'),
        ]