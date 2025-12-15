from django.shortcuts import render, redirect

def home(request):
    return redirect("compare_users")

def compare_form(request):
    return render(request, "anime_compare/compare_form.html")