# timetable/management/commands/generate_timetable_slots.py

from django.core.management.base import BaseCommand
from TimeTable.models import TimetableSlot, Day
from Subjects.models import Grade
from datetime import time

class Command(BaseCommand):
    help = "Generate blank timetable slots for all grades"

    def handle(self, *args, **kwargs):
        slots = [
            (time(8, 00), time(8, 40), "", False),
            (time(8, 40), time(9, 20), "", False),
            (time(9, 20), time(9, 30), "SHORT BREAK", False),
            (time(9, 30), time(10, 10), "", True),
            (time(10, 10), time(10, 50), "", False),
            (time(10, 50), time(11, 20), "BREAK", False),
            (time(11, 20), time(12, 00), "", False),
            (time(12, 00), time(12, 40), "", True),
            (time(12, 40), time(13, 20), "LUNCH", False),
            (time(13, 20), time(14, 00), "", False),
            (time(14, 00), time(14, 40), "", False),
        ]

        for grade in Grade.objects.all():
            for day in Day.objects.all():
                for start, end, label, is_break in slots:
                    TimetableSlot.objects.get_or_create(
                        grade=grade,
                        day=day,
                        start_time=start,
                        end_time=end,
                        defaults={
                            "label": label,

                        }
                    )

        self.stdout.write(self.style.SUCCESS("Timetable slots generated successfully."))
