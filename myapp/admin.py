from django.contrib import admin
import decimal
from .models import Topic, Course, Student, Order, Review


class CourseAdmin(admin.ModelAdmin):
    fields = [('title', 'topic'), ('price', 'num_reviews', 'for_everyone')]
    list_display = ('title', 'topic', 'price')
    actions = ['discount_10']

    def discount_10(self, request, queryset):
        from math import ceil
        discount = 10

        for course in queryset:
            multiplier = discount/decimal.Decimal(100.0)
            old_price = course.price
            new_price = ceil(old_price - (old_price * multiplier))
            course.price = new_price
            course.save(update_fields=['price'])
    discount_10.short_description = 'Set 10%% discount'


class OrderAdmin(admin.ModelAdmin):
    fields = ['courses', ('student', 'order_status')]
    readonly_fields = ['order_date']
    list_display = ('id', 'student', 'order_status', 'order_date', 'total_items')


class StudentAdmin(admin.ModelAdmin):
    fields = ['first_name', 'last_name', 'level', 'registered_courses']

    list_display = ('username', 'first_name', 'last_name', 'level', 'get_courses')

    def get_courses(self, obj):
        return ", ".join([p.title for p in obj.registered_courses.all()])


class CourseInline(admin.TabularInline):
    model = Course


class TopicAdmin(admin.ModelAdmin):
    fields = ['name', 'length']
    list_display = ('name', 'length')
    inlines = [CourseInline]


admin.site.register(Topic, TopicAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review)


