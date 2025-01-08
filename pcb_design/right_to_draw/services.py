from django.http import Http404
from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework import status

from masters.models import MstComponent
from masters.models import MstSectionGroupings, MstSubCategoryTwo
from masters.models import MstSectionRules
from .serializers import SectionGroupingsSerializer,SubCategoryTwoSerializer, CADDesignTemplatesSerializer


def get_categories_for_component_id(component_id):
    try:
        component = MstComponent.objects.prefetch_related(
            'component_categories',
            'component_categories__subcategories'
        ).get(id=component_id)

        categories = component.component_categories.all()

        result = []
        
        for category in categories:            
            subcategories = category.subcategories.all()
            subcategory_data = [
                {
                    'id': subcategory.id,
                    'name': subcategory.sub_category_name,
                    'is_section_groupings_exists': MstSectionGroupings.objects.filter(sub_categories=subcategory).exists(),
                    'is_sub_2_categories_exists': MstSubCategoryTwo.objects.filter(sub_category_id=subcategory).exists()
                }
                for subcategory in subcategories
            ]
            
            result.append({
                'category_id': category.id,
                'category_name': category.category_name,
                'subcategories': subcategory_data
            })
    

        return result
        
    except MstComponent.DoesNotExist:

        raise Http404("Component with the given ID does not exist.")


def get_section_groupings_for_subcategory_id(sub_category_id):
    try:
        section_groupings = MstSectionGroupings.objects.filter(sub_categories__id=sub_category_id).prefetch_related(
        Prefetch("rules", queryset=MstSectionRules.objects.all())
    )
        if not section_groupings:
            return Response({"message": "No section groupings found for the given subcategory."}, status=404)
        
        serialized_data = SectionGroupingsSerializer(section_groupings, many=True)

        return serialized_data
    except MstSectionGroupings.DoesNotExist:
        raise Http404("Section Groupings with the given ID does not exist.")


def get_sub_categories_two_for_subcategory_id(sub_category_id):
    try:        
        sub_categories_two = MstSubCategoryTwo.objects.filter(sub_category_id=sub_category_id)
        
        if not sub_categories_two:
            return Response({"message": "No sub-categories two found for the given subcategory."}, status=404)
         
        serialized_data = SubCategoryTwoSerializer(sub_categories_two, many=True)
        
        return serialized_data
    except MstSubCategoryTwo.DoesNotExist:
        
        raise Http404("Sub-2 Categories with the given ID does not exist.")
    

def create_cad_template(data, user):
    component_id = data.get('component')
    component_specifications = data.get('componentSpecifications')
    design_options = data.get('designOptions')
    
    try:
        component = MstComponent.objects.get(id=component_id)
    except MstComponent.DoesNotExist:
        return None, {"error": "Component not found."}

    data_for_serializer = {
        "opp_number": data.get("oppNumber"),
        "opu_number": data.get("opuNumber"),
        "edu_number": data.get("eduNumber"),
        "model_name": data.get("modelName"),
        "part_number": data.get("partNumber"),
        "revision_number": data.get("revisionNumber"),
        "component_Id": component.pk,
        "pcb_specifications": component_specifications,
        "smt_design_options": design_options,
        'created_by':user.pk,
        'updated_by': user.pk
    }

    # Create and validate the serializer
    serializer = CADDesignTemplatesSerializer(data=data_for_serializer)
    if serializer.is_valid():        
        cad_template = serializer.save()
        return cad_template, None
    else:        
        return None, serializer.errors
