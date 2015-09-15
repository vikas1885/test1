"""
Course Overview utils
"""
from django.conf import settings
from lms.djangoapps.ccx.overrides import get_current_ccx


def is_discussion_enabled(course_id):
    """
    Return True if Discussion is enabled for a course; else False
    """
    if settings.FEATURES.get('CUSTOM_COURSES_EDX', False):
        if get_current_ccx(course_id):
            return False
    return settings.FEATURES.get('ENABLE_DISCUSSION_SERVICE')
