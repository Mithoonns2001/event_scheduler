from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register', views.register),
    path('login', views.login),
    # path('employee_dashboard', views.employee_dashboard),
    path('logout', views.logout, name='logout'),
    # path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('user/<int:user_id>/events_list/', views.events_list_user, name='events_list_user'),  
    path('user/<int:user_id>/event/<int:event_id>/vote/', views.vote_date_user, name='vote_date_user'),  

    path('head/events_list', views.events_list_head, name='events_list'),
    path('head/schedule/', views.schedule_event, name='schedule_event'),

    path('head/admin_registration/', views.admin_register, name='admin_register'),

    path('head/<int:event_id>/edit/', views.edit_event, name='edit_event'),  # New URL pattern for editing events
    path('head/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('head/<int:event_id>/vote/', views.vote_date, name='vote_date'),
    path('notification/', views.notification_view, name='notification'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)