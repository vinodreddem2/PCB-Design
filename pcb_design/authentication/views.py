from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from .custom_permissions import IsAuthorized
from .serializers import RegisterSerializer
from .services import reset_user_password, get_users, update_user, delete_user


class UserRegistrationView(APIView):
    permission_classes = [IsAuthorized]
    def post(self, request):
        print(request.data)
        role = request.data.get('role', 'CADesigner')
        serializer = RegisterSerializer(data=request.data, context={'role': role})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [] 
    authentication_classes = [] 

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)                
        if user:                
            # Retrieve the user's group names (roles)
            user_roles = [group.name for group in user.groups.all()]
            user.is_logged_out = False
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': user_roles,
                'full_name': user.full_name
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        try:             
            user = request.user            
            user.is_logged_out = True
            user.save()            
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class ForgetPasswordView(APIView):

    def post(self,request):
        try:
            
            data= request.data
            
            response = reset_user_password(data)            
            return Response(response.data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({"error": f"Validation Error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({"error": f"User Not Found: {e}"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Exception occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserAPIView(APIView):
    def get(self, request):
        try:
            response = get_users()
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Exception occurred While Getting the Users: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
    
    def put(self, request, pk):
        try:
            response = update_user(request.data,pk)
            return Response(response, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({"error": f"User Not Found: {e}"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": f"Validation Error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Exception occurred While Updating the User: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, pk):
        try:    
            response = delete_user(pk)
            return Response(response)
        except NotFound as e:
            return Response({"error": f"User Not Found: {e}"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Exception occurred While Deleting the User: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)