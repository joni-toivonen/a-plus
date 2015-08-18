from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from course.models import Course, CourseInstance, CourseHook, CourseModule, \
    CourseChapter, LearningObjectCategory
from userprofile.models import UserProfile


def instance_url(instance):
    """
    Returns the URL for the admin listing.
    """
    return instance.get_absolute_url()

instance_url.short_description = _('URL')


class CourseAdmin(admin.ModelAdmin):

    list_display_links = ["id"]
    list_display = ["id", "name", "code", "url"]
    #list_editable = ["name", "code"]
    filter_horizontal = ["teachers"]

    def get_queryset(self, request):
        if not request.user.is_superuser:
            profile = UserProfile.get_by_request(request)
            return profile.teaching_courses
        else:
            return self.model.objects.filter()


class CourseInstanceAdmin(admin.ModelAdmin):

    list_display_links = ["instance_name"]
    list_display = ["course", "instance_name", "visible_to_students",
        "starting_time", "ending_time", instance_url]
    list_filter = ["course", "visible_to_students",
        "starting_time", "ending_time"]
    filter_horizontal = ["assistants"]

    def get_queryset(self, request):
        if not request.user.is_superuser:
            profile = UserProfile.get_by_request(request)
            return self.model.objects.where_staff_includes(profile)
        else:
            return self.model.objects.all()


class CourseModuleAdmin(admin.ModelAdmin):
    list_display_links = ("__str__",)
    list_display = ("course_instance", "__str__",
        "opening_time", "closing_time", instance_url)
    list_filter = ["course_instance", "opening_time", "closing_time"]


class CourseChapterAdmin(admin.ModelAdmin):
    list_display_links = ("__str__",)
    list_display = ("course_instance", "course_module",
        "__str__", instance_url, "content_url")
    list_filter = ["course_module"]


class LearningObjectCategoryAdmin(admin.ModelAdmin):
    list_display_links = ("name",)
    list_display = ("course_instance", "name")
    list_filter = ("course_instance",)
    ordering = ["course_instance", "id"]


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseInstance, CourseInstanceAdmin)
admin.site.register(CourseHook)
admin.site.register(CourseModule, CourseModuleAdmin)
admin.site.register(CourseChapter, CourseChapterAdmin)
admin.site.register(LearningObjectCategory, LearningObjectCategoryAdmin)
