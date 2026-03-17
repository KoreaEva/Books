#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper 음성 텍스트 추출기 (회의 요약용)

Whisper(STT) 기능 구현 요구사항:
1) 사용자로부터 오디오 파일 경로를 입력받는다.
2) Whisper 모델을 사용해 음성을 받아쓴다. 언어는 자동으로 감지하며, 모델 크기는 기본으로 small을 사용한다.
3) 파일이 없거나 Whisper/FFmpeg 미설치 시 예외를 처리하고 안내 메시지를 출력한다.
4) transcribe() 함수 단일 구조로 작성하며 인식된 결과를 텍스트 파일로 저장한다.
5) 성공 시 받아쓴 텍스트를 반환하고, 실패 시 사용자 친화적인 오류 메시지를 제공한다.
6) 파일명은 날짜 + 일련번호 형식으로 자동 생성한다.
"""

import os
import sys
import datetime
import glob
from pathlib import Path

# 필수 패키지 가져오기 및 설치 확인
try:
    import whisper
    print("✅ Whisper 패키지가 설치되어 있습니다.")
except ImportError:
    print("❌ Whisper 패키지가 설치되어 있지 않습니다.")
    print("📦 설치 명령어: pip install -U openai-whisper")
    print("🔗 GitHub: https://github.com/openai/whisper")
    sys.exit(1)

# FFmpeg 설치 확인
from shutil import which
if which("ffmpeg") is None:
    print("⚠️  FFmpeg가 설치되어 있지 않습니다.")
    print("🔧 일부 오디오 형식에서 문제가 발생할 수 있습니다.")
    print("🔧 설치 방법:")
    print("   Windows: choco install ffmpeg")
    print("   Mac: brew install ffmpeg") 
    print("   Linux: sudo apt install ffmpeg")
    print("✅ WAV 파일은 FFmpeg 없이도 처리 가능합니다.")
else:
    print("✅ FFmpeg가 설치되어 있습니다.")

def create_filename(output_dir=".", prefix="meeting_", extension="txt"):
    """
    날짜 + 일련번호 형식의 파일명을 생성합니다.
    
    Args:
        output_dir (str): 출력 디렉토리 경로
        prefix (str): 파일명 접두사
        extension (str): 파일 확장자
        
    Returns:
        str: 생성된 파일 경로 (예: meeting_20251015_01.txt)
    """
    # 오늘 날짜 (YYYYMMDD 형식)
    today_date = datetime.datetime.now().strftime("%Y%m%d")
    
    # 해당 날짜의 기존 파일들 검색
    search_pattern = os.path.join(output_dir, f"{prefix}{today_date}_*.{extension}")
    existing_files = glob.glob(search_pattern)
    
    # 일련번호 추출 및 다음 번호 계산
    serial_nums = []
    for file_path in existing_files:
        filename = os.path.basename(file_path)
        try:
            # 파일명에서 일련번호 추출 (예: meeting_20251015_01.txt -> 01)
            parts = filename.split(f"{today_date}_")
            if len(parts) > 1:
                serial_str = parts[1].split(f".{extension}")[0]
                if serial_str.isdigit():
                    serial_nums.append(int(serial_str))
        except (IndexError, ValueError):
            continue
    
    # 다음 일련번호 결정
    next_serial = max(serial_nums) + 1 if serial_nums else 1
    
    # 파일명 생성 (일련번호는 2자리 패딩)
    filename = f"{prefix}{today_date}_{next_serial:02d}.{extension}"
    return os.path.join(output_dir, filename)

def transcribe(audio_file_path, output_directory=".", whisper_model="small"):
    """
    음성 파일을 텍스트로 변환하고 파일에 저장하는 함수
    
    Args:
        audio_file_path (str): 입력 음성 파일 경로
        output_directory (str): 출력 디렉토리
        whisper_model (str): Whisper 모델 크기
        
    Returns:
        dict: 처리 결과 정보
        {
            'success': bool,
            'text': str,
            'output_file': str,
            'message': str,
            'language': str
        }
    """
    print("🎤 Whisper 음성-텍스트 변환 시작")
    print("=" * 60)
    
    try:
        # 1단계: 입력 파일 유효성 검사
        print("📁 입력 파일 검증...")
        audio_path = Path(audio_file_path)
        
        if not audio_path.exists():
            return {
                'success': False,
                'text': '',
                'output_file': '',
                'message': f'❌ 파일이 존재하지 않습니다: {audio_file_path}',
                'language': ''
            }
        
        # 지원되는 오디오 형식 확인
        supported_extensions = {
            '.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', 
            '.wma', '.mp4', '.avi', '.mov', '.mkv'
        }
        
        file_ext = audio_path.suffix.lower()
        if file_ext not in supported_extensions:
            return {
                'success': False,
                'text': '',
                'output_file': '',
                'message': f'❌ 지원되지 않는 파일 형식: {file_ext}\n' +
                          f'🎯 지원 형식: {", ".join(sorted(supported_extensions))}',
                'language': ''
            }
        
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        print(f"✅ 파일 검증 완료")
        print(f"📄 파일명: {audio_path.name}")
        print(f"📊 파일 크기: {file_size_mb:.2f} MB")
        
        # 2단계: 출력 디렉토리 준비
        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 3단계: Whisper 모델 로딩
        print(f"🧠 Whisper 모델 로드 중... (모델: {whisper_model})")
        
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if whisper_model not in valid_models:
            return {
                'success': False,
                'text': '',
                'output_file': '',
                'message': f'❌ 잘못된 모델명: {whisper_model}\n' +
                          f'🎯 사용 가능한 모델: {", ".join(valid_models)}',
                'language': ''
            }
        
        try:
            model = whisper.load_model(whisper_model)
            print("✅ 모델 로드 성공")
        except Exception as e:
            return {
                'success': False,
                'text': '',
                'output_file': '',
                'message': f'❌ 모델 로드 실패: {str(e)}',
                'language': ''
            }
        
        # 4단계: 음성 인식 수행
        print("🎵 음성 인식 진행 중...")
        print("⏳ 파일 크기에 따라 처리 시간이 소요됩니다...")
        
        try:
            # Whisper로 음성 인식 (언어 자동 감지)
            result = model.transcribe(str(audio_path), language=None, fp16=False)
            
            transcribed_text = result["text"].strip()
            detected_lang = result.get("language", "unknown")
            
            print("✅ 음성 인식 완료")
            print(f"🌍 감지된 언어: {detected_lang}")
            print(f"📝 텍스트 길이: {len(transcribed_text)} 문자")
            
        except Exception as e:
            return {
                'success': False,
                'text': '',
                'output_file': '',
                'message': f'❌ 음성 인식 실패: {str(e)}',
                'language': ''
            }
        
        # 5단계: 텍스트 검증
        if not transcribed_text:
            return {
                'success': False,
                'text': '',
                'output_file': '',
                'message': '⚠️  음성에서 텍스트를 추출하지 못했습니다.\n' +
                          '🔍 오디오 파일에 음성이 포함되어 있는지 확인해주세요.',
                'language': detected_lang
            }
        
        # 6단계: 텍스트 파일 저장
        output_file = create_filename(
            output_dir=str(output_path),
            prefix="meeting_",
            extension="txt"
        )
        
        print(f"💾 텍스트 파일 저장: {os.path.basename(output_file)}")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # 파일 헤더 정보 작성
                f.write("# 음성 텍스트 변환 결과\n")
                f.write(f"# 원본 파일: {audio_path.name}\n")
                f.write(f"# 변환 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 감지 언어: {detected_lang}\n")
                f.write(f"# 모델 크기: {whisper_model}\n")
                f.write(f"# 파일 크기: {file_size_mb:.2f} MB\n")
                f.write(f"# 텍스트 길이: {len(transcribed_text)} 문자\n")
                f.write("=" * 60 + "\n\n")
                
                # 변환된 텍스트 저장
                f.write(transcribed_text)
            
            print(f"✅ 파일 저장 완료: {output_file}")
            
            return {
                'success': True,
                'text': transcribed_text,
                'output_file': output_file,
                'message': f'🎉 음성 텍스트 변환 성공!\n📁 저장 파일: {os.path.basename(output_file)}',
                'language': detected_lang
            }
            
        except Exception as e:
            return {
                'success': False,
                'text': transcribed_text,
                'output_file': '',
                'message': f'❌ 파일 저장 실패: {str(e)}',
                'language': detected_lang
            }
    
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'output_file': '',
            'message': f'❌ 예상치 못한 오류: {str(e)}',
            'language': ''
        }

def main():
    """메인 실행 함수"""
    print("🎤 Whisper 음성 텍스트 추출기 (회의용)")
    print("=" * 60)
    
    # 명령행 파라미터 처리
    if len(sys.argv) < 2:
        print("📖 사용 방법:")
        print("   python 08.meeting_summary.py <음성파일> [출력폴더] [모델크기]")
        print("\n📝 사용 예시:")
        print("   python 08.meeting_summary.py meeting.mp3")
        print("   python 08.meeting_summary.py audio.wav ./output")
        print("   python 08.meeting_summary.py recording.m4a ./transcripts medium")
        print("\n🎯 지원 모델: tiny, base, small, medium, large")
        print("🎯 지원 형식: mp3, wav, m4a, flac, aac, ogg, wma, mp4, avi, mov")
        print("🎯 파일명 형식: meeting_YYYYMMDD_NN.txt")
        return
    
    # 파라미터 파싱
    audio_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    model_size = sys.argv[3] if len(sys.argv) > 3 else "small"
    
    print(f"🎵 입력 파일: {audio_file}")
    print(f"📁 출력 디렉토리: {output_dir}")
    print(f"🧠 모델 크기: {model_size}")
    print()
    
    # 음성 텍스트 변환 실행
    result = transcribe(audio_file, output_dir, model_size)
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("📊 변환 결과")
    print("=" * 60)
    print(result['message'])
    
    if result['success']:
        print(f"\n🌍 언어: {result['language']}")
        
        # 텍스트 미리보기
        text = result['text']
        if text:
            print("📖 텍스트 미리보기:")
            preview_length = 150
            if len(text) > preview_length:
                preview = text[:preview_length] + "..."
            else:
                preview = text
            
            print(f"   {preview}")
            
            if len(text) > preview_length:
                print(f"\n📏 전체 텍스트 길이: {len(text)} 문자")
    
    print("=" * 60)

# 대화형 모드 함수
def interactive_mode():
    """대화형 모드로 실행"""
    print("🎤 Whisper 음성 텍스트 추출기 - 대화형 모드")
    print("=" * 60)
    
    while True:
        try:
            print("\n📁 음성 파일 경로를 입력하세요 (종료: q 또는 quit):")
            audio_input = input("> ").strip()
            
            if audio_input.lower() in ['q', 'quit', '종료']:
                print("👋 프로그램을 종료합니다.")
                break
            
            if not audio_input:
                print("⚠️  파일 경로를 입력해주세요.")
                continue
            
            # 출력 디렉토리 선택
            print("📂 출력 디렉토리 (기본값: 현재 폴더, Enter로 건너뛰기):")
            output_input = input("> ").strip()
            output_dir = output_input if output_input else "."
            
            # 모델 크기 선택
            print("🧠 모델 크기 (tiny/base/small/medium/large, 기본값: small):")
            model_input = input("> ").strip()
            model_size = model_input if model_input else "small"
            
            print(f"\n🚀 변환 시작...")
            result = transcribe(audio_input, output_dir, model_size)
            
            print(f"\n{result['message']}")
            
            if result['success']:
                print(f"🌍 언어: {result['language']}")
                if result['text']:
                    preview = result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
                    print(f"📖 미리보기: {preview}")
        
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    # 명령행 인자가 있으면 일반 모드, 없으면 대화형 모드
    if len(sys.argv) > 1:
        main()
    else:
        interactive_mode()
