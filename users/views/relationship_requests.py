"""Relationship request view"""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Django
from django.db import transaction
from django.db.models import Q

# Models
from users.models import User, Relationship, RelationshipRequest

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from users.permissions import UserIsVerified, IsRelationRequester, IsRelationAddressed, IsActiveClient

# Serializers
from users.serializers import (
    RelationshipRequestModelSerializer, 
    CreateRelationshipRequestSerializer, 
    RelationshipModelSerializer, 
    CreateRelationshipSerializer
)

# Errors
from django.db.utils import IntegrityError


class SentRelationshipRequestViewSet(mixins.ListModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """Relationship request viewset that was sent by the requester user"""

    serializer_class = RelationshipRequestModelSerializer

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list', 'retrieve']:
            permissions = [IsAuthenticated]
        else:
            permissions = [IsAuthenticated, IsRelationRequester]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return user relationship requests sent by him"""
        relationship_requests = RelationshipRequest.objects.filter(
            requester = self.request.user
        )

        return relationship_requests

    def get_object(self):
        """Return the sent relationship request by the id"""
        relationship_request = get_object_or_404(
            RelationshipRequest,
            id = self.kwargs['pk'],
            requester = self.request.user
        )

        return relationship_request


class RecievedRelationshipRequestViewSet(mixins.ListModelMixin,
                                    mixins.UpdateModelMixin,
                                    mixins.RetrieveModelMixin,
                                    viewsets.GenericViewSet):
    """Relationship request viewset that was recieved to the request user"""

    serializer_class = RelationshipRequestModelSerializer

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list', 'retrieve']:
            permissions = [IsAuthenticated]
        else:
            permissions = [IsAuthenticated, IsRelationAddressed, IsActiveClient]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return user relationship requests the he recieved"""
        blocked = self.request.query_params.get('blocked')
        blocked = self.str_to_bool(blocked) if blocked else None

        if type(blocked) is bool:
            relationship_requests = RelationshipRequest.objects.filter(
                addressed = self.request.user,
                blocked = blocked
            )
        else:
            relationship_requests = RelationshipRequest.objects.filter(
                addressed = self.request.user
            )

        return relationship_requests

    def str_to_bool(self, str):
        if str.lower() == "false":
            return False
        elif str.lower() == "true":
            return True
        
        return None

    def get_object(self):
        """Return the recieved relationship request by the id"""
        relationship_request = get_object_or_404(
            RelationshipRequest,
            id = self.kwargs['pk'],
            addressed = self.request.user
        )

        return relationship_request

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """Accept or deny relationship request"""
        action = request.query_params.get('action')

        if action:
            instance = self.get_object()

            if action == "accept":
                return self.accept(
                    relationship_type = request.data.get("type"),
                    relationship_request = instance
                )
            elif action == "deny":
                return self.deny(relationship_request = instance)
            else:
                return Response( 
                    {"message": "the action param have to be accept or deny"}, 
                    status = status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response( {"message": "the update need the <<action>> query param"}, status = status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def accept(self, relationship_type, relationship_request):
        """Accept the relationship_request.
        Delete the relationship_request and create a relationship."""
        
        relationship_serializer = CreateRelationshipSerializer(
            data = {"type": relationship_type} if relationship_type else {},
            context = {'requester': relationship_request.requester, 'addressed': relationship_request.addressed}
        )

        relationship_serializer.is_valid(raise_exception = True)

        try:
            relationship = relationship_serializer.save()
            data = RelationshipModelSerializer(relationship).data
            data_status = status.HTTP_201_CREATED
            
            relationship_request.delete()
        except IntegrityError:
            data = {
                'detail': 'Error. This relationship alredy exist.'
            }
            data_status = status.HTTP_409_CONFLICT
        
        return Response(data, status = data_status)

    @transaction.atomic
    def deny(self, relationship_request):
        """Deny the relationship_request"""
        relationship_request_serializer = RelationshipRequestModelSerializer(
            instance = relationship_request,
            data = {"blocked": True},
            partial = True
        )
        relationship_request_serializer.is_valid(raise_exception = True)
        relationship_res = relationship_request_serializer.save()

        data = self.get_serializer(relationship_res).data

        return Response(data, status.HTTP_200_OK)

    
class RelationshipRequestViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                viewsets.GenericViewSet):
    """
    Relationship request viewset to send a relationship request 
    to a target_user or to administrate relationship request for 
    an external user (user that's not the target)"""

    serializer_class = RelationshipRequestModelSerializer
    target_user = None

    def dispatch(self, request, *args, **kwargs):
        """Verify that the user exists"""
        target_user_id = kwargs['target_user_id']
        self.target_user = get_object_or_404(User, id = target_user_id)

        return super(RelationshipRequestViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['create']:
            permissions = [IsAuthenticated, IsActiveClient]
        else:
            permissions = [IsAdminUser]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return user relationship requests the he recieved"""
        relationship_requests = RelationshipRequest.objects.filter(
            addressed = self.target_user
        )

        return relationship_requests

    def get_object(self):
        """Return the recieved relationship request by the id"""
        relationship_request = get_object_or_404(
            RelationshipRequest,
            id = self.kwargs['pk'],
            addressed = self.target_user
        )

        return relationship_request

    def create(self, request, *args, **kwargs):
        """Handle relationship request creation."""
        relationship_request_validation = RelationshipRequest.objects.filter(
            ( Q(requester = request.user) & Q(addressed = self.target_user) ) | ( Q(requester = self.target_user) & Q(addressed = request.user) )
        )
        relationship_validation = Relationship.objects.filter(
            ( Q(requester = request.user) & Q(addressed = self.target_user) ) | ( Q(requester = self.target_user) & Q(addressed = request.user) )
        )

        if relationship_request_validation:
            return Response({"detail": "The relationship alredy have a pending request"}, status.HTTP_409_CONFLICT)
        elif  relationship_validation:
            return Response({"detail": "The relationship alredy exists"}, status.HTTP_409_CONFLICT)

        relationship_request_serializer = CreateRelationshipRequestSerializer(
            data = request.data,
            context = {'requester': request.user, 'addressed': self.target_user}
        )

        relationship_request_serializer.is_valid(raise_exception = True)
        relationship_request = relationship_request_serializer.save()

        data = self.get_serializer(relationship_request).data
        data_status = status.HTTP_201_CREATED

        return Response(data, status = data_status)