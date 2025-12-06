from django.urls import path
from . import views
from .views import hello
from .views import signup, login

urlpatterns = [
     path('hello/', hello),
     path("signup/", signup),
     path("login/", login),
     path("events/", views.get_events),
    path("register-event/", views.register_event),
    path("my-registrations/", views.my_registrations),
    path("my-activity/", views.my_activity),
    path("winners/", views.get_winners),
  
    path("examiner-login/", views.examiner_login),
    path("examiner-event/", views.examiner_event),
    path("examiner-participants/", views.examiner_participants),
    path("examiner-submit-score/", views.examiner_submit_score),

   path("admin/login-jwt/", views.admin_login_jwt),
    path("admin/check-jwt/", views.admin_check_jwt),



    path("admin/users/", views.users_list_create),
    path("admin/users/<str:rollno>/", views.user_detail),

    # EVENTS
    path("admin/events/", views.events_list_create),
    path("admin/events/<str:event_id>/", views.event_detail),

    # REGISTRATIONS
    path("admin/registrations/", views.registrations_list_create),
    path("admin/registrations/<str:reg_id>/", views.registration_detail),

    # EXAMINERS
    path("admin/examiners/", views.examiners_list_create),
    path("admin/examiners/<str:examiner_id>/", views.examiner_detail),

    # WINNERS
    path("admin/winners/", views.winners_list_create),
    path("admin/winners/<str:winner_id>/", views.winner_detail),

    # ADMIN ACCOUNTS
    path("admin/admins/", views.admins_list_create),
    path("admin/admins/<str:username>/", views.admin_detail),
    
   path("verify-otp/", views.verify_otp, name="verify-otp"),
]
