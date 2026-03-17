import os
import sys
import datetime
import glob

try:
    import whisper
except ImportError:
    print("whisper 패키지가 설치되어 있지 않습니다. 설치 후 다시 실행하세요.")
    print("pip install -U openai-whisper")
    sys.exit(1)

# ffmpeg 경로 확인
from shutil import which
if which("ffmpeg") is None:
    print("ffmpeg가 시스템에 설치되어 있지 않습니다. 설치 후 다시 실행하세요.")
    print("https://ffmpeg.org/download.html 또는 choco install ffmpeg")
    sys.exit(1)

def get_next_filename(prefix, ext="txt"):
    today = datetime.datetime.now().strftime("%Y%m%d")
    files = glob.glob(f"{prefix}{today}_*.{ext}")
    nums = [int(f.split("_")[-1].split(".")[0]) for f in files if f.split("_")[-1].split(".")[0].isdigit()]
    next_num = max(nums) + 1 if nums else 1
    return f"{prefix}{today}_{next_num:02d}.{ext}"

def transcribe_and_save(audio_path, out_prefix="transcript_"):
    model = whisper.load_model("base")
    print(f"음성 파일 인식 중: {audio_path}")
    result = model.transcribe(audio_path)
    text = result["text"].strip()
    out_file = get_next_filename(out_prefix)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"텍스트가 {out_file} 파일로 저장되었습니다.")
    return out_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python whisper_transcribe.py <음성파일경로>")
        sys.exit(1)
    audio_path = sys.argv[1]
    if not os.path.exists(audio_path):
        print(f"❌ 파일을 찾을 수 없습니다: {audio_path}")
        sys.exit(1)
    try:
        transcribe_and_save(audio_path)
    except Exception as e:
        print(f"❌ 음성 인식 중 오류 발생: {e}")
        sys.exit(1)
