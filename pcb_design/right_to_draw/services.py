from django.http import Http404, HttpResponseServerError
from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import CADVerifierTemplates, CADDesignTemplates
from masters.models import MstComponent, MstSubCategoryTwo, MstDesignOptions, MstSectionRules, \
    MstSectionGroupings, MstVerifierField, MstVerifierField, MstVerifierRules, MstCategory, MstSubCategory, \
    MstConditions
from .serializers import SectionGroupingsSerializer,SubCategoryTwoSerializer, CADDesignTemplatesSerializer, \
    SectionRulesSerializer, MstVerifierFieldSerializer, CADVerifierTemplateSerializer,CADApproverTemplateSerializer
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from . import right_to_draw_logs


def get_categories_for_component_id(component_id, is_verifier=0):
    right_to_draw_logs.info(f"Get categories for component_id: {component_id}, is_verifier: {is_verifier}")
    try:
        component = MstComponent.objects.prefetch_related(
            'component_categories',
            'component_categories__subcategories'
        ).get(id=component_id)

        if is_verifier == 1:            
            categories = component.component_categories.filter(is_verifier=True)
        else:            
            categories = component.component_categories.all()

        result = []
        
        for category in categories:            
            if is_verifier == 1:                
                subcategories = category.subcategories.filter(is_verifier=True)
            else:                
                subcategories = category.subcategories.all()
                
            subcategory_data = [
                {
                    'id': subcategory.id,
                    'name': subcategory.sub_category_name,
                    'is_design_options_exists': MstDesignOptions.objects.filter(sub_category_id=subcategory).exists(),
                    'is_sub_2_categories_exists': MstSubCategoryTwo.objects.filter(sub_category_id=subcategory).exists(),
                    'has_verifier_fields': MstVerifierField.objects.filter(sub_category=subcategory).exists()
                }
                for subcategory in subcategories
            ]
            right_to_draw_logs.info(f"Number of Subcategories: {len(subcategory_data)} for Category: {category.name}")
            
            result.append({
                'category_id': category.id,
                'category_name': category.category_name,
                'subcategories': subcategory_data
            })
    
        right_to_draw_logs.info(f"Number of Categorie: {len(result)} for Component ID: {component_id}")
        return result
        
    except MstComponent.DoesNotExist:
        error_log = f"Component with ID {component_id} does not exist."
        right_to_draw_logs.info(error_log)
        right_to_draw_logs.error(error_log)
        raise Http404("Component with the given ID does not exist.")


def get_sub_categories_two_for_subcategory_id(sub_category_id):
    right_to_draw_logs.info(f"Get sub-categories two for subcategory_id: {sub_category_id}")
    try:        
        sub_categories_two = MstSubCategoryTwo.objects.filter(sub_category_id=sub_category_id)
        right_to_draw_logs.info(f"Number of Sub-categories two: {len(sub_categories_two)} for Sub Category ID: {sub_category_id}")
        if not sub_categories_two:
            error_log=f"No sub-categories two found for the given subcategory ID: {sub_category_id}"
            right_to_draw_logs.info(error_log)            
            return Response({"message": "No sub-categories two found for the given subcategory."}, status=404)
         
        serialized_data = SubCategoryTwoSerializer(sub_categories_two, many=True)
        
        return serialized_data
    except Exception as ex:
        error_log=f" Exception Occurred for fetching the Sub Categories Level Two for  {sub_category_id}"
        right_to_draw_logs.info(error_log)
        right_to_draw_logs.error(error_log)
        raise HttpResponseServerError("Exception Occurred for fetching the Sub Categories Level Two.")
    

def get_design_options_for_sub_category(sub_category_id):
    right_to_draw_logs.info(f"Get design options for sub_category_id: {sub_category_id}")
    try:     
        design_options = MstDesignOptions.objects.filter(sub_category_id=sub_category_id)
        right_to_draw_logs.info(f"Design Options: {len(design_options)}")
        
        if not design_options.exists():
            error_log=f"No Design Options found for the given Sub Category ID: {sub_category_id}"
            right_to_draw_logs.info(error_log)            
            raise Http404("No Design Options found for the given Sub Category ID.")
        
        result = []
        for design_option in design_options:
            result.append({
                'design_option_id': design_option.id,
                'desing_option_name': design_option.desing_option_name
            })
        
        right_to_draw_logs.info(f"Number of Design Options: {len(result)} for Sub Category ID: {sub_category_id}")
        return result

    except Exception as e:
        error_log = f"An error occurred while fetching design options: {str(e)}"
        right_to_draw_logs.info(error_log)
        right_to_draw_logs.error(error_log)
        raise HttpResponseServerError(f"An error occurred while fetching design options: {str(e)}")


