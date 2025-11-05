from django.views.generic import ListView, DetailView
from .models import Classification
from django.contrib.auth.mixins import LoginRequiredMixin
from crafts.models import Craft

class ClassificationListView(LoginRequiredMixin, ListView):
    model = Classification

    def get_queryset(self):
        return Classification.objects.filter(parent=None)

class ClassificationDetailView(LoginRequiredMixin, DetailView):
    model = Classification

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_by'] = self.request.GET.get("searchby", "seller")
        context['search'] = self.request.GET.get("search", "")
        self.object = self.get_object()
        all_craft = Craft.objects.filter(classification=self.object)
        if context['search_by'] != None and context['search'] != None:
            if context['search_by'] == 'seller':
                context['craft_list'] = all_craft.filter(seller__username__contains=context['search'])
            elif context['search_by'] == 'buyer':
                context['craft_list'] = all_craft.filter(buyer__username__contains=context['search'])
            else:
                context['craft_list'] = all_craft.all()
        context['classification_list'] = Classification.objects.filter(parent=self.object)
        return context