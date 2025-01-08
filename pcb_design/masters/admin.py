from django.contrib import admin
from .models import MstComponent, MstCategory, MstSubCategory, MstSectionRules, MstSectionGroupings, MstSubCategoryTwo


class MstComponentAdmin(admin.ModelAdmin):
    list_display = ('id', 'component_name', 'description', 'created_by')  
    search_fields = ('component_name', 'description')  
    list_filter = ('component_name', 'created_by',)  


class MstCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'component_Id', 'created_by')  
    search_fields = ('category_name', 'component_Id__component_name')  
    list_filter = ('category_name', 'component_Id', 'created_by')  


class MstSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'sub_category_name', 'category_Id', 'created_by')  
    search_fields = ('sub_category_name', 'category_Id__category_name')  
    list_filter = ('sub_category_name', 'created_by')  


class MstSectionRulesAdmin(admin.ModelAdmin):
    list_display = ('id', 'rule_number', 'parameter', 'min_value', 'max_value', 'nominal', 'created_by')  
    search_fields = ('rule_number', 'parameter')  
    list_filter = ('rule_number', 'created_by',)  


class MstSectionGroupingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'design_doc', 'design_name', 'created_by')  
    search_fields = ('design_doc', 'design_name')  
    list_filter = ('design_name', 'created_by',)   


class MstSubCategoryTwoAdmin(admin.ModelAdmin):
    list_display = ('id', 'sub_2_category_name', 'sub_category_id', 'created_by')  
    search_fields = ('sub_2_category_name', 'sub_category_id__sub_category_name')  
    list_filter = ('sub_2_category_name', 'created_by')  


admin.site.register(MstComponent, MstComponentAdmin)
admin.site.register(MstCategory, MstCategoryAdmin)
admin.site.register(MstSubCategory, MstSubCategoryAdmin)
admin.site.register(MstSectionRules, MstSectionRulesAdmin)
admin.site.register(MstSectionGroupings, MstSectionGroupingsAdmin)
admin.site.register(MstSubCategoryTwo, MstSubCategoryTwoAdmin)
