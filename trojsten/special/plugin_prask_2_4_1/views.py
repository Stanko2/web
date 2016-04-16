# coding=utf-8
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse
from django.db.models import Max

from trojsten.tasks.models import Task, Submit

from .tester import process_question, process_answer, POCET_PRVKOV
from .forms import SubmitForm


TASK_ID = 1173


@login_required
def task_view(request):
    task = get_object_or_404(Task, pk=TASK_ID)
    best_points = Submit.objects.filter(user=request.user, task=task).aggregate(Max('points'))
    if request.method == 'POST':
        form = SubmitForm(request.POST)
        if form.is_valid():
            queries = request.session.get('plugin_prask_2_4_1/questions', list())
            selection = form.cleaned_data['selection']
            points, message = process_answer(queries, selection)
            if points:
                if points > best_points:
                    submit = Submit(
                        task=task,
                        user=request.user,
                        points=points,
                        submit_type=Submit.EXTERNAL,
                        filepath="",
                        testing_status="OK",
                        tester_response="",
                        protocol_id="",
                    )
                    submit.save()
                pass  # @TODO: Submit!
                request.session['plugin_prask_2_4_1/best_points'] = best_points
                request.session['plugin_prask_2_4_1/last_points'] = points
            messages.add_message(request, messages.SUCCESS if points else messages.ERROR, message)
            return redirect(reverse('plugin_prask_2_4_1:task_view'))
    else:
        form = SubmitForm()

    context = dict(
        task=task,
        form=form,
        last_points=request.session.get('plugin_prask_2_4_1/last_points', 0),
        best_points=request.session.get('plugin_prask_2_4_1/best_points', 0),
    )
    return render(request, 'plugin_prask_2_4_1/task_view.html', context=context)


@login_required
def answer_query(request):
    data = dict()
    queries = request.session.get('plugin_prask_2_4_1/questions', list())
    if request.method == 'DELETE':
        queries = list()
        request.session['plugin_prask_2_4_1/questions'] = queries
        data['status'] = 'Success'
        data['queries'] = queries
        return JsonResponse(data)
    if request.method == 'GET':
        data['status'] = 'Success'
        data['queries'] = queries
        return JsonResponse(data)
    if request.method != 'POST':
        data['status'] = 'Error'
        data['message'] = 'Invalid method'
        return JsonResponse(data)

    try:
        a = int(request.POST.get('a', None))
        b = int(request.POST.get('b', None))
    except ValueError:
        data['status'] = 'Error'
        data['message'] = 'Musíš zadať celé čísla'
        return JsonResponse(data)

    if a == b:
        data['status'] = 'Error'
        data['message'] = 'Porovnávaš samé so sebou'
        return JsonResponse(data)
    if not (1 <= a <= POCET_PRVKOV and 1 <= b <= POCET_PRVKOV):
        data['status'] = 'Error'
        data['message'] = 'Čísla sú mimo rozsah [%d, %d]' % (1, POCET_PRVKOV)
        return JsonResponse(data)
    if a is None or b is None:
        data['status'] = 'Error'
        data['message'] = 'Nesprávne parametre'
        return JsonResponse(data)
    process_question(queries, a, b)
    request.session['plugin_prask_2_4_1/questions'] = queries
    data['status'] = 'Success'
    data['queries'] = queries
    return JsonResponse(data)

