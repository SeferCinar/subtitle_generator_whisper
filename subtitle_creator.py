import subprocess
import whisper
import os
from datetime import timedelta

def extract_audio_from_video(video_path, audio_path):
    """Videodan sesi çıkarır ve WAV formatında kaydeder."""
    try:
        subprocess.run([
            "ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path
        ], check=True, capture_output=True, text=True)
        print(f"Ses dosyası başarıyla oluşturuldu: {audio_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ses çıkarma hatası: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Hata: FFmpeg sistemde bulunamadı. Lütfen FFmpeg'i yükleyin ve PATH'e ekleyin.")
        return False

def generate_subtitles(audio_path, subtitle_path, model_name="base", language="tr"):
    """Whisper ile transkripsiyon yapar ve SRT formatında altyazı üretir."""
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(audio_path, verbose=False, language=language)
        
        with open(subtitle_path, "w", encoding="utf-8") as srt_file:
            for i, segment in enumerate(result["segments"], start=1):
                start_time = timedelta(seconds=segment["start"])
                end_time = timedelta(seconds=segment["end"])
                start_str = f"{int(start_time.total_seconds() // 3600):02d}:{int((start_time.total_seconds() % 3600) // 60):02d}:{int(start_time.total_seconds() % 60):02d},{int((start_time.total_seconds() % 1) * 1000):03d}"
                end_str = f"{int(end_time.total_seconds() // 3600):02d}:{int((end_time.total_seconds() % 3600) // 60):02d}:{int(end_time.total_seconds() % 60):02d},{int((end_time.total_seconds() % 1) * 1000):03d}"
                text = segment["text"].strip()
                srt_file.write(f"{i}\n{start_str} --> {end_str}\n{text}\n\n")
        
        print(f"Altyazı dosyası başarıyla oluşturuldu: {subtitle_path}")
        return True
    except Exception as e:
        print(f"Altyazı oluşturma hatası: {e}")
        return False

def create_output_directory(output_dir):
    """Çıktı klasörünü oluşturur."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Çıktı klasörü oluşturuldu: {output_dir}")

def validate_video_path(video_path):
    """Video dosyasının varlığını ve geçerliliğini kontrol eder."""
    if not os.path.isfile(video_path):
        print(f"Hata: '{video_path}' dosyası bulunamadı.")
        return False
    if not video_path.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv')):
        print(f"Hata: '{video_path}' desteklenen bir video formatı değil.")
        return False
    return True

def display_menu():
    """Menüyü gösterir."""
    print("\n=== Video Altyazı Oluşturma Uygulaması ===")
    print("1. Video dosyası seç ve altyazı oluştur")
    print("2. Çıkış")
    print("=======================================")

def main():
    video_path = ""
    output_dir = "output"
    model_name = "base"
    models = ["tiny", "base", "small", "medium", "large"]

    while True:
        display_menu()
        choice = input("Seçiminizi yapın (1-2): ").strip()

        if choice == "1":
            # Video dosyasını al
            video_path = input("Video dosyasının tam yolunu girin (ör. C:/Videos/ornek.mp4): ").strip()
            if not validate_video_path(video_path):
                continue

            # Çıktı klasörünü al
            output_dir = input("Çıktı klasörünü girin (varsayılan 'output'): ").strip() or "output"
            
            # Video dosyasının adını al (uzantısız)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            
            # Çıktı klasörünü video adına göre oluştur
            final_output_dir = os.path.join(output_dir, video_name)
            create_output_directory(final_output_dir)

            # Model seçimini al
            print("\nKullanılabilir Whisper modelleri:", ", ".join(models))
            model_choice = input(f"Model seçin (varsayılan '{model_name}'): ").strip().lower() or model_name
            if model_choice not in models:
                print(f"Hata: Geçersiz model. Varsayılan '{model_name}' kullanılacak.")
            else:
                model_name = model_choice

            # Dosya yollarını oluştur
            audio_path = os.path.join(final_output_dir, f"{video_name}_audio.wav")
            subtitle_path = os.path.join(final_output_dir, f"{video_name}.srt")

            # İşlemi başlat
            print("\nİşlem başlatılıyor...")
            if extract_audio_from_video(video_path, audio_path):
                if generate_subtitles(audio_path, subtitle_path, model_name=model_name):
                    print("Altyazı oluşturma işlemi tamamlandı!")
                # Geçici ses dosyasını sil
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    print(f"Geçici ses dosyası silindi: {audio_path}")
            input("\nDevam etmek için bir tuşa basın...")

        elif choice == "2":
            print("Uygulamadan çıkılıyor. İyi günler!")
            break
        else:
            print("Geçersiz seçim. Lütfen 1 veya 2 girin.")

if __name__ == "__main__":
    main()