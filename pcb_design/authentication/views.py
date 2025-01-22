from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status

from .custom_permissions import IsAuthorized
from .serializers import RegisterSerializer


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
        print('Inside teh Log in View Post')
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)                
        if user:                
            user_role = user.role
            user.is_logged_out = False
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': user_role,
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
