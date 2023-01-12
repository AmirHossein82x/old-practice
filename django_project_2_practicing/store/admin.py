from django.contrib import admin, messages
from django.db.models import Count, QuerySet
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html, urlencode
from django.urls import reverse

from tags.models import TagItem, Tag
from .models import *


# Register your models here.
class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'low'),
            ('>10', 'high')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)
        return queryset.filter(inventory__gt=10)


# class TagInline(GenericTabularInline):
#     model = TagItem


@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    # inlines = [TagInline]
    list_display = ['title', 'unit_price', 'collection_title', 'inventory_des']
    list_select_related = ['collection']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    search_fields = ['title__istartswith']
    actions = ['clear_inventory']

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='-inventory')
    def inventory_des(self, product):
        return 'Ok' if product.inventory > 10 else 'No'

    @admin.action(description='update inventory to 0')
    def clear_inventory(self, request, queryset: QuerySet):
        updated_count = queryset.update(inventory=0)
        product = None
        was_were = None
        if updated_count == 1:
            product = 'product'
            was_were = 'was'
        else:
            product = 'products'
            was_were = 'were'
        self.message_user(request,
                          f"{updated_count} {product} {was_were} updated",
                          messages.INFO)


@admin.register(Customer)
class AdminCustomer(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'membership', 'number_of_order']
    list_filter = ['membership']
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']
    list_per_page = 10
    list_select_related = ['user']
    autocomplete_fields = ['user']

    def get_queryset(self, request):
        return super(AdminCustomer, self).get_queryset(request).annotate(number_of_order=Count('order'))

    def number_of_order(self, customer):
        return customer.number_of_order


@admin.register(Collection)
class AdminCollection(admin.ModelAdmin):
    list_display = ['title', 'product_quantity']

    @admin.display(ordering='-product_quantity')
    def product_quantity(self, collection):
        url = (reverse('admin:store_product_changelist')
               + "?" +
               urlencode({
                   'collection__id__exact': str(collection.id)
               })
               )
        return format_html("<a href='{}'>{}</a>", url, collection.product_quantity)

    def get_queryset(self, request):
        return super(AdminCollection, self).get_queryset(request).annotate(product_quantity=Count('products'))


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'payment_status']
    inlines = [OrderItemInline]
