from django.urls import path
from . import views


urlpatterns = [
    path('courses/<int:course_id>/lesson/<int:lesson_order_num>/like/', views.press_like, name='press_like'),
    path('courses/<int:course_id>/lesson/<int:lesson_order_num>/add_comment/', views.add_comment, name='add_comment'),
    path('courses/<int:course_id>/lesson/<int:lesson_order_num>/comment/<int:comment_id>/reply-form/', views.get_reply_form, name='get_reply_form')
]