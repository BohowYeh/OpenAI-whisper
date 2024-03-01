from pytube import YouTube
from pytube.exceptions import (RegexMatchError, VideoUnavailable)
import openai
from os import path



def find_best(url, is_audio = True):
  try:
    print("取得影片資訊.......")
    yt = YouTube(url)
    if is_audio:
      # 取得音檔, 只取音檔中品質最好的, 預設為 mp4 格式,
      # 可傳入參數指定音檔格式, 傳入 None 表示不限定格式
      audio_best = yt.streams.get_audio_only(None)
      return audio_best
    else:
      # 取得影片的串流檔案, 並將影片排序來取得最高品質
      video_best = yt.streams\
                      .filter(progressive=True, file_extension='mp4')\
                      .order_by('resolution')\
                      .desc()\
                      .first() 
      return video_best
  except RegexMatchError:
    print("網址有問題！")
    return None
  except VideoUnavailable:
    print("無法取得影片資源, 這可能是需要登入才能觀看的影片")
    return None


def download_file(stream):
  # 取得預設存檔路徑中純檔名的前 32 個字元, 避免檔名過長無法建檔
  file_basename = path.basename(stream.get_file_path())[:32]
  

  print("下載檔案.....")
  # 如不指定檔名, 會以 stream 預設的檔名存檔
  stream.download(filename=file_basename)
  print("下載完成")
  return file_basename


def transcribe(audio_filename):
  print("從音檔轉換字幕....")
  with open(audio_filename, "rb") as f:
    caption = openai.Audio.transcribe('whisper-1',f,response_format='srt',prompt='翻譯成繁體中文')
  print("轉換完成")
  print("將字幕存檔")
  srt_filename = path.splitext(audio_filename)[0] + ".srt"
  with open(srt_filename, "w") as f:
    f.write(caption)
  print("存檔完成")
  return caption


if __name__ == "__main__":
  source_type = input("1. 給予 YouTube 網址 2. 給予本地檔案\n 請輸入音訊來源 (1 or 2)：")
  if source_type == "1":
    url = input("請輸入 YouTube 影片的網址：")
    stream = find_best(url, is_audio = True)
    audio_filename = download_file(stream)
  elif source_type == "2":
    audio_filename = input("請輸入上傳的檔案名稱 (加副檔名)：")
  else:
      print("輸入不正確，請重新輸入。")
    
  caption = transcribe(audio_filename)
