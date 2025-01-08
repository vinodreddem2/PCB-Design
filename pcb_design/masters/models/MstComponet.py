from django.db import models
from .BaseModel import BaseModel


class MstComponent(BaseModel):
    id = models.AutoField(primary_key=True, editable=False, db_column='ID')
    component_name = models.CharField(max_length=255, unique=True, db_column='COMPONENT_NAME')
    description = models.CharField(max_length=255, null=True, blank=True, db_column='DESCRIPTION')
    
    class Meta:
        verbose_name = 'Component'
        verbose_name_plural = 'Components'
    
    def __str__(self):
        return self.component_name
