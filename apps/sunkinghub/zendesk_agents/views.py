from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ZendeskProfile
from .serializers import ZendeskProfileSerializer

class LinkZendeskUserView(APIView):
    """
    POST /api/zendesk/link/
    Body: { "employee_id": "...", "role": "...", "country": "..." }
    uses JWT-authenticated user (SimpleJWT) and link to zendesk profile
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        employee_id = request.data.get("employee_id")
        role = request.data.get("role")
        country = request.data.get("country")
        
        if not employee_id or not country:
            return Response({"detail": "employee_id and country are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        profile, created = ZendeskProfile.objects.get_or_create(
            user=user,
            defaults={"employee_id": employee_id, "role": role, "country": country}
        )
        
        if not created:
            profile.employee_id = employee_id
            profile.role = role
            profile.country = country
            
        serializer = ZendeskProfileSerializer(profile)
        
        return Response({"status": "Linked"}, serializer.data)
        
        