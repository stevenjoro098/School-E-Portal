from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse


from .models import TimetableSlot, Day
from Subjects.models import Grade
from .forms import TimetableCellForm

class TimeTable(TemplateView, View):
    template_name = 'timetable.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(context={'grades': Grade.objects.all()})

class GradeTimetableAPIView(View):
    def get(self, request, grade_id):
        slots = (
            TimetableSlot.objects
            .filter(grade_id=grade_id)
            .select_related("day", "subject")
            .order_by("start_time", "day__order")
        )

        days = list(
            Day.objects.filter(day_time_slots__grade_id=grade_id)
            .distinct()
            .order_by("order")
            .values_list("day", flat=True)
        )

        timetable = {}
        times = set()

        # Build matrix
        for slot in slots:
            time_key = f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"
            day_name = str(slot.day)

            times.add(time_key)

            if time_key not in timetable:
                timetable[time_key] = {}

            timetable[time_key][day_name] = str(slot.subject) if slot.subject else ""

        return JsonResponse({
            "days": days,
            "times": sorted(times),
            "grid": timetable
        })

def timetable_matrix_view(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    days = Day.objects.order_by("order")

    slots = (
        TimetableSlot.objects
        .filter(grade=grade)
        .select_related("day", "subject", "teacher")
        .order_by("start_time", "day__order")
    )

    # 🔹 Group slots by time
    timetable = {}
    for slot in slots:
        key = (slot.start_time, slot.end_time)
        timetable.setdefault(key, {})[slot.day.id] = slot

    if request.method == "POST":
        for slot in slots:
            prefix = f"slot_{slot.id}"
            form = TimetableCellForm(request.POST, prefix=prefix)

            if form.is_valid():
                slot.subject = form.cleaned_data["subject"]
                slot.teacher = form.cleaned_data["teacher"]
                slot.save()

        return redirect("edit")

    # GET request → build forms
    grid = []
    for (start, end), day_slots in timetable.items():
        row = {
            "start": start,
            "end": end,
            "cells": []
        }
        for day in days:
            slot = day_slots.get(day.id)
            form = TimetableCellForm(
                initial={
                    "subject": slot.subject if slot else None,
                    "teacher": slot.teacher if slot else None,
                },
                prefix=f"slot_{slot.id}" if slot else None
            )
            row["cells"].append((slot, form))
        grid.append(row)

    return render(request, "table_matrix.html", {
        "grade": grade,
        "days": days,
        "grid": grid,
    })
