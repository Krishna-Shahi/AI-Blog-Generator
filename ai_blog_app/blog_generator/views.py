from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from pytube import YouTube
from django.conf import settings
import os
import assemblyai
import openai

# Create your views here.
@login_required
def index(request):
    print(settings.MEDIA_ROOT)
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    print("here in generate blog")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        #get title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': "Failed to get transcript"}, status=500)

        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcript(transcription)
        if not blog_content:
            return JsonResponse({'error': "Failed to generate blog article"}, status=500)
        # save blog article to database
        # return blog article as a response
        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title

def download_audio(link):
    print("here on download audio")
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    print(type(new_file))
    return new_file

def get_transcription(link):
    print("here on get transcription")
    audio_file = download_audio(link)
    print("after audio downloaded and into get transcription again")
    assemblyai.settings.api_key = ""
    transcriber = assemblyai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    print("transcript has been made")
    return transcript.text

def generate_blog_from_transcript(transcription):
    openai.api_key = "sk-proj-rajudHh5rQOeyWUyPMpIT3BlbkFJ6DXDhxh7iUWE"

    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=1000
    )

    generated_content = response.choices[0].text.strip()

    return generated_content

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_nessage': error_message})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('/')

def user_signup(request):
    if request.method=='POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmPassword = request.POST['confirmPassword']
        if password == confirmPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating an account'
        else:
            error_message = 'Passwords do not match!'
            return render(request, 'register.html', {'error_message': error_message})

    return render(request, 'register.html')