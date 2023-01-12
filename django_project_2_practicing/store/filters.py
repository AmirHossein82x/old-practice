from django_filters.rest_framework import FilterSet
from rest_framework import filters
from .models import Product
class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'collection_id': ['exact'],
            'unit_price': ['gt', 'lt']
        }

class CustomSearchFilter(filters.SearchFilter):
   search_param = 'title'