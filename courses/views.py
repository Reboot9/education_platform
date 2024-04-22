from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.core.cache import cache
from django.db.models import Count
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import CreateView, \
    UpdateView, DeleteView, FormView
from rest_framework import generics, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.api.permissions import IsEnrolled
from courses.api.serializers import SubjectSerializer, CourseSerializer, CourseWithContentsSerializer
from courses.forms import ModuleFormSet
from courses.mixins import OwnerCourseMixin, OwnerCourseEditMixin
from courses.models.main_models import Course, Module, Content, Subject
from students.forms import CourseEnrollForm


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Clear the cache after creating a new course
        cache.delete("all_courses")
        return response


# class CourseListView(ListView):
#     model = Course
#     template_name = 'course/list.html'
#     context_object_name = 'courses'
#
#     def get_queryset(self):
#         all_courses = Course.objects.annotate(
#             total_modules=Count('modules')
#         )
#
#         subject_slug = self.kwargs.get('subject')
#         if subject_slug:
#             subject = get_object_or_404(Subject, slug=subject_slug)
#             key = f'subject_{subject.id}_courses'
#             courses = cache.get(key)
#             if not courses:
#                 courses = all_courses.filter(subject=subject)
#                 cache.set(key, courses)
#         else:
#             courses = cache.get('all_courses')
#             if not courses:
#                 courses = all_courses
#                 cache.set('all_courses', courses)
#
#         return courses
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['subjects'] = cache.get('all_subjects')
#         if not context['subjects']:
#             context['subjects'] = Subject.objects.annotate(
#                 total_courses=Count('courses')
#             )
#             cache.set('all_subjects', context['subjects'])
#
#         subject = self.kwargs.get('subject')
#         if subject:
#             context['subject'] = get_object_or_404(Subject, slug=subject)
#
#         return context
class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'course/list.html'
    context_object_name = 'courses'

    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(
                            total_courses=Count('courses'))
            cache.set('all_subjects', subjects)
        all_courses = Course.objects.annotate(
                        total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = f'subject_{subject.id}_courses'
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
        return self.render_to_response({'subjects': subjects,
                                        'subject': subject,
                                        'courses': courses})


class CourseDetailView(DetailView):
    model = Course
    template_name = 'course/detail.html'

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is already enrolled in the course
        if self.get_object().students.filter(id=request.user.id).exists():
            return redirect('student_course_detail', pk=self.get_object().pk)

        return super().dispatch(request, *args, **kwargs)

    # def get_object(self, queryset=None):
    #     course_object = super().get_object(queryset=queryset)
    #
    #     # Check if the user is already enrolled in the course
    #     if self.request.user in course_object.students.all():
    #         # If the user is already enrolled, redirect to the student_course_detail
    #         return redirect(reverse('student_course_detail', args=[course_object.pk]))
    #
    #     return course_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(
            initial={'course': self.object}
        )

        return context


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

    def form_valid(self, form):
        response = super().form_valid(form)

        cache.delete('all_subjects')
        cache.delete("all_courses")
        if self.object.subject:
            key = f'subject_{self.object.subject.id}_courses'
            cache.delete(key)
        return response


class CourseDeleteView(OwnerCourseEditMixin, DeleteView):
    template_name = 'manage/course/delete.html'
    permission_required = 'courses.delete_course'

    def delete(self, request, *args, **kwargs):
        subject = self.get_object().subject
        response = super().delete(request, *args, **kwargs)

        cache.delete('all_subjects')
        cache.delete("all_courses")
        if subject:
            key = f'subject_{subject.id}_courses'
            cache.delete(key)
        return response


class CourseModuleFormView(FormView):
    template_name = 'manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        self.course = get_object_or_404(Course,
                                        id=pk,
                                        owner=request.user)

        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()

        return self.render_to_response({
            'course': self.course,
            'formset': formset,
        })

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)

        if formset.is_valid():
            formset.save()

            # Clear the cache after saving the formset
            cache.delete('all_subjects')
            cache.delete("all_courses")
            if self.course.subject:
                key = f'subject_{self.course.subject.id}_courses'
                cache.delete(key)

            return redirect('manage_course_list')

        return self.render_to_response({
            'course': self.course,
            'formset': formset,
        })


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None

    template_name = 'manage/content/form.html'

    def get_model(self, model_name):
        if model_name in {'text', 'video', 'image', 'file', }:
            return apps.get_model(app_label='courses', model_name=model_name)

        return None

    def get_form(self, model, *args, **kwargs):
        form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])

        return form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id_=None):
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)

        self.model = self.get_model(model_name)

        if id_:
            self.obj = get_object_or_404(self.model, id=id_, owner=request.user)

        return super().dispatch(request, module_id, model_name, id_)

    def get(self, request, module_id, model_name, id_=None):
        form = self.get_form(self.model, instance=self.obj)

        return self.render_to_response({'form': form,
                                        'obj': self.obj})

    def post(self, request, module_id, model_name, id_=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()

            # Clear the cache after creating or updating content
            cache.delete('all_subjects')
            cache.delete("all_courses")
            if self.module.course.subject:
                key = f'subject_{self.module.course.subject.id}_courses'
                cache.delete(key)

            if not id_:
                # new content
                Content.objects.create(module=self.module, item=obj)

            return redirect('module_content_list', self.module.id)

        return self.render_to_response({'form': form,
                                        'obj': self.obj})


class ContentDeleteView(View):
    def post(self, request, id_):
        content = get_object_or_404(Content,
                                    pk=id_,
                                    module__course__owner=request.user)

        module = content.module
        content.item.delete()
        content.delete()

        # Clear the cache after deleting content
        cache.delete('all_subjects')
        cache.delete("all_courses")
        if module.course.subject:
            key = f'subject_{module.course.subject.id}_courses'
            cache.delete(key)

        return redirect('module_content_list', module.id)


class ModuleContentListView(ListView):
    template_name = 'manage/module/content_list.html'
    context_object_name = 'module'

    def get_queryset(self):
        queryset = get_object_or_404(Module,
                                     pk=self.kwargs.get('module_id'),
                                     course__owner=self.request.user)

        return queryset


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id_, order in self.request_json.items():
            Module.objects.filter(id=id_,
                                  course__owner=request.user).update(order=order)

        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id_, order in self.request_json.items():
            Content.objects.filter(id=id_,
                                   module__course__owner=request.user).update(order=order)

        return self.render_json_response({'saved': 'OK'})


class SubjectListView(generics.ListAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()


class SubjectDetailView(generics.RetrieveAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @action(detail=True, methods=['post'],
            authentication_classes=[BasicAuthentication, ],
            permission_classes=[IsAuthenticated, ])
    def enroll(self, request, *args, **kwargs):
        course = self.get_object()
        course.students.add(request.user)

        return Response({'enrolled': True})

    @action(detail=True, methods=['get'],
            serializer_class=CourseWithContentsSerializer,
            authentication_classes=[BasicAuthentication, ],
            permission_classes=[IsAuthenticated, IsEnrolled, ])
    def contents(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
