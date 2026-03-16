from django.db import models
from django.contrib.auth.models import User
from Subjects.models import Grade


class Notice(models.Model):

    NOTICE_TYPE = (
        ("general", "General"),
        ("exam", "Exam"),
        ("assignment", "Assignment"),
        ("event", "Event"),
        ("urgent", "Urgent"),
    )

    title = models.CharField(max_length=255)

    message = models.TextField()

    notice_type = models.CharField(
        max_length=20,
        choices=NOTICE_TYPE,
        default="general"
    )

    posted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="posted_notices"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    expiry_date = models.DateTimeField(
        null=True,
        blank=True
    )

    is_pinned = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class NoticeUser(models.Model):

    notice = models.ForeignKey(
        Notice,
        related_name="target_users",
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.notice} -> {self.user}"