def get_design_rules_for_design_option(design_option_ids):
    right_to_draw_logs.info(f"Get design rules for design_option_ids: {design_option_ids}")
    try:
        right_to_draw_logs.info("Prefetching MstDesignOptions and MstDesignOptions__section_groups__rules")
        design_options = MstDesignOptions.objects.prefetch_related('section_groups__rules').filter(id__in=design_option_ids)

        rules_data = []
        unique_rule_ids = set()

        for design_option in design_options:            
            for group in design_option.section_groups.all():                
                for rule in group.rules.all():
                    if rule.id not in unique_rule_ids:
                        unique_rule_ids.add(rule.id)
                        rule_serializer = SectionRulesSerializer(rule)
                        rules_data.append(rule_serializer.data)
                        
        right_to_draw_logs.info(f"Number of Design Rules: {len(rules_data)} for Design Option IDs: {design_option_ids}")
        return rules_data

    except Exception as e:
        error_log = f"An error occurred while fetching design rules: {str(e)}"
        right_to_draw_logs.info(error_log)
        right_to_draw_logs.error(error_log)
        raise Http404(f"An error occurred while fetching design rules: {str(e)}")
    
 
def create_cad_template(data, user):
    component_id = data.get('component')
    component_specifications = data.get('componentSpecifications')
    design_options = data.get('designOptions')
    
    right_to_draw_logs.info(f"Create CAD Template for component_id: {component_id}, component_specifications: {component_specifications}, design_options: {design_options}")
    try:
        component = MstComponent.objects.get(id=component_id)
        right_to_draw_logs.info(f"Component with ID {component_id} found")
    except MstComponent.DoesNotExist:
        error_log=f"Component with ID {component_id} does not exist."
        right_to_draw_logs.info(error_log)
        right_to_draw_logs.error(error_log)
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
    log_Str = f"for component_id: {component_id}, Opp Number {data.get('oppNumber')}, \
            Opu Number {data.get('opuNumber')}, Edu Number {data.get('eduNumber')}, \
            Model Name {data.get('modelName')}, Part Number {data.get('partNumber')}, \
            Revision Number {data.get('revisionNumber')}"
    
    if serializer.is_valid():  
        right_to_draw_logs.info(f"CAD Design Template Saving {log_Str}")      
        cad_template = serializer.save()
        return cad_template, None
    else:
        right_to_draw_logs.error(f"Error Saving in CAD Design Template {log_Str}")       
        right_to_draw_logs.info(f"Error Saving in CAD Design Template {log_Str}")       
        return None, serializer.errors


def get_verifier_fields_by_params(component_id=None, category_id=None, sub_category_id=None):    
    right_to_draw_logs.info(f"Get verifier fields by params: component_id: {component_id}, category_id: {category_id}, sub_category_id: {sub_category_id}")
    filter_criteria = Q()
    if component_id:        
        filter_criteria &= Q(component_id=component_id)
    if category_id:        
        filter_criteria &= Q(category_id=category_id)
    if sub_category_id:        
        filter_criteria &= Q(sub_category__id=sub_category_id)
    verifier_fields = MstVerifierField.objects.filter(filter_criteria).distinct().order_by('id')
    right_to_draw_logs.info(f"Verifier Fields: {len(verifier_fields)} for component_id: {component_id}, category_id: {category_id}, sub_category_id: {sub_category_id}")
    serializer = MstVerifierFieldSerializer(verifier_fields, many=True)

    return serializer.data


