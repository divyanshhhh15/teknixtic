from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Contact, Chathistory, ChatSession, ChatMessage

import json
import os
from dotenv import load_dotenv

load_dotenv()

from groq import Groq

# ✅ SAFE CLIENT INIT
def get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


# -----------------------
# BASIC VIEWS
# -----------------------

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

    Contact.objects.create(
        email=email,
        message=message,
        problem=problem
    )

    messages.success(request, "Query raised successfully! We will contact you soon.")
    return redirect('contact')


def chat_detail(request, id):

    session = ChatSession.objects.get(id=id)
    messages_qs = ChatMessage.objects.filter(session=session)

    return render(request, 'chat_details.html', {
        'session': session,
        'messages': messages_qs
    })


def chat_history(request):

    sessions = ChatSession.objects.order_by('-created_at')

    return render(request, 'chat_history.html', {
        'sessions': sessions
    })


# -----------------------
# CHATBOT API
# -----------------------

@csrf_exempt
def chatbot_api(request):

    if request.method != "POST":
        return JsonResponse({"response": "Invalid request"}, status=400)

    try:
        body = json.loads(request.body)
        user_message = (body.get("message") or "").strip()

        if not user_message:
            return JsonResponse({
                "response": "Message is required"
            }, status=400)

        # ❌ API key missing check
        if not os.getenv("GROQ_API_KEY"):
            return JsonResponse({
                "response": "Server missing GROQ_API_KEY"
            }, status=500)

        client = get_client()

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
You are Teknixtic AI, an intelligent student assistant.

Help with:
- Notes
- Summaries
- MCQs
- Important questions
- Study guidance

Rules:
- Always reply in 3 to 6 bullet points
- Keep answers short and clear
- Each bullet must start with '-'
"""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        ai_reply = response.choices[0].message.content or "I’m here to help."

        # Save session + messages
        session = ChatSession.objects.create(
            title=user_message[:40] or "New Chat"
        )

        ChatMessage.objects.create(
            session=session,
            role="user",
            content=user_message
        )

        ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=ai_reply
        )

        Chathistory.objects.create(
            user_message=user_message,
            teknixtic_response=ai_reply,
        )

        return JsonResponse({"response": ai_reply})

    except Exception as e:
        print("ERROR:", e)
        return JsonResponse({
            "response": "Server Error: " + str(e)
        }, status=500)