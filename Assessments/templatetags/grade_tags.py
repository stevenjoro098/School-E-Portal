from django import template

register = template.Library()

@register.filter
def grade_color(grade_name):
    """
    Maps grade names to Bootstrap colors.
    Example: Grade 4 -> danger, Grade 5 -> primary, etc.
    """
    mapping = {
        "Grade 4": "danger",
        "Grade 5": "secondary",
        "Grade 6": "info",
        "Grade 7": "success",
        "Grade 8": "primary",
        "Grade 9": "warning",
    }
    return mapping.get(str(grade_name), "dark")  # default = dark gray
