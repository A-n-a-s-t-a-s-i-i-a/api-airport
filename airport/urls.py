from django.urls import include, path
from rest_framework import routers

from airport import views

app_name = "airport"

router = routers.DefaultRouter()
router.register("airports", views.AirportViewSet)
router.register("routes", views.RouteViewSet)
router.register("airplane_types", views.AirplaneTypeViewSet)
router.register("airplanes", views.AirplaneViewSet)
router.register("crews", views.CrewViewSet)
router.register("flights", views.FlightViewSet)
router.register("orders", views.OrderViewSet)
router.register("tickets", views.TicketViewSet)


urlpatterns = [
    path("", include(router.urls)),
]