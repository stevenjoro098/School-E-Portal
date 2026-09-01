import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import title
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View, ListView, UpdateView, DeleteView, CreateView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.reverse import reverse_lazy

from Subjects.models import Grade
from .models import Subject, Strand, SubStrand, SubStrandNote, Note, ImageResource, VideoResource, SubStrandCoverage, \
    FileResource, ImageGeneralResource
from .forms import VideoUploadForm

class HomePage(TemplateView):
    template_name = 'main_home_page.html'

class GradeList(ListView):
    model = Grade
    template_name = 'curriculum_management/grades_list.html'
    context_object_name = 'grades_list'

class SubjectsList(ListView):
    model = Subject
    template_name = 'curriculum_management/subjects_list.html'
    context_object_name = 'subjects_list'

    def get_queryset(self):
        self.grade = get_object_or_404(Grade, id=self.kwargs['grade_id'])
        return Subject.objects.filter(grade=self.grade)


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grade'] = self.grade
        return context


class AddSubjectView(CreateView):
    model = Subject
    template_name = 'curriculum_management/add_subject_form.html'
    fields = ['name']  # exclude 'grade' so it's not shown in the form

    def form_valid(self, form):
        # Pre-fill grade with the grade_id from URL
        grade = get_object_or_404(Grade, pk=self.kwargs['grade_id'])
        form.instance.grade = grade
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('subjects_list_page', kwargs={'grade_id': self.kwargs['grade_id']})

class SubjectDelete(DeleteView):
    template_name = 'curriculum_management/delete_subject.html'
    model = Subject

    def get_success_url(self):
        return reverse('subjects_list_page', kwargs={'grade_id': self.kwargs['grade_id']})


class StrandsList(ListView):
    model = Strand
    template_name = 'curriculum_management/strand_list.html'
    context_object_name = 'strands_list'

    def get_queryset(self):
        self.subject = get_object_or_404(Subject, pk=self.kwargs['subject_id'])
        return Strand.objects.filter(subject=self.subject)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strands_json'] = json.dumps(list(self.get_queryset().values('id', 'name')))
        context['subject'] = self.subject
        return context

class ManageContentView(TemplateView):
    template_name = "curriculum_management/manage_content.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['subjects'] = Subject.objects.all()
        return ctx


# Lists
class StrandListView(View):
    def get(self, request):
        subject_id = request.GET.get('subject_id')
        strands = list(Strand.objects.filter(subject_id=subject_id).values('id', 'title'))
        return JsonResponse({'strands': strands})

class SubStrandListView(ListView):
    model = SubStrand
    template_name = 'curriculum_management/substrand_list_page.html'
    context_object_name = 'substrands_list'

    def get_queryset(self):
        self.strand = get_object_or_404(Strand, pk=self.kwargs['strand_id'])
        return SubStrand.objects.filter(strand=self.strand)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strand'] = self.strand
        # Convert queryset to JSON for Vue
        substrands_qs = self.get_queryset().values('id', 'name')
        context['substrands_json'] = mark_safe(json.dumps(list(substrands_qs)))  # safe for Vue

        return context


class StrandDelete(DeleteView):
    template_name = 'curriculum_management/delete_strand.html'
    model = Strand


    def get_success_url(self):
        pass

class NoteListView(View):
    def get(self, request):
        substrand_id = request.GET.get('substrand_id')
        notes = list(SubStrandNote.objects.filter(substrand_id=substrand_id).values('id', 'content', 'created_at', 'updated_at'))
        return JsonResponse({'notes': notes})


# Creates (POST using form-data)
@method_decorator(csrf_exempt, name='dispatch')
class AddStrandAPI(View):
    def post(self, request, subject_id):
        data = json.loads(request.body)
        print(data)
        name = data.get('name')
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        subject = Subject.objects.get(pk=subject_id)
        strand = Strand.objects.create(subject=subject, name=name)
        return JsonResponse({'id': strand.id, 'name': strand.name})

@method_decorator(csrf_exempt, name='dispatch')
class AddSubStrandView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            strand_id = data.get('strand_id')
            name = data.get('title')  # Make sure the key matches what frontend sends

            if not strand_id or not title:
                return JsonResponse({'status': 'error', 'message': 'Missing strand_id or title'}, status=400)

            # Create SubStrand
            ss = SubStrand.objects.create(strand_id=strand_id, name=name)

            return JsonResponse({
                'status': 'success',
                'id': ss.id,
                'title': ss.name
            })

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

class AddNoteView(TemplateView):
    template_name = 'curriculum_management/add_notes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['substrand_id'] = self.kwargs['substrand_id']
        return context

    def post(self, request):
        substrand_id = request.POST.get('substrand_id')
        content = request.POST.get('content')
        if not substrand_id or content is None:
            return JsonResponse({'status': 'error', 'message': 'Missing substrand_id or content'}, status=400)
        n = SubStrandNote.objects.create(substrand_id=substrand_id, content=content)
        return JsonResponse({'status': 'success', 'id': n.id, 'content': n.content})

