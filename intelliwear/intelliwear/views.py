from rest_framework.response import Response
#from django.contrib.auth.models import User
from rest_framework import status ,permissions
from customerApi.serializers import UserSerializer,ChangePasswordSerializer,PasswordResetSerializer,LoginSerializer,PasswordResetConfirmSerializer, UserSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.utils import timezone
from zoneinfo import ZoneInfo


pkt = ZoneInfo("Asia/Karachi")

from drf_yasg.utils import swagger_auto_schema

User = get_user_model() 

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={201: UserSerializer(), 400: "Invalid data"}
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: "Login successful, redirecting...",
            400: "Invalid credentials"
        }
    )
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        # Authenticate using email (Ensure settings.py has correct AUTH_BACKENDS)
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)    
            user_data = UserSerializer(user).data  # Fixed user serialization

            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Use Django timezone
            access_token_expiry = timezone.now() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
            refresh_token_expiry = timezone.now() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]

            return Response({
                "token": {
                    "access_token": {
                        "token": str(access_token),
                        "expires_at": access_token_expiry.isoformat()
                    },
                    "refresh_token": {
                        "token": str(refresh),
                        "expires_at": refresh_token_expiry.isoformat()
                    }
                },
                "user_info": user_data
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: "Logged out successfully"}
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  
            logout(request)
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

    

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={200: "Password updated successfully", 400: "Invalid data"}
    )

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    
    @swagger_auto_schema(
        request_body=PasswordResetSerializer,
        responses={200: "Password reset email sent!", 400: "Invalid data"}
    )

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request=request)
            return Response({"message": "Password reset email sent!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]  # No authentication required
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]  # DRF HTML form support
    
    @swagger_auto_schema(
        request_body=PasswordResetConfirmSerializer,
        responses={200: "Password reset successful", 400: "Invalid token or data"},
        # manual_parameters=[
        #     openapi.Parameter('uidb64', openapi.IN_PATH, description="Base64 encoded User ID", type=openapi.TYPE_STRING),
        #     openapi.Parameter('token', openapi.IN_PATH, description="Password reset token", type=openapi.TYPE_STRING),
        # ]
    )

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = PasswordResetConfirmSerializer(data=request.data)
            if serializer.is_valid():
                user.set_password(serializer.validated_data["new_password"])
                user.save()
                return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
