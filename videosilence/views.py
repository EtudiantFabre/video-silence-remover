import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from moviepy.editor import VideoFileClip, concatenate_videoclips
import datetime

progress = 0

def index(request):
    return render(request, 'upload.html')




def upload_video(request):
    global progress
    if request.method == 'POST':
        video_file = request.FILES['video']
        upload_dir = os.path.join(settings.BASE_DIR, 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        video_path = os.path.join(upload_dir, video_file.name)
        print(video_path)
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
    total_steps = total_clips + 1  # Include an extra step for concatenation
    
    for i, start in enumerate(range(0, total_clips, int(subclip_duration * 4))):
        subclip = video.subclip(start / 4, min((start + subclip_duration * 4) / 4, video.duration))
        if subclip.audio is not None and subclip.audio.max_volume() > 0.07:
            clips.append(subclip)
        
        # Update progress
        if progress_callback:
            progress_callback(i + 1, total_steps)
    
    # Concatenate clips
    final_clip = concatenate_videoclips(clips)
    
    # Update progress for concatenation step
    if progress_callback:
        progress_callback(total_steps, total_steps)
    
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
    video.close()  # Close the video file
    final_clip.close()  # Close the final clip
    return os.path.join(settings.MEDIA_URL, clean_name)

def get_progress(request):
    global progress
    return JsonResponse({'progress': progress})





def delete_videos(request):
    upload_dir = os.path.join(settings.BASE_DIR, 'uploads')
    media_dir = os.path.join(settings.MEDIA_ROOT)
    
    for dir_path in [upload_dir, media_dir]:
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
    
    return JsonResponse({'status': 'success'})