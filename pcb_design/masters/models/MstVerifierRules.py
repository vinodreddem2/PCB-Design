from django.db import models

from .MstVerifierField import MstVerifierField
from .BaseModel import BaseModel
from authentication.alias import AliasField


class MstVerifierRules(BaseModel):
    id = models.AutoField(primary_key=True, editable=False, db_column='ID')
    verifier_field = models.ForeignKey(MstVerifierField, on_delete=models.CASCADE, db_column='VERIFIER_FIELD_ID')
    design_doc = models.CharField(max_length=255, db_column='DESIGN_DOC')
    rule_number = models.CharField(max_length=50, db_column='RULE_NUMBER')
    name = AliasField(db_column='RULE_NUMBER', blank=True, null=True, editable=False)

    class Meta:        
        verbose_name = 'Verifier Rule'
        verbose_name_plural = 'Verifier Rules'
        unique_together = ('verifier_field', 'design_doc', 'rule_number')

    def __str__(self):
        return f"Rule {self.rule_number} for {self.verifier_field.field_name}"
