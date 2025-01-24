from django.db.models import Count, F
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Order, Ticket, Flight
from airport.permissions import IsAdminAllOrIsAuthenticatedReadOnly
from airport.serializers import (AirportSerializer, RouteSerializer,
                                 AirplaneTypeSerializer, AirplaneSerializer,
                                 CrewSerializer, OrderSerializer,
                                 TicketSerializer, FlightSerializer,
                                 RouteListSerializer, AirplaneListSerializer,
                                 FlightListSerializer, TicketListSerializer, RouteRetrieveSerializer,
                                 AirplaneRetrieveSerializer, FlightRetrieveSerializer, TicketRetrieveSerializer)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)



class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return self.queryset.select_related()
        return self.queryset


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset

        airplane_type = self.request.query_params.get("airplane_type")
        seats_in_row = self.request.query_params.get("seats_in_row")

        if airplane_type:
            queryset = queryset.filter(airplane_type__name__icontains=airplane_type)

        if seats_in_row:
            seats = self._params_to_ints(seats_in_row)
            queryset = queryset.filter(seats_in_row__in=seats)

        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related()

        return queryset.distinct()


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return (self.queryset.prefetch_related("crew")
                    .annotate(available_seats=F("airplane__rows") *F("airplane__seats_in_row") - Count("ticket")))
        return self.queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "retrieve":
            return TicketRetrieveSerializer
        return TicketSerializer

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return self.queryset.select_related()

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Tickets cannot be created directly. Use the Order endpoint."},
            status=status.HTTP_400_BAD_REQUEST
        )

