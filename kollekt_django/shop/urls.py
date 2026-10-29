from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("offres/<slug:slug>/rejoindre/", views.join_product, name="join_product"),
    path("mes-commandes/", views.my_orders, name="my_orders"),

    path("connexion/", views.SiteLoginView.as_view(), name="login"),
    path("inscription/", views.register, name="register"),
    path("deconnexion/", LogoutView.as_view(), name="logout"),

    path("gestion/", views.dashboard, name="dashboard"),
    path("gestion/commandes/<int:pk>/statut/", views.order_set_status, name="order_set_status"),
    path("gestion/<slug:tab>/", views.dashboard, name="dashboard_tab"),
]
