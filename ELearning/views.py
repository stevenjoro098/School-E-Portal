import json
from django.urls import reverse

from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import title
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View, ListView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from fontTools.misc.bezierTools import segmentSegmentIntersections
from rest_framework.reverse import reverse_lazy

from Subjects.models import Grade
from .models import Subject, Strand, SubStrand, SubStrandNote, Note, ImageResource, VideoResource

class HomePage(TemplateView):
    template_name = 'home.html'

class GradeList(ListView):
    model = Grade
    template_name = 'curriculum_management/content_list.html'
    context_object_name = 'grades_list'

class SubjectsList(ListView):
    model = Subject
    template_name = 'curriculum_management/subjects_list.html'
    context_object_name = 'subjects_list'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strand'] = get_object_or_404(Strand, id=self.kwargs['strand_id'])
        return context

    def get_success_url(self):
        return reverse('strands_list', kwargs=self.kwargs['subject_id'])

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
        strand = get_object_or_404(Strand, id=self.kwargs['strand_id'])
        return SubStrand.objects.filter(strand=strand)

