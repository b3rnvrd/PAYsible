from django.urls import path


from . import views

app_name = 'paysible'


urlpatterns = [
    path('', views.index, name='index'),
]


