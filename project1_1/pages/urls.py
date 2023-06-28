from django.urls import path
from . import views

urlpatterns = [
  path('',views.index,name='index')  ,
  path('download_sol',views.download_files,name='download_files')  ,
  path('download_sol2',views.download_files2,name='download_files2')  ,
    
]
