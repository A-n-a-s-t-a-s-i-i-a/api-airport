from django.conf import settings
from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departure_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="arrival_routes"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} -> {self.destination}"

    @property
    def from_to(self):
        return f"{self.source} -> {self.destination}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def number_of_seats(self):
        return self.seats_in_row * self.rows


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    def __str__(self):
        return f"Flight on {self.departure_time} from {self.route.source} to {self.route.destination}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.id} by {self.user}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        unique_together = ("row", "seat", "flight")

    def __str__(self):
        return f"Ticket {self.row}-{self.seat} on flight {self.flight}"

    @property
    def row_seat(self):
        return f"row:{self.row}-seat:{self.seat}"

    @staticmethod
    def validate_row_seat(row: int, seat: int, rows: int,
                          seats_in_row: int, error_to_raise):
        if not (1 <= row <= rows):
            raise error_to_raise(f"row must be in range (1, {rows})")
        if not (1 <= seat <= seats_in_row):
            raise error_to_raise(f"seat must be in range (1, {seats_in_row})")

    def clean(self):
        Ticket.validate_row_seat(self.row, self.seat,
                                 self.flight.airplane.rows,
                                 self.flight.airplane.seats_in_row,
                                 ValueError)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)