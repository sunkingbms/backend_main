from django.urls import path
from .views import RoleListView, RoleDetailView, PermissionListView, assign_user_roles, user_roles

urlpatterns = [
    path('roles/', RoleListView.as_view(), name='role-list'),
    path('roles/<uuid:pk>/', RoleDetailView.as_view(), name='role-detail'),
    path('permissions/', PermissionListView.as_view(), name='permissions-list'),
    path('users/<uuid:user_id>/roles/', user_roles, name='user-roles'),
    path('users/<uuid:user_id>/roles/assign/', assign_user_roles, name='assign-user-role')
]