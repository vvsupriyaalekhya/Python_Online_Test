# from django.contrib.auth import authenticate, login, logout
# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse, JsonResponse
# from .models import Question, Results  # Import Results model
# import json
# import logging
# from django.contrib.auth.models import User
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas

# logger = logging.getLogger(__name__)

# def get_correct_answers():
#     # Get the correct answers from the Question model
#     return [question.answer for question in Question.objects.all()]

# @login_required
# def submit_assessment(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)

#         # Use the logged-in user instead of extracting from request body
#         username = request.user.username
#         correct_answers = data.get('correctAnswers')
#         wrong_answers = data.get('wrongAnswers')
#         total_questions = data.get('totalQuestions')
#         easy_questions = data.get('easyQuestions')
#         medium_questions = data.get('mediumQuestions')
#         hard_questions = data.get('hardQuestions')

#         # Log the assessment results for debugging
#         logger.info(f"User: {username} - Correct: {correct_answers}, Wrong: {wrong_answers}")

#         # Store results in session
#         request.session['assessment_data'] = {
#             'username': username,
#             'correct_count': correct_answers,
#             'wrong_count': wrong_answers,
#             'total_questions': total_questions,
#             'easy_count': easy_questions,
#             'medium_count': medium_questions,
#             'hard_count': hard_questions,
#         }

#         # Save results to the database
#         Results.objects.create(
#             user=request.user,
#             correct_answers=correct_answers,
#             wrong_answers=wrong_answers,
#             total_questions=total_questions,
#             easy_questions=easy_questions,
#             medium_questions=medium_questions,
#             hard_questions=hard_questions,
#         )

#         return JsonResponse({'status': 'success', 'message': 'Assessment submitted successfully.'})
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

# @login_required(login_url='login')
# def thank_you_view(request):
#     assessment_data = request.session.get('assessment_data', {})
#     return render(request, 'quiz/thank_you.html', {'assessment_data': assessment_data})

# @login_required(login_url='login')
# def generate_pdf(request):
#     assessment_data = request.session.get('assessment_data')
#     if not assessment_data:
#         logger.error("No assessment data found in session.")
#         return HttpResponse("No assessment data found.", status=400)

#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="{assessment_data["username"]}_assessment.pdf"'
#     p = canvas.Canvas(response, pagesize=letter)

#     try:
#         # PDF Heading
#         p.setFont("Times-Roman", 20)
#         p.drawString(100, 750, 'Online Assessment Report')

#         # Adding assessment details
#         p.setFont("Times-Roman", 12)
#         p.drawString(100, 720, f'Username: {assessment_data["username"]}')
#         p.drawString(100, 700, f'Total Questions: {assessment_data["total_questions"]}')
#         p.drawString(100, 680, f'Correct Answers: {assessment_data["correct_count"]}')
#         p.drawString(100, 660, f'Wrong Answers: {assessment_data["wrong_count"]}')
#         p.drawString(100, 640, f'Easy Questions: {assessment_data["easy_count"]}')
#         p.drawString(100, 620, f'Medium Questions: {assessment_data["medium_count"]}')
#         p.drawString(100, 600, f'Hard Questions: {assessment_data["hard_count"]}')

#         # Finalize PDF
#         p.showPage()
#         p.save()
#         del request.session['assessment_data']  # Clear session data after PDF generation
#     except Exception as e:
#         logger.error("Error generating PDF: %s", e)
#         return HttpResponse("Error generating PDF.", status=500)

#     return response

# @login_required(login_url='login')
# def test_view(request):
#     questions = Question.objects.order_by('?')[:30]
#     context = {
#         'questions': questions,
#         'username': request.user.username  # Ensure correct username is passed
#     }
#     return render(request, 'quiz/test.html', context)

# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
        
#         if user:
#             login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # Login the authenticated user
#             return redirect('exam')  # Redirect to the exam view

