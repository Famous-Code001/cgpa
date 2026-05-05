from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout

from .models import CGPARecord


def get_grade_point(score: int) -> float:
    if score < 0 or score > 100:
        raise ValueError("Score must be within the range 0 to 100")

    if score >= 70:
        return 5.0
    elif score >= 60:
        return 4.0
    elif score >= 50:
        return 3.0
    elif score >= 45:
        return 2.0
    elif score >= 40:
        return 1.0
    else:
        return 0.0


def landing(request):
    return render(request, "landing.html")


@login_required
def home(request):
    context = {
        "cgpa": None,
        "records": [],
    }

    # --- CALCULATION PART (UNCHANGED) ---
    if request.method == "POST" and request.POST.get("action") == "calculate":
        units = request.POST.getlist("units[]")
        scores = request.POST.getlist("scores[]")

        try:
            total_units = 0
            total_credit_points = 0

            for u, s in zip(units, scores):
                u = int(u)
                s = int(s)

                gp = get_grade_point(s)

                total_units += u
                total_credit_points += u * gp

            cgpa = round(total_credit_points / total_units, 2)
            semester = request.POST.get("semester", "Current Semester")

            CGPARecord.objects.create(
                user=request.user,
                semester=semester,
                cgpa=cgpa,
                total_units=total_units,
                total_credit_points=total_credit_points,
            )

            request.session["last_result"] = {
                "cgpa": str(cgpa),
                "total_units": total_units,
                "total_credit_points": str(total_credit_points),
                "semester": semester,
            }

            return redirect("home")

        except Exception as e:
            context["error"] = str(e)

    # --- SHOW LAST RESULT ---
    last_result = request.session.pop("last_result", None)
    if last_result:
        context.update(last_result)

    # --- IMPORTANT: LOAD USER HISTORY ---
    context["records"] = CGPARecord.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "index.html", context)

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "sign.html", {"error": "Username already exists"})
        
        User.objects.create_user(username=username, password=password)
        return redirect("login")
    
    return render(request, "signup.html")

def logout_view(request):
    auth_logout(request)
    return redirect("login")