def create_cad_verifier_template(data, user):
    right_to_draw_logs.info(f"Create CAD Verifier Template")
    
    component_id = data.get('component')
    design_compare_data = data.get('design_compare_data', [])
    verify_compare_data = data.get('verify_compare_data', [])    
    
    try:
        component = MstComponent.objects.get(id=component_id)
        right_to_draw_logs.info(f"Component with ID {component_id} found")
    except MstComponent.DoesNotExist:
        error_log=f"Component with ID {component_id} does not exist."
        right_to_draw_logs.info(error_log)
        right_to_draw_logs.error(error_log)
        return None, {"error": "Component not found."}  
    
    template_data = {
        "opp_number": data.get("oppNumber"),
        "opu_number": data.get("opuNumber"),
        "edu_number": data.get("eduNumber"),
        "model_name": data.get("modelName"),
        "part_number": data.get("partNumber"),
        "revision_number": data.get("revisionNumber"),
        "component_Id": component.pk,
        "pcb_specifications": data.get("componentSpecifications", {}),
        "verifier_query_data": data.get("verifierQueryData", {}),
        'created_by':user.pk,
        'updated_by': user.pk
    }
    log_str = f"for component_id: {component_id}, Opp Number {data.get('oppNumber')}, \
                Opu Number {data.get('opuNumber')}, Edu Number {data.get('eduNumber')}, Model Name {data.get('modelName')}, \
                Part Number {data.get('partNumber')}, Revision Number {data.get('revisionNumber')}"

    # Create and validate the serializer
    serializer = CADVerifierTemplateSerializer(data=template_data)
    if serializer.is_valid():
        right_to_draw_logs.info(f"CAD Verifier Template Saving {log_str}")
        cad_verifier_template = serializer.save()            
        return cad_verifier_template, None
    else:
        right_to_draw_logs.error(f"Error Saving in CAD Verifier Template {log_str} -- Error is {serializer.errors}")
        right_to_draw_logs.info(f"Error Saving in CAD Verifier Template {log_str} -- Error is {serializer.errors}")        
        return None, serializer.errors


def condition_operators(condition, target_value):    
    is_deviated = False
    if condition.comparison_operator == 'range':
        if not (float(target_value) >= condition.comparison_min_value  and \
                float(target_value) <= condition.comparison_max_value):
            is_deviated = True
    elif condition.comparison_operator == 'eq':
        if not float(target_value) == condition.comparison_min_value:
            is_deviated = True
    elif condition.comparison_operator == 'gte':
        if not(float(target_value) >= condition.comparison_max_value):
            is_deviated = True
    elif condition.comparison_operator == 'lte':
        if not float(target_value) <= condition.comparison_min_value:
            is_deviated = True
    elif condition.comparison_operator == 'gt':
        if not float(target_value) > condition.comparison_max_value:
            is_deviated = True
    elif condition.comparison_operator == 'lt':
        if not float(target_value) < condition.comparison_min_value:
            is_deviated = True
    return is_deviated


def check_conditions(sub_category, pcb_specifications_inp):
    pcb_specifications = {int(k):v for k, v in pcb_specifications_inp.items()}    
    conditions = MstConditions.objects.filter(subcategory=sub_category.id)    
    is_deviated = False
    right_to_draw_logs.info(f"Checking conditions for sub_category: {sub_category.name}, conditions: {len(conditions)}")
    # Check for condition operator and comparison
    for condition in conditions:
        right_to_draw_logs.info(f"Checking conditions for sub_category: {sub_category.name}, condition Variable : {condition.condition_variable} & Compare Variable {condition.comparison_variable}")
        if condition.condition_variable == 'B14 Size':            
            b14_size_id = MstCategory.objects.get(category_name='B14 Size').id
            selected_val = pcb_specifications.get(b14_size_id)
            if  selected_val:
                selected_val = float(selected_val)            
                is_condition_satisfied = False
                target_val = None
                # It is Dielectric thickness
                if condition.comparison_variable == 'Dielectric Thickness':
                    dielectric_material_thickness_id = MstCategory.objects.get(category_name='Dielectric Thickness').id
                    target_val = pcb_specifications.get(dielectric_material_thickness_id)
                    
                right_to_draw_logs.info(f"Selected Value is : {selected_val} and Target Value is {target_val}")
                if target_val:                
                    if condition.condition_operator == 'range':
                        if selected_val >= condition.condition_min_value and \
                            selected_val < condition.condition_max_value:                    
                            is_condition_satisfied = True                        
                    elif condition.condition_operator == 'gte':      
                        if selected_val >= condition.condition_max_value:
                            is_condition_satisfied = True                        

                    elif condition.condition_operator == 'lte':
                        if selected_val <= condition.condition_min_value:
                            is_condition_satisfied = True
                    elif condition.condition_operator == 'gt':
                        if selected_val > condition.condition_max_value:
                            is_condition_satisfied = True
                    elif condition.condition_operator == 'lt':
                        if selected_val < condition.condition_min_value:
                            is_condition_satisfied = True
                    elif condition.condition_operator == 'eq':
                        if selected_val == condition.condition_min_value:
                            is_condition_satisfied = True
                else:
                    continue
                
                right_to_draw_logs.info(f"Is Basic Condition Satisfied {is_condition_satisfied}")
                if is_condition_satisfied:
                    is_deviated = condition_operators(condition, target_val)
            if is_deviated:
                break
    
    right_to_draw_logs.info(f"Condition is_deviated: {is_deviated}")            
    return is_deviated


