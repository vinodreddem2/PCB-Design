from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MstComponent
from right_to_draw.serializers import ComponentSerializer
from authentication.custom_permissions import IsAuthorized
from authentication.custom_authentication import CustomJWTAuthentication


class Components(APIView):
    permission_classes = [IsAuthorized]
    authentication_classes = [CustomJWTAuthentication]
    def get(self, request,*args, **kwargs):
        
        component_id = self.kwargs.get('component_id', None)
        
        if component_id:
            try:
                component = MstComponent.objects.get(id = component_id)
                serializer = ComponentSerializer(component)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except MstComponent.DoesNotExist as e:
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        component = MstComponent.objects.all()
        serializer = ComponentSerializer(component, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)