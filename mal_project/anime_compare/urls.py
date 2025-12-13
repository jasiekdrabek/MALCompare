from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('mal/login/', views.mal_login, name='mal_login'),
    path('mal/callback/', views.mal_callback, name='mal_callback'),
    path('fetch/<str:username>/save/', views.fetch_and_save, name='fetch_and_save'),
    path("compare/", views.compare_form, name="compare_form"),
    path("compare/run/", views.compare_users, name="compare_users"),
    path(
    "compare/run/<str:user_a>/<str:user_b>/",
    views.compare_users_direct,
    name="compare_users_direct"
    ),
    path(
    "compare/partial/<str:table_type>/",
    views.compare_table_partial,
    name="compare_table_partial",
    )
]