def compare_verifier_data_with_design_data(data):    
    design_specifications_data = data.get('componentSpecifications')
    opp_number = data.get("oppNumber")
    opu_number = data.get("opuNumber")
    edu_number = data.get("eduNumber")
    model_name = data.get("modelName")
    part_number = data.get("partNumber")
    revision_number = data.get("revisionNumber")
    component_id = data.get('component')
    
    log_str = f"for component_id: {component_id}, Opp Number {opp_number}, \
                Opu Number {opu_number}, Edu Number {edu_number}, Model Name {model_name}, \
                Part Number {part_number}, Revision Number {revision_number}"
    
    right_to_draw_logs.info(f"The Verification Rules Started {log_str}")
                
    design_specifications_data = data.get('componentSpecifications')

    design_verification_res = []

    template = CADDesignTemplates.objects.filter(
        opp_number=opp_number,
        opu_number=opu_number,
        edu_number=edu_number,
        model_name=model_name,
        part_number=part_number,
        revision_number=revision_number,
        component_Id=component_id
    ).first()

    if not template:
        right_to_draw_logs.error(f"No matching CADDesignTemplate found for Verifier Template {log_str}")
        return {}       
    
    pcb_specifications_d = template.pcb_specifications 
    pcb_specifications = {int(k):int(v) for k, v in pcb_specifications_d.items()}
    
    # Looping Each record from the verfier template
    # Here B14 Size and Dielectric Thickness is going to be the Text Boxes
    for category_id, selected_sub_category_id in design_specifications_data.items():
        category_id = int(category_id)        
        try:
            category = MstCategory.objects.get(id=category_id)
        except ObjectDoesNotExist as ex:
            right_to_draw_logs.info(f"Design Verifications - Invalid Category Id submitted: {category_id} for component_id: {component_id}")
            is_deviated = True
            deviation_result = {
                'categor_id' : category_id,
                'name': "Invalid Category Id",
                'selected_deviation_id': "N/A",
                'selected_deviation_name': "N/A",
                'is_deviated': True
            }
            design_verification_res.append(deviation_result)
            continue
        right_to_draw_logs.info(f"Design Verifiation started for : {category.category_name.strip()} -- Value Selected {selected_sub_category_id}")   
        # For Dielectric Thickness, The Verifer enter the value manually Entered Value Instead 
        # of selecting from Drop Down
        if category.category_name.strip() == 'Dielectric Thickness':
            right_to_draw_logs.info(f"Validating the Dielectric Thickness category value {selected_sub_category_id}")
            selected_val = float(selected_sub_category_id)
            
            # Value should match with the value selected in Design Template
            # Steps to Check:
            # Get the Sub-Category Id of selected in Design Template
            # Get the Value of the Sub-Category from Name column
            # Compare the Both the values Should be match
            if category_id in pcb_specifications:
                right_to_draw_logs.info(f"Dielectric Thickness Present in the Design Template {category_id}")
                dielectric_thickness_sub_category = pcb_specifications.get(category_id)
                sub_category = MstSubCategory.objects.get(id=dielectric_thickness_sub_category)
                design_val = float(sub_category.name.strip('"'))
                if design_val != selected_val:
                    is_deviated = True

                deviation_result = {
                    'categor_id' : category_id,
                    'name': category.category_name,
                    'selected_deviation_id': "N/A",
                    'selected_deviation_name': selected_val,
                    'is_deviated': is_deviated
                }
                design_verification_res.append(deviation_result)
                right_to_draw_logs.info(f"The Dielectric Thickness result for {selected_sub_category_id}, component_id: {component_id} is {is_deviated}")
                continue
        elif  category.category_name.strip() == 'B14 Size':
            continue

        else:
            try:
                sub_category = MstSubCategory.objects.get(id=int(selected_sub_category_id))
            except ObjectDoesNotExist:
                right_to_draw_logs.info(f"Design Verifications - Invalid Sub Category Id submitted: {selected_sub_category_id} for Category Id{category_id} & component_id: {component_id}")                
                deviation_result = {
                    'categor_id' : category_id,
                    'name': category.category_name,
                    'selected_deviation_id': selected_sub_category_id,
                    'selected_deviation_name': "N/A",
                    'is_deviated': False
                }
                design_verification_res.append(deviation_result)
                continue                
            if category_id in pcb_specifications:            
                if pcb_specifications.get(category_id) != int(selected_sub_category_id):
                    is_deviated = True                
                else:
                    is_deviated = False                    
            else:
                is_deviated = False

            if MstConditions.objects.filter(subcategory=sub_category.pk).exists():
                is_deviated = check_conditions(sub_category, design_specifications_data)

            right_to_draw_logs.info(f"Design Verifications - Category Id: {category_id}, is_deviated: {is_deviated}")
            deviation_result = {
                'categor_id' : category_id,
                'name': category.category_name,
                'selected_deviation_id': selected_sub_category_id,
                'selected_deviation_name': sub_category.sub_category_name,
                'is_deviated': is_deviated 
            }

            design_verification_res.append(deviation_result)
    right_to_draw_logs.info(f"Design Verification completed for {log_str}")
    return design_verification_res


