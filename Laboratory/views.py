from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Q

from .models import LabEquipment


class LaboratoryEquipmentListView(TemplateView):
    template_name = "labEquipmentList.html"

    def get_queryset(self):
        search = self.request.GET.get("search", "").strip()

        queryset = LabEquipment.objects.all().order_by("name")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset

    def get(self, request, *args, **kwargs):

        # Vue AJAX request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":

            data = []

            for item in self.get_queryset():

                data.append({
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "available_quantity": item.available_quantity,
                    "image": item.image.url if item.image else "",
                    "date_added": item.date_added.strftime("%d %b %Y"),
                })

            return JsonResponse(data, safe=False)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["equipment"] = self.get_queryset()
        return context