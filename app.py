import streamlit as st
import yt_dlp
import os
import time
import sys
import requests
from yt_dlp.utils import download_range_func


def safe_int(value):
    return value if isinstance(value, int) else 0
BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg.exe")
def get_range(start, end):
    return download_range_func(None, [(start, end)])



if 'downloads' not in st.session_state:
    st.session_state.downloads = []
# FFMPEG_PATH = os.getcwd()

# Page Config
st.set_page_config(page_title="YouTube Downloader", page_icon="🎥", layout="wide")

st.title("🎥 YouTube Video Downloader")
st.write("Download YouTube videos and shorts in MP3 or MP4 format")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("⚡ **Lightning Fast**\n\nDownload in seconds")

with col2:
    st.info("🎬 **HD Quality**\n\nUp to 1080p Full HD")

with col3:
    st.info("📂 **Multiple Formats**\n\nMP3, 360p, 720p, 1080p")

st.divider()
               

url = st.text_input("📎 Enter YouTube Video/Shorts URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    try:
        with st.spinner("Fetching video information..."):
            ydl_opts = {'quiet': True, 'no_warnings': True}
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                st.success("✅ Video Found!")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(info['thumbnail'], caption="Video Thumbnail", use_container_width=True)
                    response = requests.get(info['thumbnail'])
                    if response.status_code == 200:
                        st.download_button(
                            "⬇⤵️ Download Thumbnail",
                            data=response.content,
                            file_name=f"{info['title']}_thumbnail.jpg",
                            mime="image/jpeg"
                        )
                with col2:
                    st.subheader(f"📹 {info['title']}")
                    st.write(f"**👤 Channel:** {info['uploader']}")
                    duration = safe_int(info.get('duration'))
                    st.write(f"**⏱️ Duration:** {duration//60} minutes {duration%60} seconds")
                    st.write(f"**👁️ Views:** {info['view_count']:,}")
                    

                                # Analytics Dashboard
                st.subheader("📊 Video Analytics")
                
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                with metric_col1:
                    likes = safe_int(info.get('like_count'))
                    st.metric("👍 Likes", f"{likes:,}")

                with metric_col2:
                    comments = safe_int(info.get('comment_count'))
                    st.metric("💬 Comments", f"{comments:,}")

                with metric_col3:
                    views = safe_int(info.get('view_count'))
                    st.metric("👁️ Views", f"{views:,}")

                with metric_col4:
                    duration = safe_int(info.get('duration'))
                    engagement = (likes / views * 100) if views > 0 else 0
                    size_1080p = (duration / 60) * 10 if duration > 0 else 0

                    st.metric("📈 Engagement", f"{engagement:.2f}%")
                    st.caption(f"📦 Est. 1080p Size: ~{size_1080p:.0f} MB")


                if 'total_downloads' not in st.session_state:
                    st.session_state.total_downloads = 0

                st.success(f"🎉 Total Downloads Today: {st.session_state.total_downloads}")
                st.divider()


                # Video Trimmer Feature
                st.subheader("✂️ Video Trimmer (Optional)")
                use_trimmer = st.checkbox("Enable trimming - download specific part only")
                safe_duration = safe_int(info.get('duration'))

                start_time = 0
                end_time = info['duration'] 
                if use_trimmer:
                    st.info("⏰ Select portion to download")
                    
                    trim_col1, trim_col2 = st.columns(2)
                    
                    with trim_col1:
                        start_time = st.number_input(
                            "⏪ Start Time (seconds)",
                            min_value=0,
                            max_value=safe_duration,
                            value=0
                        )
                    
                    with trim_col2:
                        end_time = st.number_input(
                            "⏩ End Time (seconds)",
                            min_value=start_time + 1,
                            max_value=safe_duration,
                            value=info['duration']
                        )
                    
                    trim_duration = end_time - start_time
                    st.success(f"✂️ Will download: {trim_duration}s ({trim_duration//60}m {trim_duration%60}s)")

                st.divider()

                st.subheader("📥 Select Download Format:")
                st.write("Choose your preferred quality:")
                format_col1, format_col2, format_col3, format_col4 = st.columns(4)

                with format_col1:
                    st.metric("🎵 MP3", "Audio", "192 kbps")

                with format_col2:
                    st.metric("📹 360p", "Video", "~20 MB")

                with format_col3:
                    st.metric("📹 720p", "Video", "~50 MB")

                with format_col4:
                    st.metric("📹 1080p", "Video", "~100 MB")

                st.write("")  # Spacing
                col1, col2, col3, col4 = st.columns(4)

                # MP3 Option
                with col1:
                    if st.button("🎵 MP3 (Audio Only)", use_container_width=True):
                        with st.spinner("Downloading MP3..."):
                            try:
                                   
                                
                                output_file = f"{info['title'][:40]}_audio_{int(time.time())}"
                                
                                ydl_opts_mp3 = {
                                    'format': 'bestaudio/best',
                                    'outtmpl': os.path.join(DOWNLOAD_DIR, f'{output_file}.%(ext)s'),
                                    'ffmpeg_location': FFMPEG_PATH,
                                    'prefer_ffmpeg': True,
                                    'postprocessors': [{
                                        'key': 'FFmpegExtractAudio',
                                        'preferredcodec': 'mp3',
                                        'preferredquality': '192',
                                    }],
                                }

                                # Example: MP3 option mein
                                if use_trimmer:
                                    ydl_opts_mp3['download_ranges'] = get_range(start_time, end_time)
                                    ydl_opts_mp3['force_keyframes_at_cuts'] = True




                                with yt_dlp.YoutubeDL(ydl_opts_mp3) as ydl:
                                    ydl.download([url])
                                mp3_file = None
                                for f in os.listdir(DOWNLOAD_DIR):
                                    if f.endswith(".mp3") and output_file in f:
                                        mp3_file = os.path.join(DOWNLOAD_DIR, f)
                                        break

                                if mp3_file:
                                    with open(mp3_file, "rb") as file:
                                        st.download_button(
                                            "⬇️ Download MP3",
                                            data=file,
                                            file_name=os.path.basename(mp3_file),
                                            mime="audio/mpeg"
                                        )

                                st.success(f"✅ MP3 Downloaded!")
                                st.balloons()
                                st.session_state.total_downloads += 1  
                                st.session_state.downloads.append({
                                    'title': info['title'], 
                                    'format': 'MP3', 
                                    'time': time.strftime('%H:%M:%S')
                                })
                            except Exception as e:
                      
                                if "downloaded" in str(e).lower() or os.path.exists(f"{output_file}.mp3"):
                                    st.success("✅ Audio file downloaded!")
                                    st.info("Note: File may be in M4A/WEBM format")
                                    st.balloons()
                                else:
                                    st.error(f"❌ Error: {str(e)}")

                # MP4 360p
                with col2:
                    if st.button("📹 MP4 - 360p", use_container_width=True):
                        with st.spinner("Downloading 360p..."):
                            try:
                                output_file = f"{info['title'][:40]}_360p_{int(time.time())}"
                                
                                ydl_opts_360 = {
                                    'format': '18',
                                    'outtmpl': os.path.join(DOWNLOAD_DIR, f'{output_file}.%(ext)s'),

                                }
                                
                                if use_trimmer:
                                    ydl_opts_360['download_ranges'] = get_range(start_time, end_time)
                                    ydl_opts_360['force_keyframes_at_cuts'] = True
                                    ydl_opts_360['ffmpeg_location'] = FFMPEG_PATH

                                with yt_dlp.YoutubeDL(ydl_opts_360) as ydl:
                                    ydl.download([url])
                                video_360 = None
                                for f in os.listdir(DOWNLOAD_DIR):
                                    if f.endswith(".mp4") and output_file in f:
                                        video_360 = os.path.join(DOWNLOAD_DIR, f)
                                        break

                                if video_360:
                                    with open(video_360, "rb") as file:
                                        st.download_button(
                                            "⬇️ Download 360p Video",
                                            data=file,
                                            file_name=os.path.basename(video_360),
                                            mime="video/mp4"
                                        )

                                st.success(f"✅ 360p Downloaded!")
                                st.balloons()
                                st.session_state.total_downloads += 1  
                                st.session_state.downloads.append({
                                    'title': info['title'], 
                                    'format': '360p', 
                                    'time': time.strftime('%H:%M:%S')
                                })
                            except Exception as e:
                                st.error(f"❌ {str(e)}")

                # MP4 720p
                with col3:
                    if st.button("📹 MP4 - 720p HD", use_container_width=True):
                        with st.spinner("Downloading 720p HD..."):
                            try:
                                output_file = f"{info['title'][:40]}_720p_{int(time.time())}"
                                
                                ydl_opts_720 = {
                                                    'format': 'best[height<=720]',
                                                    'outtmpl': os.path.join(DOWNLOAD_DIR, f'{output_file}.%(ext)s'),
                                                    'quiet': False,
                                                    'socket_timeout': 60,
                                                    'retries': 10,
                                                    'fragment_retries': 10,
                                                }
                                                
                                if use_trimmer:
                                    ydl_opts_720['download_ranges'] = get_range(start_time, end_time)
                                    ydl_opts_720['force_keyframes_at_cuts'] = True
                                    ydl_opts_720['ffmpeg_location'] = FFMPEG_PATH


                                with yt_dlp.YoutubeDL(ydl_opts_720) as ydl:
                                        ydl.download([url])   
                                        video_720 = None
                                for f in os.listdir(DOWNLOAD_DIR):
                                    if f.endswith(".mp4") and output_file in f:
                                        video_720 = os.path.join(DOWNLOAD_DIR, f)
                                        break

                                if video_720:
                                    with open(video_720, "rb") as file:
                                        st.download_button(
                                            "⬇️ Download 720p HD Video",
                                            data=file,
                                            file_name=os.path.basename(video_720),
                                            mime="video/mp4"
                                        )
                                            
                                st.success(f"✅ 720p HD Downloaded Successfully!")
                                st.balloons()
                                st.session_state.total_downloads += 1  
                                st.session_state.downloads.append({
                                    'title': info['title'], 
                                    'format': '720p HD', 
                                    'time': time.strftime('%H:%M:%S')
                                })
                            except Exception as e:
                                st.error(f"❌ Download failed. Try 360p for faster download.")


                # MP4 1080p
                with col4:
                    if st.button("📹 MP4 - 1080p Full HD", use_container_width=True):
                        with st.spinner("Downloading 1080p Full HD..."):
                            try:
                                output_file = f"{info['title'][:40]}_1080p_{int(time.time())}"

                                ydl_opts_1080 = {
                                    'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',  
                                    'outtmpl': os.path.join(DOWNLOAD_DIR, f'{output_file}.%(ext)s'),
                                    'ffmpeg_location': FFMPEG_PATH, 
                                    'merge_output_format': 'mp4',   
                                    'socket_timeout': 60,
                                    'retries': 10,
                                    'fragment_retries': 10,
                                }
                                
                                if use_trimmer:
                                 ydl_opts_1080['download_ranges'] = get_range(start_time, end_time)
                                 ydl_opts_1080['force_keyframes_at_cuts'] = True


                                with yt_dlp.YoutubeDL(ydl_opts_1080) as ydl:
                                    ydl.download([url])
                                video_1080 = None
                                for f in os.listdir(DOWNLOAD_DIR):
                                    if f.endswith(".mp4") and output_file in f:
                                        video_1080 = os.path.join(DOWNLOAD_DIR, f)
                                        break

                                if video_1080:
                                    with open(video_1080, "rb") as file:
                                        st.download_button(
                                            "⬇️ Download 1080p Full HD Video",
                                            data=file,
                                            file_name=os.path.basename(video_1080),
                                            mime="video/mp4"
                                        )

                                st.success(f"✅ 1080p Full HD Downloaded Successfully!")
                                st.balloons()
                                st.session_state.total_downloads += 1  
                                st.session_state.downloads.append({
                                    'title': info['title'], 
                                    'format': '1080p Full HD', 
                                    'time': time.strftime('%H:%M:%S')
                                })
                               
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                
                        st.divider()
                                                                               
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


st.divider()

st.caption("⚠️ Respect copyright laws")

st.divider()

with st.expander("💡 Download Tips"):
    st.write("• Use 360p for faster downloads")
    st.write("• Use 720p for balanced quality & size")
    st.write("• Use 1080p for maximum quality")
    st.write("• MP3 is perfect for music/podcasts")
    st.write("• Enable trimmer to download specific parts")
    


st.subheader("☁️ Best YouTube Downloader")

st.write("""
This YouTube Downloader allows you to download videos in MP3 and MP4 formats 
(up to 1080p), including Shorts.  

Just paste the YouTube link, select the quality, and download directly 
to your device — fast, simple, and free.
""")


st.subheader("❓ How to use?")

st.markdown("""
1. Paste the YouTube video or Shorts link  
2. Choose MP3 or MP4 quality  
3. (Optional) Trim the video  
4. Click download and save the file
""")


st.subheader("📌 Frequently Asked Questions")

with st.expander("1. Where are downloads saved?"):
    st.write("Files are processed on the server and downloaded directly to your device using the browser.")

with st.expander("2. How to download YouTube videos in MP3?"):
    st.write("Paste the YouTube link, click the MP3 button, and download the audio file.")

with st.expander("3. How long does it take to download videos?"):
    st.write("Download time depends on video length and your internet speed.")


with st.expander("4. Is it safe to use this downloader?"):
    st.write("Yes. This app does not store your data or track users.")


st.divider()
st.write("sohail shoro")