def comapre_verfier_data_with_rules(verifier_id, field_value):    
    try:
        right_to_draw_logs.info(f"Compare verifier data with rules for verifier_id: {verifier_id}, field_value: {field_value}") 
        verifier_field = MstVerifierField.objects.get(id=int(verifier_id))        
        verifier_rule = MstVerifierRules.objects.get(verifier_field=verifier_field.pk)        
        rule_number = verifier_rule.rule_number
        design_doc = verifier_rule.design_doc                
        section_rule = MstSectionRules.objects.get(rule_number=rule_number, design_doc=design_doc)
        try:        
            min_value = float(section_rule.min_value) if section_rule.min_value else None                   
        except Exception as e:
            min_value = None

        try:                    
            max_value = float(section_rule.max_value) if section_rule.max_value else None        
        except Exception as e:
            max_value = None


        is_deviation = False
        if (min_value is not None and field_value < min_value) or (max_value is not None and field_value > max_value):
            is_deviation = True
        
        return is_deviation

    except ObjectDoesNotExist as ex:
        right_to_draw_logs.info(f"Verifier Field or Rule not found: {str(ex)}")
        right_to_draw_logs.error(f"Verifier Field or Rule not found: {str(ex)}")
        return False
    except Exception as ex:
        right_to_draw_logs.error(f"An error occurred while comparing verifier data with rules: {str(ex)}")
        right_to_draw_logs.info(f"An error occurred while comparing verifier data with rules: {str(ex)}")
        return False

def comapre_verfier_data(verified_data):
    verifier_res = []
    for id, val in verified_data.items():
        val = float(val)
        is_deviated = comapre_verfier_data_with_rules(id, val)
        verifier_field = MstVerifierField.objects.get(id=id)
        name = verifier_field.name
        data = {'id' :id, 'name':name, 'value':val, 'is_deviated':is_deviated}
        verifier_res.append(data)
    return verifier_res


