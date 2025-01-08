from django.db import models
from authentication.models import CustomUser

class BaseModel(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING,
                                   related_name='%(class)s_created_by',
                                   null=True, blank=True, db_column='CREATED_BY')
    created_at = models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING,
                                   related_name='%(class)s_updated_by',
                                   null=True, blank=True, db_column='UPDATED_BY')
    updated_at = models.DateTimeField(auto_now=True, db_column='UPDATED_AT')

    class Meta:
        abstract = True
