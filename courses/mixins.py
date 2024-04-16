from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy

from courses.models.main_models import Course


class OwnerMixin:
    """Mixin for filtering queryset by the owner."""

    def get_queryset(self):
        """Return queryset filtered by the request user as the owner."""


class OwnerEditMixin:
    """Mixin for setting owner when form is valid."""

    def form_valid(self, form):
        """Set the owner of the instance to the request user."""
        if hasattr(form, 'instance'):
            form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin,
                       LoginRequiredMixin,
                       PermissionRequiredMixin):
    """Mixin for courses owned by the user."""
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    """Mixin for editing courses owned by the user."""
    template_name = 'manage/course/form.html'
