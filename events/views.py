from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import UserSignup, UserLogin, EventForm, UserForm
from django.contrib import messages
from .models import Event, UserEvent
from datetime import date
from django.db.models import Q

def home(request):
	events=Event.objects.filter(date__gte=date.today())
	query=request.GET.get("q")
	if query:
		events=events.filter(title__contains=query)

	context={

	'events':events,
	}
	return render(request, 'home.html', context)

def event_list(request):
	context={

	'events':Event.objects.filter(date__gte=date.today())

	}
	return render(request, 'event_list.html', context)

def create_event(request):
	if request.user.is_anonymous:
		messages.warning(request, "You need to sign in first")
		return redirect('events:signin')
	form = EventForm()
	if request.method == "POST":
		form = EventForm(request.POST)
		if form.is_valid():
			event = form.save(commit=False)
			event.organizer = request.user
			event.save()
			messages.success(request, "Successfully Created!")
			return redirect('events:dashboard')
	context = {
	"form": form,
	}
	return render(request, 'event_create.html', context)

def dashboard(request):
	if request.user.is_anonymous:
		messages.warning(request, "You need to sign in first")
		return redirect('events:signin')

	events=Event.objects.filter(organizer=request.user)
	context={

		'events':events

	}
	return render(request,'dash.html',context)

def event_detail(request, event_id):
	context={
	'event':Event.objects.get(id=event_id)

	}
	return render(request,'event_detail.html',context)


def event_update(request, event_id):
	event = Event.objects.get(id=event_id)
	form = EventForm(instance=event)
	if request.method == "POST":
		form = EventForm(request.POST,instance=event)
		if form.is_valid():
			form.save()
			messages.success(request, "Successfully Edited!")
			return redirect('events:dashboard')
	context = {
	"form": form,
	"event": event,
	}
	return render(request, 'event_update.html', context)


def event_delete(request, event_id):
	Event.objects.get(id=event_id).delete()
	messages.success(request, "Successfully Deleted!")
	return redirect('events:dashboard')


class Signup(View):
	form_class = UserSignup
	template_name = 'signup.html'

	def get(self, request, *args, **kwargs):
		form = self.form_class()
		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.set_password(user.password)
			user.save()
			messages.success(request, "You have successfully signed up.")
			login(request, user)
			return redirect("events:home")
		messages.warning(request, form.errors)
		return redirect("events:signup")

def event_book(request, event_id):
	form = UserForm()
	event = Event.objects.get(id=event_id)
	if request.user.is_anonymous:
		return redirect('events:signin')
	if request.method == "POST":
		form = UserForm(request.POST)
		if form.is_valid():
			user_event = form.save(commit=False)
			user_event.event = Event.objects.get(id=event_id)
			user_event.name = request.user
			user_event.save()
			return redirect('events:home')
	context = {
		"form":form,
		"event": event,
	}
	return render(request, 'book_event.html', context)
class Login(View):
	form_class = UserLogin
	template_name = 'login.html'



	def get(self, request, *args, **kwargs):
		form = self.form_class()
		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():

			username = form.cleaned_data['username']
			password = form.cleaned_data['password']

			auth_user = authenticate(username=username, password=password)
			if auth_user is not None:
				login(request, auth_user)
				messages.success(request, "Welcome Back!")
				return redirect('events:dashboard')
			messages.warning(request, "Wrong email/password combination. Please try again.")
			return redirect("events:signin")
		messages.warning(request, form.errors)
		return redirect("events:signin")


class Logout(View):
	def get(self, request, *args, **kwargs):
		logout(request)
		messages.success(request, "You have successfully logged out.")
		return redirect("events:home")

