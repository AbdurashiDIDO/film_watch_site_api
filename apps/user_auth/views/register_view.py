from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shared.utils.token_gen import account_activation_token
from apps.user_auth.serializers.register_serializer import RegisterSerializer
from apps.users.models.user import User
from apps.shared.utils.send_to_email import send_email


# from shared.utils.send_to_email import send_email


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        host = get_current_site(request).domain
        email = request.data['email']

        # send_email.delay(host, email, 'register')

        response_data = {
            'message': 'User registered successfully, check your email for activate your account!',
            'uidb64': urlsafe_base64_encode(force_bytes(str(user.pk))),
            'token': account_activation_token.make_token(user)
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class ActivateAccountView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(tags=['Account activate'])
    def post(self, request, *args, **kwargs):
        uid = kwargs['uidb64']
        token = kwargs['token']
        try:
            uuid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uuid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'success': 'Thank you for your email confirmation. Now you can login your account.'},
                            status.HTTP_200_OK)
        return Response({'user not found'},
                        status.HTTP_404_NOT_FOUND)
