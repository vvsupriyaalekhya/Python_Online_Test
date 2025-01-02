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
@login_required(login_url='login')
def generate_pdf(request):
    # Retrieve assessment data from session
    assessment_data = request.session.get('assessment_data')
    email = request.user.email  # Assuming the email is saved in the User model
    
    # Log the assessment data to ensure it's being retrieved correctly
    logger.debug("Assessment Data Retrieved: %s", assessment_data)

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

        # Add Detected Objects to the PDF
        if 'detected_objects' in assessment_data:
            p.setFont("Helvetica-Bold", 12)
            p.setFillColor(colors.black)
            p.drawString(1 * inch, 6.5 * inch, "Detected Objects:")
            y_position = 6.3 * inch

            # Log detected objects
            logger.debug("Detected Objects: %s", assessment_data['detected_objects'])

            # Print detected objects and probabilities in the PDF
            for obj, prob in assessment_data['detected_objects']:
                p.drawString(1 * inch, y_position, f"- {obj}: {prob}%")
                y_position -= 0.2 * inch  # Adjust for space between entries
        else:
            logger.warning("No detected objects found in assessment data.")

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


# import cv2
# import numpy as np

# # Load pre-trained YOLO model
# net = cv2.dnn.readNet("quiz/templates/quiz/yolov3.weights", "quiz/templates/quiz/yolov3.cfg")
# layer_names = net.getLayerNames()
# output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# # Load COCO class labels
# with open("quiz/templates/quiz/coco.names", "r") as f:
#     classes = [line.strip() for line in f.readlines()]

# # Initialize the webcam (0 refers to the default camera)
# cap = cv2.VideoCapture(0)

# # Create a small window with a specified name
# cv2.namedWindow("Live Detection", cv2.WINDOW_NORMAL)

# while True:
#     # Capture each frame from the camera
#     ret, frame = cap.read()

#     # If frame is not successfully captured, break out of the loop
#     if not ret:
#         print("Failed to grab frame")
#         break

#     # Convert the frame to grayscale for face and pedestrian detection
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # Detect faces
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

#     # Detect objects using YOLO
#     blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
#     net.setInput(blob)
#     outs = net.forward(output_layers)

#     # Process YOLO detections
#     class_ids = []
#     confidences = []
#     boxes = []

#     for out in outs:
#         for detection in out:
#             scores = detection[5:]
#             class_id = np.argmax(scores)
#             confidence = scores[class_id]
#             if confidence > 0.5:  # Confidence threshold
#                 center_x = int(detection[0] * frame.shape[1])
#                 center_y = int(detection[1] * frame.shape[0])
#                 w = int(detection[2] * frame.shape[1])
#                 h = int(detection[3] * frame.shape[0])

#                 x = int(center_x - w / 2)
#                 y = int(center_y - h / 2)

#                 boxes.append([x, y, w, h])
#                 confidences.append(float(confidence))
#                 class_ids.append(class_id)

#     # Apply Non-Maximum Suppression (NMS) to remove redundant overlapping boxes
#     indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)  # Adjust NMS threshold as needed

#     # Capture the detected faces and objects (No rectangles drawn here)
#     detected_faces = []
#     detected_objects = []

#     # Collect detected faces
#     for (x, y, w, h) in faces:
#         detected_faces.append((x, y, w, h))  # Store coordinates of detected faces

#     # Collect detected objects
#     if len(indices) > 0:
#         for i in indices.flatten():
#             x, y, w, h = boxes[i]
#             label = str(classes[class_ids[i]])
#             confidence_text = f'{round(confidences[i] * 100, 2)}%'  # Display confidence percentage
#             detected_objects.append((label, confidence_text, (x, y, w, h)))

#     # Prepare the box for displaying detected objects information
#     output_text = ""
#     for obj in detected_objects:
#         output_text += f"{obj[0]}: {obj[1]}\n"

#     # Draw the small box on the right side of the screen
#     if output_text:
#         height, width, _ = frame.shape
#         # Create a small box area on the right side of the screen
#         box_width = 250  # Adjust width for longer text
#         box_height = 200  # Adjust height for text
#         box_x = width - box_width - 10  # Position box at the right side
#         box_y = 20  # Distance from the top

