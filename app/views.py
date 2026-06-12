from django.shortcuts import render, redirect 
from django.http import HttpResponse, JsonResponse 
from django.contrib import messages 
from django.views.decorators.csrf import csrf_exempt 
from .models import Contact, Chathistory, ChatSession, ChatMessage

import json 
from openai import OpenAI  

import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
# Existing Views
def home(request):
    sessions = ChatSession.objects.order_by('-created_at')[:5]
    return render(request, "index.html", {"sessions": sessions})


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def savedata(request):

    email = request.POST.get('email', "")
    message = request.POST.get('message', "")
    problem = request.POST.get('problem', "")

    if not email or not message or not problem:
        messages.error(request, "Please fill in all fields.")
        return redirect('contact')

    note = Contact(
        email=email,
        message=message,
        problem=problem
    )

    note.save()
    messages.success(request, "Query raised successfully! We will contact you soon.")
    return redirect('contact')

def chat_detail(request, id):

    session = ChatSession.objects.get(id=id)

    messages = ChatMessage.objects.filter(
        session=session
    )

    return render(
        request,
        'chat_details.html',
        {
            'session': session,
            'messages': messages
        }
    )

def chat_history(request):

    sessions = ChatSession.objects.order_by('-created_at')

    return render(
        request,
        'chat_history.html',
        {
            'sessions': sessions
        }
    )

# CHATBOT API
@csrf_exempt
def chatbot_api(request):

    if request.method == "POST":

        try:

            body = json.loads(request.body)

            user_message = (body.get("message") or "").strip()

            if not user_message:
                return JsonResponse({
                    "response": "Please enter a question to continue."
                }, status=400)

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": """
                        You are Teknixtic AI,
                        an intelligent student study assistant.

                        Help students with:
                        - Notes
                        - Topic summaries
                        - MCQ generation
                        - Important questions
                        - Study guidance

                        Keep responses concise,
                        professional and student-friendly.

                        IMPORTANT: Format every answer as bullet points.
                        Use 3 to 6 short bullet points, not long paragraphs.
                        Start each bullet with a dash (-) and keep each point clear and direct.
                        """
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            ai_reply = response.choices[0].message.content or "I’m here to help."

            session = ChatSession.objects.create(title=user_message[:40] or "New Chat")
            ChatMessage.objects.create(session=session, role="user", content=user_message)
            ChatMessage.objects.create(session=session, role="assistant", content=ai_reply)

            # Save chat history
            Chathistory.objects.create(
                user_message=user_message,
                teknixtic_response=ai_reply,
            )

            return JsonResponse({
                "response": ai_reply
            })

        except Exception as e:
            print("ERROR:", e)
            return JsonResponse({
                "response": str(e)   # temporary debug
            })

    return JsonResponse({
        "response": "Invalid request"
    })
