import random

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import mail_admins
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg

from models import Question, UsersAnswer
from forms import QuestionForm
from answer import Answer
from game_data import *

def index(request):
    return random_question(request)

def random_question(request):
    return HttpResponseRedirect(
    "/quiz/question/%d" % get_unanswered_question(UserData(request.session)))

def clear(request):
    user_data = UserData(request.session)
    request.session.clear()
    user_data.clear_correct_answers()
    save_user_data(user_data, request.session)
    return random_question(request)

@staff_member_required
def categorize(request):
    if request.method == 'POST':
        for key, value in request.POST.iteritems():
            if key.startswith('difficulty_'):
                pk = key.split('_')[1]
                q = Question.objects.get(pk=pk)
                q.difficulty = value
                anchor = "#question_%d" % q.pk
                q.save()
                return HttpResponseRedirect("/quiz/categorize/?changed=%d#question_%d" % (q.pk, q.pk))
    else:
        changed = int(request.REQUEST.get('changed', 0))
        questions = Question.objects.filter(published=True).order_by('difficulty')\
                    .annotate(num_answers=Count('usersanswer'))
        for q in questions:
            num_correct = len(UsersAnswer.objects.filter(question=q, correct=True))
            q.percentage_correct = num_correct * 100.0 / q.num_answers
        return render_to_response('quiz/categorize.html' ,
            {'questions': questions, 'changed':changed},
            context_instance=RequestContext(request)
            )

def create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            mail_admins('Someone made a question!', 'http://' + request.get_host() + '/admin/quiz/question/?published__exact=0')
            return HttpResponseRedirect('/quiz/created')
    else:
        form = QuestionForm()
    return render_to_response('quiz/create.html',
        {'form':form},
        context_instance=RequestContext(request)
        )

def preview(request, question_id):
    if not request.user.is_staff:
        raise Http404
    d = {}
    d['question'] = get_object_or_404(Question, id=question_id)
    return render_to_response('quiz/preview.html',
        d,
        context_instance=RequestContext(request)
        )

def question(request, question_id):
    if request.REQUEST.get('preview'):
        return preview(request, question_id)
    user_data = UserData(request.session)
    q = get_object_or_404(Question, id=question_id, published=True)
    d = {}
    d['answered'] = False
    d['question'] = q
    if request.REQUEST.get('did_answer'):
        d['answered'] = True
        answer = Answer(q, request)
        answer.register_given_answer()
        if answer.correct:
            d['correct_result'] = True
            user_data.register_correct_answer(question_id)
    d['total_questions'] = Question.objects.filter(published=True).count()
    d['user_data'] = user_data
    d['show_hint'] = request.REQUEST.get('show_hint', False)
    save_user_data(user_data, request.session)
    return render_to_response('quiz/index.html',
        d,
        context_instance=RequestContext(request)
        )

#TODO what if there are no questions
def get_unanswered_question(user_data):
    available_questions = [q.id for q in Question.objects.filter(published=True)]
    for q in user_data.get_correctly_answered_questions():
        if int(q) in available_questions:
            available_questions.remove(int(q))
    if len(available_questions) == 0:
        return Question.objects.filter(published=True).order_by('?')[0].id
    else:
        return random.choice(available_questions)
