from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from website.task.forms import EditTaskForm, AddTaskForm
from website.task.models import Task


@login_required
def all_tasks(request):
    hide_completed = request.GET.get('hide_completed', False)
    tasks = Task.objects.all()
    if hide_completed:
        tasks = tasks.filter(completed=False)

    return TemplateResponse(request, 'tasks.html', {
        'tasks': tasks
    })


@login_required
def add(request):
    if request.method == 'POST':
        form = AddTaskForm(request.POST)
        if form.is_valid():
            Task(
                assignee=form.cleaned_data.get('assignee'),
                name=form.cleaned_data.get('name'),
                description=form.cleaned_data.get('description'),
                created_by=request.user
            ).save()
            return HttpResponseRedirect(reverse('all_tasks'))
        else:
            return TemplateResponse(request, 'edit_task.html', {'errors': form.errors})
    else:
        return TemplateResponse(request, 'edit_task.html', {})


@login_required
def mark_done(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        task.completed = True
        task.save(update_fields=['completed'])
    except Task.DoesNotExist:
        raise Http404

    return HttpResponseRedirect(reverse('all_tasks'))


@login_required
def edit(request, task_id):
    if request.method == 'POST':
        form = EditTaskForm(instance=Task.objects.get(id=task_id), data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('all_tasks'))
        return TemplateResponse(request, 'edit_task.html', {'errors': form.errors})
    else:
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise Http404

        form = EditTaskForm(instance=task)
        return TemplateResponse(request, 'edit_task.html', {'form': form, 'edit': True, 'task_id': task_id})


@login_required
def delete(request, task_id):
    try:
        Task.objects.get(id=task_id).delete()
    except Task.DoesNotExist:
        raise Http404

    return HttpResponseRedirect(reverse('all_tasks'))
