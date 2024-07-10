from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
import datetime
from django.conf import settings

progress = 0

def index(request):
    return render(request, 'upload.html')

def upload_video(request):
    global progress
    if request.method == 'POST':
        video_file = request.FILES['video']
        video_path = os.path.join('uploads', video_file.name)
        
        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        
        # Process the video to remove silence
        def progress_callback(current, total):
            global progress
            progress = (current / total) * 100
        
        processed_video_path = remove_silence(video_path, progress_callback)
        
        return JsonResponse({
            'original_video_url': os.path.join(settings.MEDIA_URL, video_file.name),
            'processed_video_url': processed_video_path
        })
    return HttpResponse("Upload a video file.")

def remove_silence(video_path, progress_callback=None):
    video = VideoFileClip(video_path)
    clips = []
    subclip_duration = 0.25  # Duration of each subclip in seconds
    total_clips = int(video.duration * 4)
    
    for i, start in enumerate(range(0, total_clips, int(subclip_duration * 4))):
        subclip = video.subclip(start / 4, min((start + subclip_duration * 4) / 4, video.duration))
        if subclip.audio is not None and subclip.audio.max_volume() > 0.07:
            clips.append(subclip)
        
        # Update progress
        if progress_callback:
            progress_callback(i + 1, total_clips)
    
    print("Je suis ici")
    final_clip = concatenate_videoclips(clips)
    
    # Generate a unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    base_name = os.path.basename(video_path)
    name, ext = os.path.splitext(base_name)
    clean_name = f"{timestamp}{ext}"
    processed_video_path = os.path.join(settings.MEDIA_ROOT, clean_name)
    
    # Ensure the media directory exists
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)
        
    final_clip.write_videofile(processed_video_path)
    return os.path.join(settings.MEDIA_URL, clean_name)

def get_progress(request):
    global progress
    return JsonResponse({'progress': progress})




def delete_video(request):
    if request.method == 'POST':
        video_path = request.POST.get('video_path')
        print(os.path.exists(video_path))
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'File not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})