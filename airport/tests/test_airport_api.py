import tempfile
import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Order, Ticket
from airport.serializers import AirportSerializer, RouteSerializer, AirplaneSerializer, CrewSerializer, \
    FlightSerializer, OrderSerializer, TicketSerializer, AirplaneListSerializer, AirplaneRetrieveSerializer, \
    FlightListSerializer, FlightRetrieveSerializer
from airport.views import FlightViewSet

AIRPORT_URL = reverse("airport:airport-list")
ROUTE_URL = reverse("airport:route-list")
AIRPLANE_URL = reverse("airport:airplane-list")
FLIGHT_URL = reverse("airport:flight-list")
ORDER_URL = reverse("airport:order-list")
TICKET_URL = reverse("airport:ticket-list")

def sample_airport(**params):
    defaults = {
        "name": "Test Airport",
        "closest_big_city": "Test City",
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)

def sample_route(**params):
    source = sample_airport(name="Source Airport")
    destination = sample_airport(name="Destination Airport")
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 100,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)

def sample_airplane_type(**params):
    defaults = {
        "name": "Test Type",
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)

def sample_airplane(**params):
    airplane_type = sample_airplane_type()
    defaults = {
        "name": "Test Airplane",
        "rows": 10,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)

def sample_crew(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Doe",
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)

def sample_flight(**params):
    route = sample_route()
    airplane = sample_airplane()
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2023-01-01T10:00:00Z",
        "arrival_time": "2023-01-01T12:00:00Z",
    }
    defaults.update(params)
    flight = Flight.objects.create(**defaults)
    flight.crew.add(sample_crew())
    return flight

def sample_order(**params):
    user = get_user_model().objects.create_user("test@test.com", "password")
    defaults = {
        "user": user,
    }
    defaults.update(params)
    return Order.objects.create(**defaults)

def sample_ticket(**params):
    flight = sample_flight()
    order = sample_order()
    defaults = {
        "row": 1,
        "seat": 1,
        "flight": flight,
        "order": order,
    }
    defaults.update(params)
    return Ticket.objects.create(**defaults)

def create_airplane_with_type(name, airplane_type_name):
    airplane = sample_airplane(name=name)
    airplane_type = AirplaneType.objects.create(name=airplane_type_name)
    airplane.airplane_type = airplane_type
    airplane.save()
    return airplane

def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=(airplane_id,))


class UnauthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        urls = [AIRPORT_URL, ROUTE_URL, AIRPLANE_URL, FLIGHT_URL, ORDER_URL, TICKET_URL]
        for url in urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_airport(self):
        payload = {
            "name": "Unauthorized Airport",
            "closest_big_city": "Unauthorized City",
        }
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_flight(self):
        route = sample_route()
        airplane = sample_airplane()
        crew = sample_crew()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-01-01T10:00:00Z",
            "arrival_time": "2023-01-01T12:00:00Z",
            "crew": [crew.id],
        }
        res = self.client.post(FLIGHT_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order(self):
        flight = sample_flight()
        payload = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": flight.id},
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("testuser", "password")
        self.client.force_authenticate(self.user)

    def test_airplane_list(self):
        sample_airplane()

        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_airpanes_by_seats(self):
        airplane1 = sample_airplane(seats_in_row=4)
        airplane2 = sample_airplane(seats_in_row=5)
        airplane3 = sample_airplane(seats_in_row=6)

        res = self.client.get(AIRPLANE_URL,
                              {"seats_in_row": "4, 5"}
                              )

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)
        serializer3 = AirplaneListSerializer(airplane3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_airpanes_by_types(self):
        airplane1 = create_airplane_with_type("Airplane1", "Boing 123")
        airplane2 = create_airplane_with_type("Airplane2", "Boing 456")
        airplane3 = create_airplane_with_type("Airplane3", "Airbus")

        res = self.client.get(AIRPLANE_URL, {"airplane_type": "boing"})

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)
        serializer3 = AirplaneListSerializer(airplane3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_airplane_detail(self):
        airplane1 = create_airplane_with_type("Airplane1", "Boing 123")

        url = detail_url(airplane1.id)

        res = self.client.get(url)

        serializer = AirplaneRetrieveSerializer(airplane1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_fail(self):
        payload = {
            "name": "Test Airplane",
            "rows": 10,
            "seats_in_row": 6,
            "airplane_type": "Boing",
        }

        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_airport_fail(self):
        payload = {
            "name": "Authenticated Airport",
            "closest_big_city": "Authenticated City",
        }
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_flight_fail(self):
        route = sample_route()
        airplane = sample_airplane()
        crew = sample_crew()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-01-01T10:00:00Z",
            "arrival_time": "2023-01-01T12:00:00Z",
            "crew": [crew.id],
        }
        res = self.client.post(FLIGHT_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_ticket_fail(self):
        flight = sample_flight()
        order = sample_order(user=self.user)
        payload = {
            "row": 1,
            "seat": 1,
            "flight": flight.id,
            "order": order.id,
        }
        res = self.client.post(TICKET_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_flight_list(self):
        sample_flight()

        res = self.client.get(FLIGHT_URL)

        view = FlightViewSet()
        view.action = "list"
        view.request = self.client.request()
        flights = view.get_queryset()
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_order(self):
        flight = sample_flight()
        payload = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": flight.id},
                {"row": 1, "seat": 2, "flight": flight.id},
            ]
        }

        res = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data["id"])
        tickets = order.tickets.all()
        self.assertEqual(tickets.count(), 2)

class AdminApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("admin", "password", is_staff=True)
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        airplane_type = AirplaneType.objects.create(name="Boing")

        payload = {
            "name": "Test Airplane",
            "rows": 10,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id,
        }

        res = self.client.post(AIRPLANE_URL, payload)

        airplane = Airplane.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "airplane_type":
                self.assertEqual(payload[key], airplane.airplane_type.id)
            else:
                self.assertEqual(payload[key], getattr(airplane, key))

    def test_create_airport(self):
        payload = {
            "name": "New Airport",
            "closest_big_city": "New City",
        }

        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airport = Airport.objects.get(id=res.data["id"])
        self.assertEqual(airport.name, payload["name"])
        self.assertEqual(airport.closest_big_city, payload["closest_big_city"])

    def test_create_flight(self):
        route = sample_route()
        airplane = sample_airplane()
        crew = sample_crew()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-01-01T10:00:00Z",
            "arrival_time": "2023-01-01T12:00:00Z",
            "crew": [crew.id],
        }

        res = self.client.post(FLIGHT_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        flight = Flight.objects.get(id=res.data["id"])
        self.assertEqual(flight.route.id, payload["route"])
        self.assertEqual(flight.airplane.id, payload["airplane"])

    def test_update_airport(self):
        airport = sample_airport()
        payload = {
            "name": "Updated Airport",
            "closest_big_city": "Updated City",
        }
        url = reverse("airport:airport-detail", args=(airport.id,))
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        airport.refresh_from_db()
        self.assertEqual(airport.name, payload["name"])
        self.assertEqual(airport.closest_big_city, payload["closest_big_city"])

    def test_delete_airport(self):
        airport = sample_airport()
        url = reverse("airport:airport-detail", args=(airport.id,))
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Airport.objects.filter(id=airport.id).exists())

    def test_update_flight(self):
        flight = sample_flight()
        new_route = sample_route()
        payload = {
            "route": new_route.id,
            "airplane": flight.airplane.id,
            "departure_time": "2023-01-01T10:00:00Z",
            "arrival_time": "2023-01-01T12:00:00Z",
            "crew": [crew.id for crew in flight.crew.all()],
        }
        url = reverse("airport:flight-detail", args=(flight.id,))
        res = self.client.put(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        flight.refresh_from_db()
        self.assertEqual(flight.route.id, new_route.id)

    def test_delete_flight(self):
        flight = sample_flight()
        url = reverse("airport:flight-detail", args=(flight.id,))
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Flight.objects.filter(id=flight.id).exists())