class NoteEditView(UpdateView):
    model = Note
    template_name = 'curriculum_management/edit_notes.html'
    fields = ['content']
    success_url = reverse_lazy('add_substrands')

    def get_success_url(self):
        # Access extra variables
        substrand_id = self.kwargs['substrand_id']
        return reverse('resources_view', kwargs={'substrand_id': substrand_id})

class NoteDeleteView(DeleteView):
    template_name = 'curriculum_management/delete_note.html'
    model = Note

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note'] = get_object_or_404(Note, id=self.kwargs['pk'])
        context['substrand'] = self.kwargs['substrand_id']
        return context

    def get_success_url(self):
        # Access extra variables
        substrand_id = self.kwargs['substrand_id']
        return reverse('resources_view', kwargs={'substrand_id': substrand_id})


class ImageDeleteView(DeleteView):
    model = ImageResource
    template_name = 'curriculum_management/delete_image.html'

    def get_success_url(self):
        # Access extra variables
        substrand_id = self.kwargs['substrand_id']
        return reverse('resources_view', kwargs={'substrand_id': substrand_id})


# Update / Delete note (PUT and DELETE)
class SubstrandResourceView(TemplateView):
    template_name = 'curriculum_management/view_substrand_resources.html'

    def get(self, request, *args, **kwargs):
        try:
            substrand = get_object_or_404(SubStrand, id=self.kwargs['substrand_id'])
            notes = Note.objects.filter(substrand=substrand)
            images = ImageResource.objects.filter(substrand=substrand)
            videos = VideoResource.objects.filter(substrand=substrand)

            context = {
                'substrand': substrand,
                'notes': notes,
                'images': images,
                'videos': videos,
            }
            return render(request, self.template_name, context)
        except Exception as e:
            return HttpResponse(f"Unable to load resources: {e}", status=500)

    def put(self, request, note_id):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

        note = get_object_or_404(SubStrandNote, pk=note_id)
        content = data.get('content')
        if content is not None:
            note.content = content
            note.save()
        return JsonResponse({'status': 'success', 'id': note.id, 'content': note.content})

    def delete(self, request, note_id):
        note = get_object_or_404(SubStrandNote, pk=note_id)
        note.delete()
        return JsonResponse({'status': 'success'})


