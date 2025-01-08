from django.urls import path

from .views import ComponentDetailedAPIView,SectionGroupingsAPIView,SubCategoryTwoAPIView,CADDesignTemplatesAPIView

urlpatterns = [
    path('pcb-specification/<int:component_id>/', ComponentDetailedAPIView.as_view()),
    path("section-groupings/<int:sub_category_id>/", SectionGroupingsAPIView.as_view(), name="section-groupings"),
    path('sub-categories-two/<int:sub_category_id>/', SubCategoryTwoAPIView.as_view(), name='sub-categories-two'),
    path('cad_design-templates/<int:id>/', CADDesignTemplatesAPIView.as_view(), name='design-templates'),
    path('cad_design-templates/', CADDesignTemplatesAPIView.as_view(), name='design-templates'),
]