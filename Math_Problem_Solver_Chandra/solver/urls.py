from django.urls import path
from . import views

app_name = 'solver'

urlpatterns = [
    path('', views.index, name='index'),
    path('health/', views.health_check, name='health'),
    path('solve/', views.solve_problem, name='solve'),
    path('process-image/', views.process_image, name='process_image'),
]
