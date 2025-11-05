from accounts.models import Profile
from django.views.generic.base import RedirectView
from django.views.generic.edit import DeleteView, FormView
from .forms import SelectBuyerForm, TradeOutcomeForm
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from .models import CarryService, CarryServicePotentialBuyer
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.template.response import SimpleTemplateResponse


class CarryServiceListView(LoginRequiredMixin, ListView):
    model = CarryService
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_by'] = self.request.GET.get("searchby", "seller")
        context['search'] = self.request.GET.get("search", "")
        return context
    def get_queryset(self):
        search_by = self.request.GET.get("searchby", None)
        search = self.request.GET.get("search", None)
        if search_by != None and search != None:
            if search_by == 'seller':
                return CarryService.objects.filter(seller__username__contains=search)
            elif search_by == 'buyer':
                return CarryService.objects.filter(buyer__username__contains=search)
            elif search_by == 'type':
                return CarryService.objects.filter(type__contains=search)
        return super().get_queryset()
            

class CarryServiceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = CarryService
    fields = ['price', 'currency']
    def test_func(self):
        return CarryService.objects.filter(seller = self.request.user).count() < 5
    def handle_no_permission(self):
        return SimpleTemplateResponse('carry_services/carryservice_create_limit.html')
    def form_valid(self, form):
        form.instance.seller = self.request.user
        return super().form_valid(form)

class CarryServiceDetailView(LoginRequiredMixin, DetailView):
    model = CarryService

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_potential_buyer'] = self.object.is_potential_buyer(self.request.user)
        context['is_seller'] = self.object.is_seller(self.request.user)
        context['is_buyer'] = self.object.is_buyer(self.request.user)
        context['has_buyer'] = self.object.buyer != None
        context['buyer_trade_open'] = self.object.buyer_trade_outcome == None
        context['seller_trade_open'] = self.object.seller_trade_outcome == None
        return context

class AddCarryServicePotentialBuyerView(LoginRequiredMixin, UserPassesTestMixin, RedirectView):
    http_method_names=['post']
    pattern_name='carry_services:carry-service-detail'
    def get_redirect_url(self, *args, **kwargs):
        object = CarryService.objects.filter(pk=kwargs['pk']).first()
        potentialBuyer = CarryServicePotentialBuyer(carry_service=object, buyer=self.request.user)
        potentialBuyer.save()
        return reverse('carry_services:carry-service-detail', kwargs={'pk': kwargs['pk']})
    def test_func(self):
        object = CarryService.objects.get(pk=self.kwargs['pk'])
        does_not_have_buyer = object.buyer == None
        is_seller = object.is_seller(self.request.user)
        return (not is_seller) and does_not_have_buyer

class RemoveCarryServicePotentialBuyerView(LoginRequiredMixin, UserPassesTestMixin, RedirectView):
    http_method_names=['post']
    pattern_name='carry_services:carry-service-detail'
    def get_redirect_url(self, *args, **kwargs):
        object = CarryService.objects.filter(pk=kwargs['pk']).first()
        potentialBuyer = CarryServicePotentialBuyer.objects.filter(carry_service=object, buyer=self.request.user)
        if potentialBuyer.count() > 0:
            potentialBuyer.delete()
        return reverse('carry_services:carry-service-detail', kwargs={'pk': kwargs['pk']})
    def test_func(self):
        object = CarryService.objects.get(pk=self.kwargs['pk'])
        return object.buyer == None

class CarryServiceSelectBuyerView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CarryService
    form_class = SelectBuyerForm
    def test_func(self):
        self.object = self.get_object()
        does_not_have_buyer = self.object.buyer == None
        return self.object.is_seller(self.request.user) and does_not_have_buyer

class CarryServiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CarryService

    def get_success_url(self):
        return reverse('carry_services:carry-service-list')

    def test_func(self):
        self.object = self.get_object()
        does_not_have_buyer = self.object.buyer == None
        return self.object.is_seller(self.request.user) and does_not_have_buyer

class CarryServiceTradeOutcomeView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class=TradeOutcomeForm
    template_name='carry_services/carryservice_tradeoutcome.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_pk'] = self.kwargs['pk']
        return context

    def get_object(self):
        return CarryService.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('carry_services:carry-service-list')

class CarryServiceSellerTradeOutcomeView(CarryServiceTradeOutcomeView):

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

class CarryServiceBuyerTradeOutcomeView(CarryServiceTradeOutcomeView):

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