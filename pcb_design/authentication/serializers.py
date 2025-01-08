from rest_framework import serializers
from django.contrib.auth.models import Group

from .models import CustomUser
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

valid_roles = ['Admin', 'CADesigner', 'Approver', 'Verifier']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['id','email', 'password']
    
    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

 
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
  
    class Meta:
        model = CustomUser
        fields = ( 'password', 'password2', 'email')
  
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
        )

        
        user.set_password(validated_data['password'])
        role = self.context.get('role', 'CADesigner')
        print("vinod role is ", role)
        if role not in valid_roles:
            role = 'CADesigner'
        group, created = Group.objects.get_or_create(name=role)

        # Assign the user to the group
        user.groups.add(group)
        user.save()
        
        return user