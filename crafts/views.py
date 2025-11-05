from django.urls.base import reverse_lazy
from accounts.models import Profile
from django.views.generic.base import RedirectView
from django.views.generic.edit import DeleteView, FormView
from .forms import SelectBuyerForm, TradeOutcomeForm
from django.views.generic import CreateView, DetailView, UpdateView
from .models import Craft, CraftPotentialBuyer
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.template.response import SimpleTemplateResponse

class CraftCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Craft
    fields = ['classification', 'amount', 'price', 'currency']
    def test_func(self):
        return Craft.objects.filter(seller = self.request.user).count() < 5
    def handle_no_permission(self):
        return SimpleTemplateResponse('crafts/craft_create_limit.html')
    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)

class CraftDetailView(LoginRequiredMixin, DetailView):
    model = Craft

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_potential_buyer'] = self.object.is_potential_buyer(self.request.user)
        context['is_seller'] = self.object.is_seller(self.request.user)
        context['is_buyer'] = self.object.is_buyer(self.request.user)
        context['has_buyer'] = self.object.buyer != None
        context['buyer_trade_open'] = self.object.buyer_trade_outcome == None
        context['seller_trade_open'] = self.object.seller_trade_outcome == None
        return context

class AddCraftPotentialBuyerView(LoginRequiredMixin, UserPassesTestMixin, RedirectView):
    http_method_names=['post']
    pattern_name='crafts:craft-detail'

    def get_redirect_url(self, *args, **kwargs):
        object = Craft.objects.get(pk=kwargs['pk'])
        potentialBuyer = CraftPotentialBuyer(craft=object, buyer=self.request.user)
        potentialBuyer.save()
        return reverse('crafts:craft-detail', kwargs={'pk': kwargs['pk']})

    def test_func(self):
        object = Craft.objects.get(pk=self.kwargs['pk'])
        does_not_have_buyer = object.buyer == None
        is_seller = object.is_seller(self.request.user)
        return (not is_seller) and does_not_have_buyer

class RemoveCraftPotentialBuyerView(LoginRequiredMixin, UserPassesTestMixin, RedirectView):
    http_method_names=['post']
    pattern_name='crafts:craft-detail'

    def get_redirect_url(self, *args, **kwargs):
        object = Craft.objects.get(pk=kwargs['pk'])
        potentialBuyer = CraftPotentialBuyer.objects.filter(craft=object, buyer=self.request.user)
        if potentialBuyer.count() > 0:
            potentialBuyer.delete()
        return reverse('crafts:craft-detail', kwargs={'pk': kwargs['pk']})

    def test_func(self):
        object = Craft.objects.get(pk=self.kwargs['pk'])
        return object.buyer == None

class CraftSelectBuyerView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Craft
    form_class = SelectBuyerForm

    def test_func(self):
        self.object = self.get_object()
        does_not_have_buyer = self.object.buyer == None
        return self.object.is_seller(self.request.user) and does_not_have_buyer

class CraftDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Craft
    success_url = reverse_lazy('classifications:classification-list')

    def test_func(self):
        self.object = self.get_object()
        does_not_have_buyer = self.object.buyer == None
        return self.object.is_seller(self.request.user) and does_not_have_buyer

class CraftTradeOutcomeView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class=TradeOutcomeForm
    template_name='crafts/craft_tradeoutcome.html'
    success_url = reverse_lazy('classifications:classification-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_pk'] = self.kwargs['pk']
        return context

    def get_object(self):
        return Craft.objects.get(pk=self.kwargs['pk'])

class CraftSellerTradeOutcomeView(CraftTradeOutcomeView):

    def form_valid(self, form):
        self.object = self.get_object()
        
        if self.object.buyer_trade_outcome == None:
            if form.cleaned_data['outcome'] == 'True':
                self.object.seller_trade_outcome = True
            else:
                self.object.seller_trade_outcome = False
            self.object.save()
        else:
            buyer_profile = Profile.objects.get(user=self.object.buyer)
            seller_profile = Profile.objects.get(user=self.object.seller)
            if form.cleaned_data['outcome'] == 'True':
                buyer_profile.reputation += 1
            else:
                buyer_profile.reputation -= 1
            if self.object.buyer_trade_outcome:
                seller_profile.reputation += 1
            else:
                seller_profile.reputation -= 1
            buyer_profile.save()
            seller_profile.save()
            self.object.delete()
        return super().form_valid(form)

    def test_func(self):
        self.object = self.get_object()
        has_buyer = self.object.buyer != None
        seller_trade_open = self.object.seller_trade_outcome == None
        return self.object.is_seller(self.request.user) and has_buyer and seller_trade_open

class CraftBuyerTradeOutcomeView(CraftTradeOutcomeView):

    def form_valid(self, form):
        self.object = self.get_object()
        
        if self.object.seller_trade_outcome == None:
            if form.cleaned_data['outcome'] == 'True':
                self.object.buyer_trade_outcome = True
            else:
                self.object.buyer_trade_outcome = False
            self.object.save()
        else:
            buyer_profile = Profile.objects.get(user=self.object.buyer)
            seller_profile = Profile.objects.get(user=self.object.seller)
            if form.cleaned_data['outcome'] == 'True':
                seller_profile.reputation += 1
            else:
                seller_profile.reputation -= 1
            if self.object.seller_trade_outcome:
                buyer_profile.reputation += 1
            else:
                buyer_profile.reputation -= 1
            buyer_profile.save()
            seller_profile.save()
            self.object.delete()
        return super().form_valid(form)

    def test_func(self):
        self.object = self.get_object()
        has_buyer = self.object.buyer != None
        buyer_trade_open = self.object.buyer_trade_outcome == None
        return self.object.is_buyer(self.request.user) and has_buyer and buyer_trade_open