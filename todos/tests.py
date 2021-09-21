import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Todo

class TodoModelTests(TestCase):

    def test_was_published_recently_with_future_todo(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_todo = Todo(pub_date=time)
        self.assertIs(future_todo.was_published_recently(), False)

    def test_was_published_recently_with_old_todo(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_todo = Todo(pub_date=time)
        self.assertIs(old_todo.was_published_recently(), False)

    def test_was_published_recently_with_recent_todo(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_todo = Todo(pub_date=time)
        self.assertIs(recent_todo.was_published_recently(), True)

def create_todo(todo_text, days):
    """
    Create a todo with the given `todo_text` and published the
    given number of `days` offset to now (negative for todos published
    in the past, positive for todos that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Todo.objects.create(todo_text=todo_text, pub_date=time)


class todoIndexViewTests(TestCase):
    def test_no_todos(self):
        """
        If no todos exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('todos:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No todos are available.")
        self.assertQuerysetEqual(response.context['latest_todo_list'], [])

    def test_past_todo(self):
        create_todo(todo_text="Past todo.", days=-30)
        response = self.client.get(reverse('todos:index'))
        self.assertQuerysetEqual(
            response.context['latest_todo_list'],
            ['<Todo: Past todo.>']
        )

    def test_future_todo(self):
        create_todo(todo_text="Future todo.", days=30)
        response = self.client.get(reverse('todos:index'))
        self.assertContains(response, "No todos are available.")
        self.assertQuerysetEqual(response.context['latest_todo_list'], [])

    def test_future_todo_and_past_todo(self):
        create_todo(todo_text="Past todo.", days=-30)
        create_todo(todo_text="Future todo.", days=30)
        response = self.client.get(reverse('todos:index'))
        self.assertQuerysetEqual(
            response.context['latest_todo_list'],
            ['<Todo: Past todo.>']
        )

    def test_two_past_todos(self):
        create_todo(todo_text="Past todo 1.", days=-30)
        create_todo(todo_text="Past todo 2.", days=-5)
        response = self.client.get(reverse('todos:index'))
        self.assertQuerysetEqual(
            response.context['latest_todo_list'],
            ['<Todo: Past todo 2.>', '<Todo: Past todo 1.>']
        )

class TodoDetailViewTests(TestCase):
    def test_future_todo(self):
        """
        The detail view of a todo with a pub_date in the future
        returns a 404 not found.
        """
        future_todo = create_todo(todo_text='Future todo.', days=5)
        url = reverse('todos:detail', args=(future_todo.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_todo(self):
        """
        The detail view of a todo with a pub_date in the past
        displays the todo's text.
        """
        past_todo = create_todo(todo_text='Past Todo.', days=-5)
        url = reverse('todos:detail', args=(past_todo.id,))
        response = self.client.get(url)
        self.assertContains(response, past_todo.todo_text)