#         else:
#             # Check if user with username exists but password is incorrect
#             if User.objects.filter(username=username).exists():
#                 messages.error(request, "Invalid username or password.")
#             else:
#                 try:
#                     # Create a new user
#                     user = User.objects.create_user(username=username, password=password)
#                     # Login with specified backend
#                     login(request, user, backend='django.contrib.auth.backends.ModelBackend')
#                     messages.success(request, "Registration successful! You are now logged in.")
#                     return redirect('exam')  # Redirect to the exam view
#                 except Exception as e:
#                     messages.error(request, f"Error creating user: {str(e)}")
    
#     return render(request, 'quiz/login.html')

# @login_required(login_url='login')
# def exam_view(request):
#     print(f"Logged in user: {request.user.username}")  # Debugging output
#     context = {
#         'username': request.user.username  # Ensure context has the correct username
#     }
#     return render(request, 'quiz/exam.html', context)

# def logout_view(request):
#     logout(request)  # Log out the user
#     return redirect('login')  # Redirect to the login page after logout
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from .models import Question, Results
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import logging
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def get_correct_answers():
    return [question.answer for question in Question.objects.all()]

@csrf_exempt
@login_required
def submit_assessment(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = request.user.username
        user_answers = data.get('userAnswers')  # List of user's answers
        
        # Set the fixed number of questions
        total_questions = 30
        correct_answers = get_correct_answers()[:total_questions]  # Get only the first 30 answers

        # Initialize counts
        correct_count = 0
        wrong_count = 0
        total_attempted = 0

        # Calculate results
        for user_answer, correct_answer in zip(user_answers, correct_answers):
            if user_answer:
                total_attempted += 1
                if user_answer == correct_answer:
                    correct_count += 1
                else:
                    wrong_count += 1

        easy_questions = sum(1 for i in range(total_questions) if Question.objects.get(id=i+1).level == 'easy')
        medium_questions = sum(1 for i in range(total_questions) if Question.objects.get(id=i+1).level == 'medium')
        hard_questions = sum(1 for i in range(total_questions) if Question.objects.get(id=i+1).level == 'hard')

        logger.info(f"User: {username} - Correct: {correct_count}, Wrong: {wrong_count}, Total Attempted: {total_attempted}")

        # Store results in session
        request.session['assessment_data'] = {
            'username': username,
            'correct_count': correct_count,
            'wrong_count': wrong_count,
            'total_questions': total_questions,  # Fixed number of questions
            'total_attempted': total_attempted,
            'easy_count': easy_questions,
            'medium_count': medium_questions,
            'hard_count': hard_questions,
        }

        # Save results to the database
        Results.objects.create(
            user=request.user,
            correct_answers=correct_count,
            wrong_answers=wrong_count,
            total_questions=total_questions,
            easy_questions=easy_questions,
            medium_questions=medium_questions,
            hard_questions=hard_questions,
        )

        return JsonResponse({'status': 'success', 'message': 'Assessment submitted successfully.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@login_required(login_url='login')
def thank_you_view(request):
    assessment_data = request.session.get('assessment_data', {})
    email = request.user.email  # Get email directly from the logged-in user

    # Log to check the email value
    logger.info(f"User: {request.user.username}, Email: {email}")  

    return render(request, 'quiz/thank_you.html', {
        'assessment_data': assessment_data,
        'email': email  # Pass email to the template
    })



from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required(login_url='login')
def generate_pdf(request):
    assessment_data = request.session.get('assessment_data')
    email = request.user.email  # Assuming the email is saved in the User model
    
    if not assessment_data:
        logger.error("No assessment data found in session.")
        return HttpResponse("No assessment data found.", status=400)

    # Set up the response for PDF download
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{assessment_data["username"]}_assessment_report.pdf"'

    # Create PDF canvas
    p = canvas.Canvas(response, pagesize=letter)
    p.setTitle("Online MCQ Evaluator Report")
    p.bookmarkPage("Online_mcq_evaluator")  # Add bookmark

    try:
        # Add Header
        p.setFont("Helvetica-Bold", 24)
        p.setFillColor(colors.darkblue)
        p.drawString(1 * inch, 10 * inch, "Online MCQ Evaluator")

        # Add Subtitle
        p.setFont("Helvetica", 18)
        p.setFillColor(colors.black)
        p.drawString(1 * inch, 9.6 * inch, "Assessment Report")

        # Draw a line below header
        p.setStrokeColor(colors.darkblue)
        p.setLineWidth(2)
        p.line(1 * inch, 9.4 * inch, 7.5 * inch, 9.4 * inch)

        # Display User Information
        p.setFont("Helvetica", 12)
        p.setFillColor(colors.black)
        p.drawString(1 * inch, 9.0 * inch, f"Username: {assessment_data['username']}")
        p.drawString(1 * inch, 8.8 * inch, f"Email ID: {email}")

        # Display Assessment Details
        p.drawString(1 * inch, 8.4 * inch, "Assessment Summary:")
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1 * inch, 8.1 * inch, f"Total Questions: {assessment_data['total_questions']}")
        p.drawString(1 * inch, 7.9 * inch, f"Total Questions Attempted: {assessment_data['total_attempted']}")
        p.drawString(1 * inch, 7.7 * inch, f"Correct Answers: {assessment_data['correct_count']}")
        p.drawString(1 * inch, 7.5 * inch, f"Wrong Answers: {assessment_data['wrong_count']}")
        
        # Display Difficulty Breakdown with Highlighted Colors
        # p.setFont("Helvetica-Bold", 12)
        # p.setFillColor(colors.green)
        # p.drawString(1 * inch, 7.4 * inch, f"Easy Questions: {assessment_data['easy_count']}")
        
        # p.setFillColor(colors.orange)
        # p.drawString(1 * inch, 7.2 * inch, f"Medium Questions: {assessment_data['medium_count']}")
        
        # p.setFillColor(colors.red)
        # p.drawString(1 * inch, 7.0 * inch, f"Hard Questions: {assessment_data['hard_count']}")

        # Add Footer
        p.setFillColor(colors.gray)
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(1 * inch, 0.5 * inch, "Generated by Online MCQ Evaluator")

        # Finalize and save PDF
        p.showPage()
        p.save()

        # Remove session data after generating PDF
        del request.session['assessment_data']
    except Exception as e:
        logger.error("Error generating PDF: %s", e)
        return HttpResponse("Error generating PDF.", status=500)

    return response


@login_required(login_url='login')
def test_view(request):
    questions = Question.objects.order_by('?')[:30]  # Fetch only 30 random questions
    context = {
        'questions': questions,
        'username': request.user.username
        
    }
    return render(request, 'quiz/test.html', context)

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')  # Get email from form

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # User exists and password is correct
            login(request, user)  # Log the user in
            return redirect('exam')  # Redirect to the exam page
        else:
            # Check if the username already exists
            try:
                existing_user = User.objects.get(username=username)
                messages.error(request, 'Username already exists. Please choose a different username.')  # User already exists
            except User.DoesNotExist:
                # Handle the case where the user doesn't exist and create a new user
                new_user = User(username=username, email=email)  # Save the email
                new_user.set_password(password)  # Hash the password
                new_user.save()  # Save the new user

                # Authenticate and log in the new user
                new_user = authenticate(request, username=username, password=password)
                if new_user is not None:
                    login(request, new_user)  # Log in the newly created user
                    return redirect('exam')  # Redirect to the exam page
                else:
                    messages.error(request, 'Error during registration or authentication. Please try again.')

    return render(request, 'quiz/login.html')

@login_required(login_url='login')
def exam_view(request):
    print(f"Logged in user: {request.user.username}")
    context = {
        'username': request.user.username
    }
    return render(request, 'quiz/exam.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')
