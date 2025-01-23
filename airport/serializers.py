from django.db import transaction
from rest_framework import serializers

from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Order, Ticket


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )
    destination = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )


class RouteRetrieveSerializer(RouteSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = "__all__"


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = "__all__"


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer()


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = "__all__"


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class FlightListSerializer(FlightSerializer):
    route = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="from_to",
    )
    airplane = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name",
    )
    crew = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name",
    )
    num_seats = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="number_of_seats",
        source="airplane"
    )
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane",
                  "departure_time", "arrival_time",
                  "crew", "num_seats", "available_seats")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_row_seat(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane.rows,
            attrs["flight"].airplane.seats_in_row,
            serializers.ValidationError
        )
        return data


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer()


class FlightRetrieveSerializer(FlightSerializer):
    route = RouteListSerializer()
    airplane = AirplaneSerializer()
    crew = CrewSerializer(many=True)
    taken_seats = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="row_seat",
        source="ticket_set"
    )

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew", "taken_seats")


class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightRetrieveSerializer()

class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order