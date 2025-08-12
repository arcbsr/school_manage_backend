from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BranchViewSet, ShiftViewSet, SchoolClassViewSet, SectionViewSet, SubjectViewSet


router = DefaultRouter()
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'classes', SchoolClassViewSet, basename='class')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'subjects', SubjectViewSet, basename='subject')

urlpatterns = [
    path('', include(router.urls)),
]


