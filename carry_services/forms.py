from django import forms
from .models import CarryService, CarryServicePotentialBuyer
from django.contrib.auth.models import User

class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.username

class SelectBuyerForm(forms.ModelForm):
    class Meta:
        model = CarryService
        fields = ['buyer']

    buyer = UserModelChoiceField(queryset=User.objects.all(), to_field_name='username')

    def __init__(self, *args, **kwargs):
        super(SelectBuyerForm, self).__init__(*args, **kwargs)
        if self.instance:
            pks = CarryServicePotentialBuyer.objects.filter(carry_service=self.instance).exclude(buyer=self.instance.seller).values('buyer')
            self.fields['buyer'].queryset = User.objects.filter(pk__in=pks)

class TradeOutcomeForm(forms.Form):
    TRUE_FALSE_CHOICES = [
        (True, 'Yes'),
        (False, 'No')
    ]
    outcome = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, label='Did the trade work out?', initial='', widget=forms.Select(), required=True)