from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("le-groupe/", views.about, name="about"),
    path("membres/", views.members_list, name="members"),
    path("membres/<int:pk>/", views.member_detail, name="member_detail"),
    path("albums/", views.albums_list, name="albums"),
    path("albums/<int:pk>/", views.album_detail, name="album_detail"),
    path("videos/", views.videos_list, name="videos"),
    path("dates/", views.events_list, name="events"),
    path("contact/", views.contact, name="contact"),
]
