import json
import openai
from django.conf import settings
from django.http import StreamingHttpResponse
from ninja import Router

# Set OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

# Create API router
router = Router()

# Stream output
@router.get("/stream", tags=_TGS)
def create_stream(request):

    # Read user message
    user_content = request.GET.get('content', '')

    # Talk to OpenAI API
    def event_stream():
        for chunk in openai.ChatCompletion.create(
            model='gpt-4-turbo',
            messages=[{
                "role": "user", "content": f"{user_content}. Response should \
                be in markdown formatting."
            }],
            stream=True,
        ):
            chatcompletion_delta = chunk["choices"][0].get("delta", {})
            data = json.dumps(dict(chatcompletion_delta))
            yield f'data: {data}\\n\\n'

    # Stream API output to browser in real-time
    response = StreamingHttpResponse(
        event_stream(), content_type="text/event-stream"
    )
    response.headers.update({
        'X-Accel-Buffering': 'no', 'Cache-Control': 'no-cache'
    })
    return response