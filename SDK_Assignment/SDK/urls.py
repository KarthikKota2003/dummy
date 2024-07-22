from django.urls import path
from .views import Text_To_Speech,Record_Audio,Convert_to_Text,QueryLLM

urlpatterns = [
    path('play', Text_To_Speech.as_view(), name='play'),
    path('record', Record_Audio.as_view(), name='record'),
    path('convert', Convert_to_Text.as_view(), name='convert'),
    path('query', QueryLLM.as_view(), name='query'),
]
