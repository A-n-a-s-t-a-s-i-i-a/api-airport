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


class FlightRetrieveSerializer(FlightSerializer):
    route = RouteListSerializer()
    airplane = AirplaneSerializer()
    crew = CrewSerializer(many=True)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer()
    order = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="id",
    )


class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightRetrieveSerializer()
    order = OrderSerializer()

