from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.
class TagItemManager(models.Manager):
    def get_for_content(self, content, content_id):
        content_type = ContentType.objects.get_for_model(content)
        query_set = TagItem.objects.filter(content_type=content_type, object_id=content_id)
        return query_set
    # def all(self):
    #     return TagItem.objects.filter(object_id=2)
class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(object_id=4)

    def all_new_product(self):
        return TagItem.new_object.filter(object_id=8)

class Tag(models.Model):
    label = models.CharField(max_length=255)

class TagItem(models.Model):
    objects = TagItemManager()
    new_object = ProductManager()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()