def save_notes(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))  # parse JSON
            notes = data.get('notes')
            substrand_id = data.get('substrand_id')

            substrand = get_object_or_404(SubStrand, id=substrand_id)
            Note.objects.create(content=notes, substrand=substrand)

            return JsonResponse({'status': 'success', 'message': 'Notes saved successfully!'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def save_image(request):
    if request.method == "POST":
        image = request.FILES.get("image")
        substrand_id = request.POST.get("substrand_id")

        if not image:
            return JsonResponse({"status": "error", "message": "No image provided"}, status=400)

        substrand = get_object_or_404(SubStrand, id=substrand_id)
        image_resource = ImageResource.objects.create(substrand=substrand, image=image)
        # Example: Save image to MEDIA
        # from django.core.files.storage import default_storage
        # filename = default_storage.save(f"substrands/{image.name}", image)

        return JsonResponse({
            "status": "success",
            "substrand_id": substrand_id
        })

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=405)
@csrf_exempt
def save_video(request):
    if request.method == 'POST':
        video = request.POST.get('video') or request.body.decode()
        VideoResource.objects.create(url=video, substrand_id=1)
        return JsonResponse({'message': 'Video saved'})


 # ==================================== Learners View =========================================================

class LearnersGradeList(ListView):
    model = Grade
    template_name = 'learners_templates/learner_grades_list.html'
    context_object_name = 'grade_list'

class GradeSubjectList(ListView):
    model = Subject
    template_name = 'learners_templates/learners_grade_subjects_list.html'
    context_object_name = 'subjects_list'

    def get_queryset(self):
        self.grade = get_object_or_404(Grade, id=self.kwargs['grade_id'])
        return Subject.objects.filter(grade=self.grade)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grade'] = self.grade
        return context

class SubjectStrandsList(ListView):
    model = Strand
    template_name = 'learners_templates/learners_subject_strands_list.html'
    context_object_name = 'strands_list'

    def get_queryset(self):
        self.subject = get_object_or_404(Subject, id=self.kwargs['subject_id'])
        return Strand.objects.filter(subject=self.subject)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject'] = self.subject
        return context

class SubStrandsList(ListView):
    model = SubStrand
    template_name = 'learners_templates/learners_substrands_list.html'
    context_object_name = 'sub_strands_list'

    def get_queryset(self):
        self.strand = get_object_or_404(Strand, id=self.kwargs['strand_id'])
        return SubStrand.objects.filter(strand=self.strand)

    def get_context_data(
        self, *, object_list = ..., **kwargs
    ):
        context = super().get_context_data(**kwargs)
        context['strand'] = self.strand
        return context

# views.py
from django.shortcuts import render, redirect

from .models import VideosResource

def upload_video(request):
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('video_list')
    else:
        form = VideoUploadForm()

    return render(request, "curriculum_management/upload_video.html", {"form": form})

def video_list(request):
    videos = VideosResource.objects.all()
    return render(request, "learners_templates/video_list.html", {"videos": videos})


class TeacherCoverageView(LoginRequiredMixin, TemplateView):
    template_name = "curriculum_management/curriculum_coverage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        subject = Subject.objects.get(pk=self.kwargs["subject_id"])

        strands = (
            Strand.objects
            .filter(subject=subject)
            .prefetch_related("substrands")
        )

        completed = {
            c.substrand_id: c
            for c in SubStrandCoverage.objects.all()
        }

        strand_data = []

        for strand in strands:

            total = strand.substrands.count()
            completed_count = 0
            substrands = []

            for ss in strand.substrands.all():

                coverage = completed.get(ss.id)

                is_completed = False
                status = "Not Started"
                completed_on = ""

                if coverage:
                    status = coverage.status.replace("_", " ").title()

                    if coverage.status == "completed":
                        is_completed = True
                        completed_count += 1

                    if coverage.completed_on:
                        completed_on = coverage.completed_on.strftime("%d %b %Y")

                substrands.append({
                    "id": ss.id,
                    "name": ss.name,
                    "status": status,
                    "completed": is_completed,
                    "completed_on": completed_on,
                })

            strand_data.append({
                "id": strand.id,
                "name": strand.name,
                "total": total,
                "completed": completed_count,
                "finished": total == completed_count,
                "substrands": substrands
            })

        context["subject"] = subject
        context["strand_data_json"] = json.dumps(strand_data)

        return context

from django.views import View
from django.shortcuts import get_object_or_404

class DeleteSubStrandView(View):

    def post(self, request, pk):

        substrand = get_object_or_404(SubStrand, pk=pk)

        substrand.delete()

        return JsonResponse({
            "status": "success"
        })

from django.http import JsonResponse
from django.utils import timezone
from django.views import View

class CompleteSubStrandView(LoginRequiredMixin, View):

    def post(self, request, substrand_id):
        substrand = get_object_or_404(SubStrand, pk=substrand_id)
        subject = get_object_or_404(Subject, pk=substrand.strand.subject.id)
        coverage, created = SubStrandCoverage.objects.get_or_create(
            substrand=substrand,
            subject=subject,
            term='Term',
            defaults={
                "status": "completed",
                "completed_on": timezone.now().date(),
            }
        )

        if not created:
            coverage.status = "completed"
            coverage.completed_on = timezone.now().date()
            coverage.save()

        return JsonResponse({
            "status": "success",
            "completed_on": coverage.completed_on.strftime("%d %b %Y")
        })

class StartSubStrandView(LoginRequiredMixin, View):
    def post(self, request):

        substrand = SubStrand.objects.get(
            pk=request.POST["substrand"]
        )

        coverage, created = SubStrandCoverage.objects.get_or_create(
            teacher=request.user,
            substrand=substrand
        )

        coverage.status="in_progress"

        if not coverage.started_on:
            coverage.started_on=timezone.now().date()

        coverage.save()

        return JsonResponse({
            "status":"success"
        })



class ResourcesPageView(TemplateView):
    template_name = "curriculum_management/resources_page_mngt.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["files"] = FileResource.objects.all().order_by("-id")
        context["images"] = ImageGeneralResource.objects.all().order_by("-id")
        context["videos"] = VideosResource.objects.all().order_by("-id")

        return context

class CreateVideoResource(CreateView):
    model = VideosResource
    template_name = 'curriculum_management/create_video_form.html'
    fields = ['title','description','video']
    success_url = reverse_lazy('resource_mngt_page')

class CreateFileResource(CreateView):
    model = FileResource
    template_name = 'curriculum_management/create_file_form.html'
    fields = ['file_title','file_description','grade','file']
    success_url = reverse_lazy('resource_mngt_page')

class CreateImageResource(CreateView):
    model = ImageGeneralResource
    template_name = 'curriculum_management/create_image_form.html'
    fields = ['image_title','image_description','image']
    success_url = reverse_lazy('resource_mngt_page')


class LearnerResourcePage(TemplateView):
    template_name = "learners_templates/resources_main_page.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["files"] = FileResource.objects.all().order_by("-id")
        context["images"] = ImageGeneralResource.objects.all().order_by("-id")
        context["videos"] = VideosResource.objects.all().order_by("-id")

        return context

class CurriculumCoverageSummaryView(TemplateView):

            template_name = (
                "curriculum_management/"
                "curriculum_coverage_summary.html"
            )

            def get_context_data(self, **kwargs):

                context = super().get_context_data(**kwargs)

                # --------------------------------------------------
                # Filters
                # --------------------------------------------------

                grade_id = self.request.GET.get("grade")
                term = self.request.GET.get("term")
                year = self.request.GET.get("year")

                if not term:
                    term = "Term 1"

                if not year:
                    year = 2026
                else:
                    try:
                        year = int(year)
                    except ValueError:
                        year = 2026

                grades = Grade.objects.all()

                grade = None

                if grade_id:
                    grade = grades.filter(id=grade_id).first()

                # Default to first grade
                if grade is None:
                    grade = grades.first()

                # --------------------------------------------------
                # Subjects
                # --------------------------------------------------

                subjects_data = []

                total_strands = 0
                covered_strands = 0

                total_substrands = 0
                covered_substrands = 0

                if grade:

                    subjects = (
                        Subject.objects
                        .filter(grade=grade)
                    )

                    for subject in subjects:

                        strands = (
                            Strand.objects
                            .filter(subject=subject)
                            .prefetch_related("substrands")
                        )

                        subject_total_strands = 0
                        subject_covered_strands = 0

                        subject_total_substrands = 0
                        subject_covered_substrands = 0

                        strand_data = []

                        for strand in strands:

                            substrands = strand.substrands.all()

                            strand_total = substrands.count()

                            strand_completed = (
                                SubStrandCoverage.objects
                                .filter(
                                    #grade=grade,
                                    #sub_strand__in=substrands,
                                    #term=term,
                                    #year=year,
                                    status="completed",
                                )
                                .count()
                            )

                            if strand_total:
                                strand_percentage = round(
                                    (strand_completed / strand_total) * 100
                                )
                            else:
                                strand_percentage = 0

                            if strand_completed == strand_total and strand_total > 0:
                                strand_status = "completed"
                            elif strand_completed > 0:
                                strand_status = "in_progress"
                            else:
                                strand_status = "not_started"

                            substrand_data = []

                            for substrand in substrands:
                                coverage = (
                                    SubStrandCoverage.objects
                                    .filter(
                                        #grade=grade,
                                        #sub_strand=substrand,
                                        #term=term,
                                        #year=year,
                                    )
                                    .first()
                                )

                                status = (
                                    coverage.status
                                    if coverage
                                    else "not_started"
                                )

                                substrand_data.append({
                                    "id": substrand.id,
                                    "name": substrand.name,
                                    "status": status,
                                    "remarks": (
                                        coverage.remarks
                                        if coverage
                                        else ""
                                    ),
                                })

                            strand_data.append({
                                "id": strand.id,
                                "name": strand.name,
                                "total": strand_total,
                                "completed": strand_completed,
                                "percentage": strand_percentage,
                                "status": strand_status,
                                "substrands": substrand_data,
                            })

                            # Subject totals
                            subject_total_substrands += strand_total
                            subject_covered_substrands += strand_completed

                            subject_total_strands += 1

                            if strand_completed == strand_total and strand_total > 0:
                                subject_covered_strands += 1

                        # Subject percentage
                        if subject_total_substrands:
                            subject_percentage = round(
                                (
                                        subject_covered_substrands
                                        / subject_total_substrands
                                ) * 100
                            )
                        else:
                            subject_percentage = 0

                        subjects_data.append({
                            "id": subject.id,
                            "name": subject.name,

                            "total_strands": subject_total_strands,
                            "covered_strands": subject_covered_strands,

                            "total_substrands": subject_total_substrands,
                            "covered_substrands": subject_covered_substrands,

                            "percentage": subject_percentage,

                            "strands": strand_data,
                        })

                        # Overall totals
                        total_strands += subject_total_strands
                        covered_strands += subject_covered_strands

                        total_substrands += subject_total_substrands
                        covered_substrands += subject_covered_substrands

                # --------------------------------------------------
                # Overall percentage
                # --------------------------------------------------

                if total_substrands:
                    overall_percentage = round(
                        (covered_substrands / total_substrands) * 100
                    )
                else:
                    overall_percentage = 0

                # --------------------------------------------------
                # Context
                # --------------------------------------------------

                context.update({
                    "grades": grades,
                    "grade": grade,
                    "subjects_data": subjects_data,

                    "term": term,
                    "year": year,

                    "total_strands": total_strands,
                    "covered_strands": covered_strands,

                    "total_substrands": total_substrands,
                    "covered_substrands": covered_substrands,

                    "overall_percentage": overall_percentage,
                })

                return context