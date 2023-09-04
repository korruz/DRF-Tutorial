from django.urls import path, include
from rest_framework.routers import DefaultRouter

from course import views

router = DefaultRouter()
router.register('viewsets', views.CourseViewSet)

urlpatterns = [
    # Function Based View
    path('fbv/list', views.course_list, name='fbv-list'),
    path('fbv/detail/<int:pk>', views.course_detail, name='fbv-detail'),

    # Class Based View
    path('cbv/list', views.CourseList.as_view(), name='cbv-list'),
    path('cbv/detail/<int:pk>', views.CourseDetail.as_view(), name='cbv-detail'),

    # Generic Class Based View
    path('gcbv/list', views.GCourseList.as_view(), name='gcbv-list'),
    path('gcbv/detail/<int:pk>', views.GCourseDetail.as_view(), name='gcbv-detail'),

    # DRF viewsets
    # path('viewsets/list', views.CourseViewSet.as_view({'get': 'list'}), name='viewsets-list'),
    # path('viewsets/detail/<int:pk>', views.CourseViewSet.as_view({'get': 'retrieve'}), name='viewsets-detail'),
    path("", include(router.urls)),
]