#         # Draw a rectangle to create the box
#         cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), (0, 0, 0), -1)

#         # Place the output text inside the small box
#         cv2.putText(frame, output_text, (box_x + 10, box_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

#     # Optionally, you can process the detected_faces and detected_objects as needed
#     for face in detected_faces:
#         print(f"Detected face: {face}")
#     for obj in detected_objects:
#         print(f"Detected object: {obj[0]} with confidence: {obj[1]} at position: {obj[2]}")

#     # Display the frame without resizing
#     cv2.imshow("Live Detection", frame)

#     # Move the window to the right side of the screen
#     cv2.moveWindow("Live Detection", 1000, 100)  # Adjust the window position as needed

#     # Exit the loop if the user presses the 'q' key
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release the webcam and close all OpenCV windows
# cap.release()
# cv2.destroyAllWindows()


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

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)  # Log the user in
            return redirect('exam')  # Redirect to the exam page
        else:

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
@login_required(login_url='login')
def capture_view(request):
    return render(request, 'quiz/capture.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

net = cv2.dnn.readNet("quiz/templates/quiz/yolov3.weights", "quiz/templates/quiz/yolov3.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

with open("quiz/templates/quiz/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

import cv2
import numpy as np

def detect_objects(image, net, output_layers, classes):
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []
    height, width, _ = image.shape

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:  # Confidence threshold
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply NMS
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    detected_objects = []
    if len(indices) > 0:
        for i in indices.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])  # Get the label
            confidence = round(confidences[i] * 100, 2)
            detected_objects.append({"label": label, "confidence": confidence, "box": [x, y, w, h]})

    return detected_objects

import cv2
import numpy as np
from django.http import JsonResponse

net = cv2.dnn.readNet("quiz/templates/quiz/yolov3.weights", "quiz/templates/quiz/yolov3.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
classes = []  # Load your class names from the file
with open("quiz/templates/quiz/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Your view function to handle POST requests
from fpdf import FPDF
import cv2
import numpy as np

def detect_objects_view(request):
    if request.method == 'POST':
        try:
            # Get image from the request (assuming it's base64 encoded or as a file upload)
            image = request.FILES['image']  # If the image is uploaded via a form
            image = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
            
            # Perform object detection
            objects = detect_objects(image, net, output_layers, classes)
            
            # Calculate accuracy (just a sample example here)
            total_objects = len(objects)
            correct_objects = sum([1 for obj in objects if obj['confidence'] > 70])  # Example condition for correct objects
            accuracy = (correct_objects / total_objects * 100) if total_objects > 0 else 0

            # Generate the PDF report
            pdf = FPDF()
            pdf.add_page()

            # Add the assessment summary
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(200, 10, txt="Online MCQ Evaluator Assessment Report", ln=True, align='C')

            pdf.set_font('Arial', '', 12)
            pdf.cell(200, 10, txt="Username: Supriya123", ln=True)
            pdf.cell(200, 10, txt="Email ID: supriyavenkata119@gmail.com", ln=True)
            pdf.cell(200, 10, txt="Total Questions: 30", ln=True)
            pdf.cell(200, 10, txt="Total Questions Attempted: 0", ln=True)
            pdf.cell(200, 10, txt="Correct Answers: 0", ln=True)
            pdf.cell(200, 10, txt="Wrong Answers: 0", ln=True)

            # Add object detection labels and accuracy
            pdf.cell(200, 10, txt="Object Detection Summary:", ln=True)
            pdf.set_font('Arial', '', 10)
            for obj in objects:
                pdf.cell(200, 10, txt=f"Label: {obj['label']}, Confidence: {obj['confidence']}%", ln=True)

            pdf.cell(200, 10, txt=f"Object Detection Accuracy: {accuracy}%", ln=True)

            # Output PDF to a file or send as response
            pdf.output("assessment_report.pdf")

            return JsonResponse({'message': 'Report generated successfully.'}, status=200)

        except Exception as e:
            # Handle any exceptions that may arise
            return JsonResponse({'error': str(e)}, status=500)
