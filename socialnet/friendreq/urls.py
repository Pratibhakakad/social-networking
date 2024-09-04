from django.urls import path
from .views import SignupView, SearchUserView, FriendRequestView, FriendListView, PendingFriendRequestView, LoginView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('search/', SearchUserView.as_view(), name='search_users'),
    path('friend-request/', FriendRequestView.as_view(), name='friend_request'),
    path('friend-request/<int:pk>/', FriendRequestView.as_view(), name='friend_request_action'),
    path('friends/', FriendListView.as_view(), name='friend_list'),
    path('pending-requests/', PendingFriendRequestView.as_view(), name='pending_requests'),
    path('login/', LoginView.as_view(), name='login'),
]
