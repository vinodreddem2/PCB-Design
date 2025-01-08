from django.http import Http404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from authentication.custom_permissions import IsAuthorized
from authentication.custom_authentication import CustomJWTAuthentication
from .models import CADDesignTemplates
from .services import get_categories_for_component_id,get_section_groupings_for_subcategory_id, \
    get_sub_categories_two_for_subcategory_id, create_cad_template
from drf_yasg.utils import swagger_auto_schema
from .serializers import CADDesignTemplatesSerializer


class ComponentDetailedAPIView(APIView):
    permission_classes = [IsAuthorized]
    authentication_classes = [CustomJWTAuthentication]
    
    def get(self, request, component_id):
        print(component_id)
        
        try:            
            response = get_categories_for_component_id(component_id)            
            return Response(response, status=status.HTTP_200_OK) 
        
        except Http404 as e:            
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": f"Exception Occurred {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SectionGroupingsAPIView(APIView):
    permission_classes = [IsAuthorized]
    authentication_classes = [CustomJWTAuthentication]
    def get(self, request, sub_category_id):
        try:
            response = get_section_groupings_for_subcategory_id(sub_category_id)
            return Response(response.data, status=status.HTTP_200_OK)
        except Http404 as e:            
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubCategoryTwoAPIView(APIView):
    permission_classes = [IsAuthorized]
    authentication_classes = [CustomJWTAuthentication]
    def get(self, request, sub_category_id):
        try:
            response =  get_sub_categories_two_for_subcategory_id(sub_category_id)
            return Response(response.data, status=status.HTTP_200_OK)
        except Http404 as e:            
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CADDesignTemplatesAPIView(APIView):
    permission_classes = [IsAuthorized]
    authentication_classes = [CustomJWTAuthentication]
    
    def get(self, request, *args, **kwargs):        
        cad_template_id = request.query_params.get('id', None)

        if cad_template_id:
            try:                
                cad_template = CADDesignTemplates.objects.get(id=cad_template_id)                
                serializer = CADDesignTemplatesSerializer(cad_template)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CADDesignTemplates.DoesNotExist:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        else:            
            cad_templates = CADDesignTemplates.objects.all()            
            serializer = CADDesignTemplatesSerializer(cad_templates, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'oppNumber': openapi.Schema(type=openapi.TYPE_STRING, description='Opportunity Number'),
                'opuNumber': openapi.Schema(type=openapi.TYPE_STRING, description='Opu Number'),
                'eduNumber': openapi.Schema(type=openapi.TYPE_STRING, description='Education Number'),
                'modelName': openapi.Schema(type=openapi.TYPE_STRING, description='Model Name'),
                'partNumber': openapi.Schema(type=openapi.TYPE_STRING, description='Part Number'),
                'revisionNumber': openapi.Schema(type=openapi.TYPE_STRING, description='Revision Number'),
                'component': openapi.Schema(type=openapi.TYPE_INTEGER, description='Component ID (e.g., b14)'),
                'componentSpecifications': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(type=openapi.TYPE_STRING, description="Dynamic specification fields")
                ),
                'designOptions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description='Design options (array of strings)'
                )
            },
            required=['oppNumber', 'opuNumber', 'modelName', 'partNumber', 'component'],
        ),
        responses={201: 'Template Created', 400: 'Bad Request'}
    )
    def post(self, request):
        user = request.user
        template, error = create_cad_template(request.data, user)        
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(template.id, status=status.HTTP_201_CREATED)
