from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Topic, Course, Student, Order
from .forms import SearchForm, OrderForm, ReviewForm, LoginForm, RegisterForm, ForgotPasswordForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime


def index(request):
    if request.session.get('last_login'):
        top_list = Topic.objects.all().order_by('id')[:10]
        student_name = request.user.get_username()
        return render(request, 'myapp/index.html', {'top_list': top_list, 'student_name': student_name})
    else:
        message = 'Your last login was more than one hour ago.'
        return render(request, 'myapp/index.html', {'message': message})


def about(request):

    student_name = request.user.get_username()
    if request.session.get('about_visits'):
        request.session['about_visits'] += 1
        request.session.set_expiry(300)
        about_visits = request.session['about_visits']
    else:
        request.session['about_visits'] = 1
        request.session.set_expiry(300)
        about_visits = request.session['about_visits']
    return render(request, 'myapp/about.html', {'student_name': student_name, 'about_visits': about_visits})


def detail(request, topic_id):
    topics = Topic.objects.filter(pk=topic_id)
    courses = Course.objects.filter(topic__in=topics)
    return render(request, 'myapp/detail.html', {'topics': topics, 'courses': courses})


def findcourses(request):
    # breakpoint()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            length = form.cleaned_data['length']
            max_price = form.cleaned_data['max_price']
            courselist = []
            if length:
                topics = Topic.objects.filter(length=length)
                for top in topics:
                    courselist = courselist + list(top.courses.filter(price__lt=max_price))

            else:
                topics = Topic.objects.all()
                for top in topics:
                    courselist = courselist + list(top.courses.filter(price__lt=max_price))
                return render(request, 'myapp/results.html', {'courselist': courselist, 'name': name, 'length': length})
        else:
            return HttpResponse('Invalid data')
    else:
        form = SearchForm()
        return render(request, 'myapp/findcourses.html', {'form': form})


def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            courses = form.cleaned_data['courses']
            order = form.save(commit=True)
            student = order.student
            status = order.order_status
            order.save()
            if status == 1:
                for c in order.courses.all():
                    student.registered_courses.add(c)
            return render(request, 'myapp/order_response.html', {'courses': courses, 'order': order})
        else:
            return render(request, 'myapp/place_order.html', {'form': form})

    else:
        form = OrderForm()
        return render(request, 'myapp/place_order.html', {'form': form})


def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            course = form.cleaned_data['course']
            if 0 < rating < 6:
                review = form.save(commit=True)
                review.save()
                course.num_reviews += 1
                top_list = Topic.objects.all().order_by('id')[:10]
                return render(request, 'myapp/index.html', {'top_list': top_list})
            else:
                form = ReviewForm()
                error_message = 'You must enter a rating between 1 and 5!'
                return render(request, 'myapp/review.html', {'form': form, 'error_message': error_message})
    else:
        form = ReviewForm()
        return render(request, 'myapp/review.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    request.session['last_login'] = str(datetime.today()) + str(datetime.now())
                    request.session.set_expiry(3600)
                    return HttpResponseRedirect(reverse('myapp:myaccount'))
                else:
                    return HttpResponse('Your account is disabled.')
            else:
                return HttpResponse('Invalid login details.')
        else:
            return HttpResponse('Invalid Data!')
    else:
        form = LoginForm()
        return render(request, 'myapp/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('myapp:index'))


@login_required
def myaccount(request):
    username = request.user.username
    try:
        student = Student.objects.get(username=username)
    except Student.DoesNotExist:
        student = None
    if student:
        first_name = student.first_name
        last_name = student.last_name
        interested_in = student.interested_in
        registered_courses = student.registered_courses
        topic_list = []
        for topic in interested_in.all():
            topic_list.append(topic)
        course_list = []
        for course in registered_courses.all():
            course_list.append(course)
        return render(request, 'myapp/myaccount.html',
                      {'first_name': first_name, 'last_name': last_name, 'topic_list': topic_list,
                       'course_list': course_list})

    else:
        return HttpResponse('You are not a registered student!')


@login_required
def myorders(request):
    user_id = request.user.id
    try:
        if user_id:
            user = get_object_or_404(Student, pk=user_id)
            orders = Order.objects.select_related().filter(student__username=user)
            return render(request, 'myapp/myorders.html',
                          {'user': user, 'orders': orders})
    except:
        msg = 'You are not a registered student!'
        return render(request, 'myapp/myorders.html', {'msg': msg})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('myapp:login')
    form = RegisterForm()
    return render(request, 'myapp/register.html', {'form': form})


def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                student = Student.objects.get(username=username)
                new_password = student.username + "123456"
                student.set_password(new_password)
                student.save()
                receiver = student.email
                sender = 'naderik@gmail.com'
                mail_body = "Your new password is: " + new_password
                send_mail('New Password', mail_body, sender, [receiver])
                message = "New password has been sent to your email id."
                return render(request, 'myapp/forgot_password.html', {'form': form,
                                                                      'message': message})
            except Student.DoesNotExist:
                form = ForgotPasswordForm()
                message = 'Invalid username, Please try again.'
                return render(request, 'myapp/forgot_password.html', {'form': form,
                                                                      'message': message})
    else:
        form = ForgotPasswordForm()
        return render(request, 'myapp/forgot_password.html', {'form': form})