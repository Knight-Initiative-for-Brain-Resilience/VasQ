import json
from django.http import JsonResponse
from django.shortcuts import render
from .functions import chat

# Render landing page
def index(request):
    return render(request, 'vasq/index.html')

# Parse user input
def parse_input(request):
    return json.loads(request.body).get('message', '')

# API endpoint for chat
def api_chat(request):
    
    # Parse user input
    user_input = parse_input(request)
    print(f"Received message: {user_input}")

    # Load history and process request
    history = request.session.get('history', [])
    content, history = chat(user_input, history)
        
    # Update history
    request.session['history'] = history

    # Return formatted response
    return JsonResponse({"response": content})