def compare_verifier_data_with_rules_and_designs(data):    
    res = {
        "opp_number": data.get("oppNumber"),
        "opu_number": data.get("opuNumber"),
        "edu_number": data.get("eduNumber"),
        "model_name": data.get("modelName"),
        "part_number": data.get("partNumber"),
        "revision_number": data.get("revisionNumber"), 
        "component_id": data.get('component')     
    }

    result_string = ", ".join(f"{key}: {value}" for key, value in res.items())
    
    design_specification_data = compare_verifier_data_with_design_data(data)
    if not design_specification_data:
        return {}
    res['verify_design_fields_data']= design_specification_data

    right_to_draw_logs.info(f"Compare verifier data with rules and designs for {result_string}")    
    verified_rule_data = comapre_verfier_data(data.get("verifierQueryData"))
    res['verified_query_data'] = verified_rule_data


    right_to_draw_logs.info(f"Verification Completed for {result_string}")
    return res


def get_verifier_record(request_data):
    """
    This function takes the request data, queries the CADVerifierTemplates table
    based on the parameters provided, and returns the data in the required format.
    """
    right_to_draw_logs.info(f"Get verifier record for request data")
    # Extract the parameters from the request data
    right_to_draw_logs.info("Extract the parameters from the request data")
    opp_number = request_data.get('oppNumber')
    opu_number = request_data.get('opuNumber')
    edu_number = request_data.get('eduNumber')
    model_name = request_data.get('modelName')
    part_number = request_data.get('partNumber')
    revision_number = request_data.get('revisionNumber')
    component_id = request_data.get('component')

    # Query the CADVerifierTemplates table based on the parameters
    try:
        right_to_draw_logs.info(f"Querying CADVerifierTemplates table to get verifier record for parameters: {opp_number}, {opu_number}, {edu_number}, {model_name}, {part_number}, {revision_number}, {component_id}")
        verifier_record = CADVerifierTemplates.objects.get(
            opp_number=opp_number,
            opu_number=opu_number,
            edu_number=edu_number,
            model_name=model_name,
            part_number=part_number,
            revision_number=revision_number,
            component_Id=component_id
        )
    except ObjectDoesNotExist as ex:
        error_log = f"Verifier record not found: {str(ex)}"
        right_to_draw_logs.info(error_log)
        right_to_draw_logs.error(error_log)
        raise ObjectDoesNotExist('Verifier record not found.')

    # Prepare the response data in the required format
    response_data = {
        'oppNumber': verifier_record.opp_number,
        'opuNumber': verifier_record.opu_number,
        'eduNumber': verifier_record.edu_number,
        'modelName': verifier_record.model_name,
        'partNumber': verifier_record.part_number,
        'revisionNumber': verifier_record.revision_number,
        'component': verifier_record.component_Id.id,

        'componentSpecifications': verifier_record.pcb_specifications,
        'verifierQueryData': verifier_record.verifier_query_data
    }
    right_to_draw_logs.info(f"Response data prepared for the queried verifier record")
    return response_data


def save_approver_results(data, user):
    try:
        template_data = {
            "opp_number": data.get("oppNumber"),
            "opu_number": data.get("opuNumber"),
            "edu_number": data.get("eduNumber"),
            "model_name": data.get("modelName"),
            "part_number": data.get("partNumber"),
            "revision_number": data.get("revisionNumber"),
            "component_Id":data.get('component'),
            "pcb_specifications": data.get("componentSpecifications", {}),
            "approver_data": data.get("approverQueryData", {}),
            "status": data.get("status"),
            "comments": data.get("comments"),
            "created_by": user.id,
            "updated_by": user.id
        }
        serializer = CADApproverTemplateSerializer(data=template_data)

        log_str = f"for component_id: {data.get('component')}, Opp Number {data.get('oppNumber')}, \
                    Opu Number {data.get('opuNumber')}, Edu Number {data.get('eduNumber')}, Model Name {data.get('modelName')}, \
                    Part Number {data.get('partNumber')}, Revision Number {data.get('revisionNumber')}"
        
        if serializer.is_valid():        
            template = serializer.save()
            return template, None
            
        else:
            right_to_draw_logs.error(f"Error Saving in Approver Template {log_str} -- Error is {serializer.errors}")
            right_to_draw_logs.info(f"Error Saving in Approver Template {log_str} -- Error is {serializer.errors}")        
            return None, serializer.errors
    except Exception as ex:
        right_to_draw_logs.error(f"An error occurred while saving approver template: {str(ex)}")
        right_to_draw_logs.info(f"An error occurred while saving approver template: {str(ex)}")
        return None, str(ex)
