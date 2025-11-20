from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination 
from .models import ZendeskProfile
from .serializers import ZendeskProfileSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class LinkZendeskUserView(APIView):
    """
    POST /api/zendesk/link/
    Allows:
      - Admin: link a Zendesk profile to any user (pass user_id)
      - Normal user: link to self (omit user_id)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ZendeskProfileSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Determine the user to link
        if "user_id" in data:
            if not request.user.is_staff:
                return Response({"detail": "You are not allowed to link other users."},
                                status=status.HTTP_403_FORBIDDEN)
            target_user = User.objects.get(id=data["user_id"])
        else:
            target_user = request.user

        # Create or update profile
        profile, created = ZendeskProfile.objects.get_or_create(
            user=target_user,
            defaults={
                "employee_id": data["employee_id"],
                "role": data.get("role", "Agent"),
                "country": data["country"],
            }
        )

        if not created:
            profile.employee_id = data["employee_id"]
            profile.role = data.get("role", profile.role)
            profile.country = data["country"]
            profile.save(update_fields=["employee_id", "role", "country"])

        out_serializer = ZendeskProfileSerializer(profile, context={"request": request})
        return Response(out_serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ZendeskProfileListView(APIView):
    """
    GET /api/zendesk/profiles/
    - Admin: lists all linked Zendesk profiles
    - Normal users: lists only their own profile
    Supports pagination and optional filtering by employee_id or country
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        # Admin: list all profiles
        if request.user.is_staff:
            qs = ZendeskProfile.objects.select_related("user").all()
        else:
            # Normal user: only their own profile
            qs = ZendeskProfile.objects.select_related("user").filter(user=request.user)

        # Optional filters
        employee_id = request.query_params.get("employee_id")
        country = request.query_params.get("country")
        if employee_id:
            qs = qs.filter(employee_id__iexact=employee_id)
        if country:
            qs = qs.filter(country__iexact=country)

        # Pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request, view=self)
        serializer = ZendeskProfileSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)
