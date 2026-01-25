from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import TimetableSlot, Day
from Subjects.models import Grade
from .forms import TimetableCellForm

def timetable_matrix_view(request):
    grade = get_object_or_404(Grade, id=1)
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
