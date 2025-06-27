import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from subtitle_creator import extract_audio_from_video, generate_subtitles, create_output_directory

class SubtitleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Altyazı Oluşturucu")
        self.root.geometry("500x350")
        self.root.resizable(False, False)

        self.video_path = tk.StringVar()
        self.output_dir = tk.StringVar(value="output")
        self.model_name = tk.StringVar(value="base")
        self.models = ["tiny", "base", "small", "medium", "large"]

        self.create_widgets()

    def create_widgets(self):
        padding = {'padx': 10, 'pady': 5}

        # Video dosyası seçimi
        tk.Label(self.root, text="Video Dosyası:").grid(row=0, column=0, sticky="e", **padding)
        tk.Entry(self.root, textvariable=self.video_path, width=40).grid(row=0, column=1, **padding)
        tk.Button(self.root, text="Gözat", command=self.browse_video).grid(row=0, column=2, **padding)

        # Çıktı klasörü seçimi
        tk.Label(self.root, text="Çıktı Klasörü:").grid(row=1, column=0, sticky="e", **padding)
        tk.Entry(self.root, textvariable=self.output_dir, width=40).grid(row=1, column=1, **padding)
        tk.Button(self.root, text="Seç", command=self.browse_output_dir).grid(row=1, column=2, **padding)

        # Model seçimi
        tk.Label(self.root, text="Whisper Modeli:").grid(row=2, column=0, sticky="e", **padding)
        ttk.Combobox(self.root, textvariable=self.model_name, values=self.models, state="readonly").grid(row=2, column=1, **padding)

        # Başlat butonu
        tk.Button(self.root, text="Altyazı Oluştur", command=self.start_process).grid(row=3, column=1, pady=15)

        # Sonuç/Log kutusu
        self.log_text = tk.Text(self.root, height=10, width=60, state="disabled")
        self.log_text.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

    def browse_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video Dosyaları", "*.mp4;*.mkv;*.avi;*.mov;*.wmv")])
        if path:
            self.video_path.set(path)

    def browse_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir.set(path)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def start_process(self):
        video = self.video_path.get()
        output = self.output_dir.get()
        model = self.model_name.get()

        if not video or not os.path.isfile(video):
            messagebox.showerror("Hata", "Geçerli bir video dosyası seçin.")
            return
        if not video.lower().endswith((".mp4", ".mkv", ".avi", ".mov", ".wmv")):
            messagebox.showerror("Hata", "Desteklenmeyen video formatı.")
            return
        if not output:
            messagebox.showerror("Hata", "Çıktı klasörü belirtin.")
            return
        if model not in self.models:
            messagebox.showerror("Hata", "Geçersiz model seçimi.")
            return

        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.log("İşlem başlatılıyor...")
        threading.Thread(target=self.process_subtitles, args=(video, output, model), daemon=True).start()

    def process_subtitles(self, video, output, model):
        try:
            self.log(f"Çıktı klasörü kontrol ediliyor: {output}")
            create_output_directory(output)
            audio_path = os.path.join(output, "extracted_audio.wav")
            subtitle_path = os.path.join(output, "subtitles.srt")

            self.log("Videodan ses çıkarılıyor...")
            if not extract_audio_from_video(video, audio_path):
                self.log("Ses çıkarma başarısız.")
                return
            self.log("Ses çıkarma tamamlandı.")

            self.log(f"Whisper modeli ile transkripsiyon başlatılıyor ({model})...")
            if not generate_subtitles(audio_path, subtitle_path, model_name=model):
                self.log("Altyazı oluşturma başarısız.")
                return
            self.log(f"Altyazı dosyası oluşturuldu: {subtitle_path}")

            if os.path.exists(audio_path):
                os.remove(audio_path)
                self.log(f"Geçici ses dosyası silindi: {audio_path}")
            self.log("İşlem tamamlandı!")
        except Exception as e:
            self.log(f"Hata: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleApp(root)
    root.mainloop() 