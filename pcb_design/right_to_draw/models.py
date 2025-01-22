from django.db import models
from masters.models.MstComponet import MstComponent
from masters.models.BaseModel import BaseModel


class CADDesignTemplates(BaseModel):
    opp_number = models.CharField(max_length=255, unique=True, db_column='OPP_NUMBER')
    opu_number = models.CharField(max_length=255, unique=True, db_column='OPU_NUMBER')
    edu_number = models.CharField(max_length=255, unique=True, db_column='EDU_NUMBER')
    model_name = models.CharField(max_length=255, unique=True, db_column='MODEL_NAME')
    part_number = models.CharField(max_length=255, unique=True, db_column='PART_NUMBER')
    revision_number = models.CharField(max_length=255, unique=True, db_column='REVISION_NUMBER')
    component_Id = models.ForeignKey(MstComponent, on_delete=models.CASCADE, related_name='design_templates',
                                     db_column='COMPONENT_ID')
    pcb_specifications = models.JSONField(db_column='PCB_SPECIFICATIONS')
    smt_design_options = models.JSONField(db_column='SMT_DESIGN_OPTIONS')
    
    def __str__(self):
        return f"{self.model_name} ({self.part_number})"


class CADVerifierTemplates(BaseModel):
    opp_number = models.CharField(max_length=255, unique=True, db_column='OPP_NUMBER')
    opu_number = models.CharField(max_length=255, unique=True, db_column='OPU_NUMBER')
    edu_number = models.CharField(max_length=255, unique=True, db_column='EDU_NUMBER')
    model_name = models.CharField(max_length=255, unique=True, db_column='MODEL_NAME')
    part_number = models.CharField(max_length=255, unique=True, db_column='PART_NUMBER')
    revision_number = models.CharField(max_length=255, unique=True, db_column='REVISION_NUMBER')
    component_Id = models.ForeignKey(MstComponent, on_delete=models.CASCADE, related_name='verifier_templates',
                                     db_column='COMPONENT_ID')
    pcb_specifications = models.JSONField(db_column='PCB_SPECIFICATIONS')
    verifier_query_data = models.JSONField(db_column='VERIFIER_QUERY_DATA')
    
    def __str__(self):
        return f"{self.model_name} ({self.part_number})"


class CADApproverTemplates(BaseModel):
    opp_number = models.CharField(max_length=255, unique=True, db_column='OPP_NUMBER')
    opu_number = models.CharField(max_length=255, unique=True, db_column='OPU_NUMBER')
    edu_number = models.CharField(max_length=255, unique=True, db_column='EDU_NUMBER')
    model_name = models.CharField(max_length=255, unique=True, db_column='MODEL_NAME')
    part_number = models.CharField(max_length=255, unique=True, db_column='PART_NUMBER')
    revision_number = models.CharField(max_length=255, unique=True, db_column='REVISION_NUMBER')
    component_Id = models.ForeignKey(MstComponent, on_delete=models.CASCADE, related_name='approver_templates',
                                     db_column='COMPONENT_ID')
    pcb_specifications = models.JSONField(db_column='PCB_SPECIFICATIONS')
    approver_data = models.JSONField(db_column='APPROVER_QUERY_DATA')
    
    def __str__(self):
        return f"{self.model_name} ({self.part_number})"
    