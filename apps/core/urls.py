from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard"
    ),
    path(
        "details/",
        views.detail_list,
        name="details"
    ),
    path(
        "details/<int:id>/",
        views.detail_card,
        name="detail_card"
    ),
    path(
        "machines/",
        views.machine_list,
        name="machines"
    ),
    # Аутентификация
    path('login/', auth_views.LoginView.as_view(
        template_name='base/login.html',
        next_page='/'
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/login/'
    ), name='logout'),
]