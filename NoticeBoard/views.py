from braces.views import LoginRequiredMixin
from django.views.generic import CreateView, ListView
from rest_framework.reverse import reverse_lazy

from .models import Notice


# Create your views here.
class CreateNotice(CreateView, LoginRequiredMixin):
    model = Notice
    template_name = 'create_notice.html'
    fields = ['title','message','notice_type','expiry_date']
    success_url = reverse_lazy('notice_board')

class NoticeBoardList(ListView):
    template_name = 'notice_board.html'
    model = Notice

    def get_context_data(
        self, *, object_list = ..., **kwargs
    ):
        context = super().get_context_data(**kwargs)
        context['pinned_notices'] = Notice.objects.filter(is_pinned = True)
        context['notices'] = Notice.objects.all()
        return context
