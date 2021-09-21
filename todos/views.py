from django.http import JsonResponse
from django.views import generic, View

from .models import Todo
from django.utils import timezone

import json


class IndexView(generic.ListView):
    template_name = 'todos/index.html'
    context_object_name = 'latest_todo_list'

    def get_queryset(self):
        return Todo.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    def get_queryset(self):
        return Todo.objects.filter(pub_date__lte=timezone.now())

class TodoData(View):

    def post(self, request):
        body = json.loads(request.body)
        print(body, "twice")

        t = Todo(todo_text=body["title"], pub_date=timezone.now())
        t.save()

        return JsonResponse({'objects': 0}, status=200)
    
    def get(self, request):
        todo_queryset = Todo.objects.all()

        json_objects = [{
            'text': todo.todo_text,
            'id': todo.id
        } for todo in reversed(todo_queryset)]

        return JsonResponse({'objects': json_objects}, status=200)