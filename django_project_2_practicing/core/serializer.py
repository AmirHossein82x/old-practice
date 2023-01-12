from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserCreateSerializer, User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class CustomUserCreateSerializer(UserCreateSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta(UserCreateSerializer.Meta):
        fields = ['id', 'username', 'email', 'password', 'password2', 'first_name', 'last_name']

    def validate(self, attrs):
        password2 = attrs.pop('password2')
        user = User(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
            if password != password2:
                raise serializers.ValidationError(
                    {'password you entered are not match'}
                )
        except ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs