from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import DetailView

from courses.models.other_models import Course


class CourseChatRoom(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'chat/room.html'
    context_object_name = 'course'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except self.model.DoesNotExist:
            # User doesn't have permission to join chat
            return HttpResponseForbidden()

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        course_id = self.kwargs.get('course_id')
        return self.request.user.courses_joined.get(id=course_id)
