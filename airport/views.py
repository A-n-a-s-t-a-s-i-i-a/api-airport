from rest_framework import viewsets

from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Order, Ticket, Flight
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


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()

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


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return AirplaneSerializer

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return self.queryset.select_related()
        return self.queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return self.queryset.prefetch_related("crew")
        return self.queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "retrieve":
            return TicketRetrieveSerializer
        return TicketSerializer

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return self.queryset.select_related()
        return self.queryset


