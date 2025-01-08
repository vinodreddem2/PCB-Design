from django.db import models

from .BaseModel import BaseModel
from .MstSubCategory import MstSubCategory
from .MstSectionRules import MstSectionRules


class MstSectionGroupings(BaseModel):
    id = models.AutoField(primary_key=True, editable=False, db_column='ID')
    design_doc = models.CharField(max_length=255, db_column='DESIGN_DOC')
    design_name = models.CharField(max_length=255, unique=True, db_column='DESIGN_NAME')
    rules = models.ManyToManyField(MstSectionRules, db_column='RULES')
    sub_categories = models.ManyToManyField(MstSubCategory, db_column='SUB_CATEGORIES')

    class Meta:
        verbose_name = 'Section Grouping'
        verbose_name_plural = 'Section Groupings'

    def __str__(self):
        return f"{self.design_name}-{self.design_doc}"

