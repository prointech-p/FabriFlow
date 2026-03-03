from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [

    path("", views.dashboard, name="dashboard"),
    path("details/", views.detail_list, name="details"),
        # Для карточки детали
    path('details/<int:pk>/', views.detail_detail, name='detail_detail'),
    path('details/<int:pk>/recalculate/', views.detail_recalculate, name='detail_recalculate'),
    path('details/<int:pk>/stage/<int:stage_id>/complete/', views.stage_complete, name='stage_complete'),
    path('api/detail/<int:pk>/', views.detail_api, name='detail_api'),
    # path(
    #     "details/<int:id>/",
    #     views.detail_card,
    #     name="detail_card"
    # ),
    path(
        "machines/",
        views.machine_list,
        name="machines"
    ),
    path(
        "stages/",
        views.stage_list,
        name="stages"
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