from datetime import timedelta, timezone
from django.db import IntegrityError
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer, FriendRequestSerializer
from .models import FriendRequest
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password

# Create your views here.


User = get_user_model()

class SignupView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create(
                email=email,
                username=username,
                password=make_password(password)
            )
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

    

class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100    

class SearchUserView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('query', '').strip().lower()
        if '@' in query:
            return User.objects.filter(email__iexact=query)
        return User.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(username__icontains=query))
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  

class FriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        if not receiver_id:
            return Response({"error": "Receiver ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        receiver = User.objects.filter(id=receiver_id).first()
        if not receiver:
            return Response({"error": "Receiver not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check rate limit
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(sender=request.user, created_at__gte=one_minute_ago).count()
        if recent_requests >= 3:
            return Response({"error": "Rate limit exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        friend_request, created = FriendRequest.objects.get_or_create(sender=request.user, receiver=receiver)
        if not created:
            return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        friend_request = FriendRequest.objects.filter(id=pk, receiver=request.user, status='pending').first()
        if not friend_request:
            return Response({"error": "Friend request not found or already processed"}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'accept':
            friend_request.status = 'accepted'
        elif action == 'reject':
            friend_request.status = 'rejected'
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.save()
        return Response(FriendRequestSerializer(friend_request).data)

class FriendListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        friends = FriendRequest.objects.filter(Q(sender=self.request.user, status='accepted') | Q(receiver=self.request.user, status='accepted'))
        friend_ids = [fr.sender.id if fr.receiver == self.request.user else fr.receiver.id for fr in friends]
        return User.objects.filter(id__in=friend_ids)

class PendingFriendRequestView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(receiver=self.request.user, status='pending')




class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '').strip()

        user = authenticate(request, username=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
