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
        "cgpa": None
    }

    if request.method == "POST" and request.POST.get("action") == "calculate":
        try:
            units = request.POST.getlist("units[]")
            scores = request.POST.getlist("scores[]")

            if not units or not scores:
                raise ValueError("No data submitted.")

            if len(units) != len(scores):
                raise ValueError("Mismatched units and scores.")

            total_units = 0
            total_credit_points = 0

            for u, s in zip(units, scores):
                try:
                    u = int(u)
                    s = int(s)
                except (ValueError, TypeError):
                    raise ValueError("All inputs must be valid numbers.")

                if u < 1:
                    raise ValueError("Units must be at least 1.")

                gp = get_grade_point(s)

                total_units += u
                total_credit_points += u * gp

            if total_units == 0:
                raise ValueError("Total units cannot be zero.")

            cgpa = round(total_credit_points / total_units, 2)

            CGPARecord.objects.create(
                user=request.user,
                semester=request.POST.get("semester", "Current Semester"),
                cgpa=cgpa,
                total_units=total_units,
                total_credit_points=total_credit_points
            )

            context.update({
                "cgpa": cgpa,
                "total_units": total_units,
                "total_credit_points": total_credit_points
            })

        except ValueError as e:
            context["error"] = str(e)

        except Exception as e:
            context["error"] = str(e)

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

