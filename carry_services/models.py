import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class CarryService(models.Model):
    def validate_greater_than_zero(value):
        if value < 1:
            raise ValidationError(
                ('Quantity %(value)s is not allowed'),
                params={'value': value}
            )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
                name='carry_service_buyer_and_seller_can_not_be_same'
            )
        ]

    @property
    def potential_buyers(self):
        return CarryServicePotentialBuyer.objects.filter(carry_service=self)

    def is_seller(self, user):
        return self.seller == user

    def is_potential_buyer(self, user):
        return self.potential_buyers.filter(buyer=user).count() > 0

    def is_buyer(self, user):
        return self.buyer == user

    def get_absolute_url(self):
        return reverse("carry_services:carry-service-detail", args=(self.pk, ))

class CarryServicePotentialBuyer(models.Model):
    carry_service = models.ForeignKey(CarryService, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['carry_service', 'buyer'], name='carry_service_and_buyer_must_be_unique'),
        ]
