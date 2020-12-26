"""Resotres views"""

# DRF
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Documentation
from drf_yasg.utils import swagger_auto_schema

# Permissions
from rest_framework.permissions import IsAuthenticated

# Serializers
from users.serializers import RestorePasswordSerializer


class RestorePasswordAPIView(APIView):
    """Restore password view
    
    Handle secure update of the password.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(auto_schema = None)
    def post(self, request, format=None):
        auth_user = request.user
        serializer = RestorePasswordSerializer(data = request.data)

        if serializer.is_valid():
            new_password = request.data.get("new_password")
            auth_user.set_password(new_password)
            auth_user.save()

            return Response(
                {"detail": "password updated"}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        