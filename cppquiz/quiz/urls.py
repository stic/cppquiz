from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView


from quiz import views

urlpatterns = patterns('',
    url(r'^quiz/question/(?P<question_id>.+)', views.question, name='question'),
    url(r'^quiz/clear', views.clear, name='clear'),
    url(r'^quiz/random', views.random_question, name='random'),
    url(r'^quiz/created', TemplateView.as_view(template_name = 'quiz/created.html')),
    url(r'^quiz/create', views.create, name='create'),
    url(r'^quiz/categorize', views.categorize, name='categorize'),
    url(r'^quiz/about', TemplateView.as_view(template_name = 'quiz/help.html')),
    url(r'^quiz/help', TemplateView.as_view(template_name = 'quiz/help.html')),
    url(r'^$', views.index, name='index'),
)
