# นำเข้า Library ต่างๆที่ต้องใช้งาน
import os, re, threading
import customtkinter as tk
from typing import TypedDict
from yt_dlp import YoutubeDL
from tkinter import filedialog, messagebox

# ตั้งค่าธีมเริ่มต้นให้กับแอปพลิเคชัน โดยอ่านไฟล์ 'theme.json' จากโฟลเดอร์ปัจจุบัน
tk.set_default_color_theme( os.path.join( os.getcwd(), 'theme.json' ) )

# สร้างโครงสร้างข้อมูลสำหรับการตั้งค่าแอปพลิเคชัน
class ConfigureOption( TypedDict ):
    name: str  # ชื่อแอปพลิเคชัน
    size: str  # ขนาดหน้าต่าง

# คลาสหลักสำหรับเริ่มแอปพลิเคชัน
class InitializeApplication:

    # ตัวสร้างเริ่มต้น รับหน้าต่างหลักและสร้าง UI
    def __init__( self, app:tk.CTk ):
        self.app = app  # กำหนดตัวแอป
        self.isDownloading = False  # ตัวบ่งชี้สถานะการดาวน์โหลด
        self.createApplicationUI()  # เรียกใช้ฟังก์ชันสร้าง UI

    # ฟังก์ชันสำหรับสร้าง UI ของแอปพลิเคชัน
    def createApplicationUI( self ):

        window = self.app  # กำหนดหน้าต่างหลัก

        # ตัวแปรเก็บเส้นทางการดาวน์โหลด
        export_path = tk.StringVar( value=os.path.join( os.getcwd(), "download" ) )
        # ตัวแปรเก็บลิงก์ YouTube
        youtubeLink = tk.StringVar( value="" )

        # ฟังก์ชันสำหรับเปิดหน้าต่างเลือกโฟลเดอร์
        def select_folder( event = None ):
            folder_selected = filedialog.askdirectory()  # เปิดหน้าต่างเลือกโฟลเดอร์
            if folder_selected:
                export_path.set( folder_selected )  # ถ้าเลือกโฟลเดอร์ ให้ตั้งค่าเส้นทางเป็นโฟลเดอร์ที่เลือก
        
        # สร้างเฟรมสำหรับกรอกที่อยู่การบันทึกไฟล์
        wigedFrameExport = tk.CTkFrame(
            window, # กำหนดพื้นที่หลัก
            fg_color="transparent" # ลบสีพื้นหลัง
        )
        # ประกอบเฟรมเข้ากับพื้นที่หลัก
        wigedFrameExport.pack(
            fill="both", # กำหนดให้มีขนาดกว้างเต็ม
            expand=False, # กำหนดให้สูงไม่เต็มจอ
            padx=20, # เพิ่มระยะห่างแกน x
            pady=(20,0) # เพิ่มระยะห่างแกน y บน/ล่าง
        )

        # ช่องกรอกที่อยู่โฟลเดอร์สำหรับการดาวน์โหลด
        exportWiged = tk.CTkEntry(
            wigedFrameExport, # กำหนดพื้นที่หลัก
            height=36, # กำหนดสูง
            border_width=0, # กำหนดขอบ
            textvariable=export_path,  # เชื่อมกับตัวแปรเส้นทาง
            state="readonly"  # ตั้งเป็น readonly ห้ามแก้ไข
        )
        # ประกอบเข้ากับพื้นที่หลัก
        exportWiged.pack(
            fill="both", # กว้างเต็มจอ
            padx=14, # เพิ่มระยะห่างแกน x
            pady=14 # เพิ่มระยะห่างแกน y
        )
        exportWiged.bind( "<Button-1>", select_folder )  # เพิ่มอีเวนท์คลิกเพื่อเลือกโฟลเดอร์

        # ฟังก์ชันที่ทำงานเมื่อกดปุ่มบนแป้นพิมพ์ในช่องลิงก์ YouTube
        def onLinkEntryKeyUp( event = None ):
            youtubeLink.set( linkWiged.get() )  # อัปเดตค่าลิงก์

        # สร้างเฟรมสำหรับกรอกลิงก์ YouTube
        wigedFrameLink = tk.CTkFrame(
            window, # พื้นที่หลัก
            fg_color="transparent" # ลบสีพื้นหลัง
        )
        # ประกอบเข้ากับพื้นที่หลัก
        wigedFrameLink.pack(
            fill="both", # กำหนดเต็มจอ กว้าง
            expand=False, # กำหนดไม่เต็มจอ สูง
            padx=20, # ระยะห่างซ้ายขวา
            pady=(15,0) # ระยะห่างบนล่าง
        )
        # ช่องกรอกลิงก์ YouTube
        linkWiged = tk.CTkEntry(
            wigedFrameLink, # พื้นที่หลัก
            height=36, # สูง
            border_width=0, # ขนาดเส้นขอบ
            placeholder_text="Enter Youtube URL"  # ข้อความแนะนำการกรอก
        )
        # ประกอบเข้ากับพื้นที่หลัก
        linkWiged.pack(
            fill="both", # กำหนดเต็มจอ กว้าง
            padx=14, # ระยะห่าง ซ้ายขวา
            pady=14 # ระยะห่าง บนล่าง
        )
        linkWiged.bind( "<KeyRelease>", onLinkEntryKeyUp )  # เพิ่มอีเวนท์ตรวจจับเมื่อกดปุ่มบนแป้นพิมพ์

        # ฟังก์ชันตรวจสอบว่าลิงก์ YouTube ถูกต้องหรือไม่
        def validYouTubeLink( url:str ):
            youtube_patterns = [
                r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$',  # ลิงก์ YouTube ปกติ
                r'(https?://)?(www\.)?youtube\.com/shorts/.+$',         # ลิงก์ YouTube Shorts
                r'(https?://)?(music\.)?youtube\.com/.+$'               # ลิงก์ YouTube Music
            ]
            for pattern in youtube_patterns:
                if re.match( pattern, url ):
                    return True
            return False  # ถ้าไม่ตรงกับแพทเทิร์นใดเลย ถือว่าไม่ถูกต้อง
        
        # ฟังก์ชันรีเซ็ต logger
        def ResetLogger():
            logger.configure( text="" ) # กำหนดให้แสดงการประมวลผลเป็นค่าว่าง

        # ฟังก์ชันแสดงความคืบหน้าในการดาวน์โหลด
        def ProgressLogger( target = None ):

            # ถ้าไม่มีค่าส่งมาจะไม่ดำเนินการต่อ
            if target is None or 'status' not in target:
                return
            
            # ถ้ากำลังดาวน์โหลด
            if target['status'] == "downloading":
                downloaded_bytes = target.get('downloaded_bytes', 0)  # ขนาดที่ดาวน์โหลดแล้ว
                total_bytes = target.get('total_bytes', 0)  # ขนาดไฟล์ทั้งหมด
                if total_bytes > 0:
                    percent = ( downloaded_bytes / total_bytes ) * 100  # คำนวณเปอร์เซ็นต์
                else:
                    percent = 0
                progress_text = f"Download progress: {percent:.2f}% ({downloaded_bytes / (1024 * 1024):.2f} MB of {total_bytes / (1024 * 1024):.2f} MB)" # ส่งออกการคำนวณ
                logger.configure( text=progress_text ) # ตั้งค่าให้แสดงการคำนวณ
                logger.update_idletasks()  # อัปเดทการแสดงผล
            # ถ้าดาวน์โหลดสำเร็จ
            elif target['status'] == "finished":
                logger.configure( text="Download video successfully." ) # แสดงข้อความ
                window.after( 3000, ResetLogger )  # รอ 3 วินาทีก่อนรีเซ็ตข้อความ
                self.isDownloading = False  # ตั้งค่าสถานะดาวน์โหลดเป็น False

        # คลาส NoLogger สำหรับปิดการแจ้งเตือน logger ไม่ให้แสดงที่คอลโซล
        class NoLogger( object ):
            def debug( self, _ ):
                pass
            def warning( self, _ ):
                pass
            def error( self, _ ):
                pass

        # ฟังก์ชันสำหรับดาวน์โหลดวิดีโอ YouTube
        def DownloadYouTubeVideo( event = None ):

            # ดักจับกำลังดาวน์โหลด
            if self.isDownloading:
                messagebox.showwarning("Youtube Downloader Alert", "Downloading, please wait") # แสดงข้อความแจ้งเตือน
                return

            # ฟังก์ชันสำหรับเรียกใช้การดาวน์โหลดในเธรดใหม่
            def download_thread():
                self.isDownloading = True # ตั้งค่าให้มีการดาวน์โหลดอยู่
                logger.configure(text="Download metadata from API") # แสดงข้อความ
                logger.update_idletasks() # อัปเดทการแสดงผล

                link = youtubeLink.get()  # รับลิงก์ YouTube
                out = export_path.get()  # รับเส้นทางการบันทึก
                isYoutubeLink = validYouTubeLink(link)  # ตรวจสอบว่าลิงก์ถูกต้องหรือไม่

                if isYoutubeLink:

                    if not os.path.exists(out):
                        os.makedirs(out)  # สร้างโฟลเดอร์ถ้ายังไม่มี
                        logger.configure(text="Created folder")
                        logger.update_idletasks()

                    try:
                        # ตั้งค่าการดาวน์โหลด
                        ydl_opts = {
                            'noplaylist': True,
                            'logger': NoLogger(),
                            'nocheckcertificate': True,
                            'cookiefile': 'cookies.txt',
                            'format': 'best[ext=mp4]/best',
                            'progress_hooks': [ProgressLogger],
                            'outtmpl': os.path.join(out, '%(title)s.%(ext)s'),
                            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        }
                        with YoutubeDL(ydl_opts) as ytdl:
                            logger.configure(text="Starting download")
                            ytdl.download([link])  # เริ่มดาวน์โหลด
                    except Exception as e:
                        logger.configure(text=f"Failed to download video: {str(e)}")  # แสดงข้อผิดพลาด -ถ้ามี-
                    finally:
                        self.isDownloading = False # เสร็จขั้นตอนการดาวน์โหลด และเปลี่ยนสถานะเป็นว่างจากการดาวน์โหลด
                else:
                    messagebox.showerror("Youtube Downloader Alert", "Please enter a valid YouTube URL.")  # แจ้งเตือนเมื่อ URL ไม่ถูกต้อง
                    linkWiged.delete(0, tk.END)  # ล้างช่องลิงก์ YouTube
            threading.Thread(target=download_thread).start()  # เริ่มการดาวน์โหลดในเธรดใหม่

        # ปุ่มสำหรับดาวน์โหลดวิดีโอ
        tk.CTkButton(
            window, text="Download", height=30, command=DownloadYouTubeVideo
        ).pack( pady=(10,0) )

        # ป้ายข้อความสำหรับเลือกโฟลเดอร์
        tk.CTkLabel( 
            window,
            text=" Select Export Folder ",
            font=( "Arial", 10 ),
            height=12,
            anchor="w"
        ).place( relx=0.1, rely=0.06 )

        # ป้ายข้อความสำหรับดาวน์โหลด YouTube
        tk.CTkLabel( 
            window,
            text=" Youtube Download ",
            font=( "Arial", 10 ),
            height=12,
            anchor="w"
        ).place( relx=0.1, rely=0.385 )

        # ป้ายข้อความแสดงสถานะการดาวน์โหลด
        logger = tk.CTkLabel(
            window,
            font=( "Roboto", 12 ),
            text=""
        )
        logger.place( relx=0.05, rely=0.88 )
    
    # ฟังก์ชันตั้งค่าโหมดมืดหรือสว่าง
    def setDarkMode( self, dark:bool = False ):
        if dark:
            tk.set_appearance_mode( 'dark' )  # ตั้งโหมดมืด
        else:
            tk.set_appearance_mode( 'light' )  # ตั้งโหมดสว่าง
    
    # ฟังก์ชันสำหรับปิดการปรับขนาดหน้าต่าง
    def disbleResize( self, resize:bool = False ):
        if not resize:
            self.app.resizable( False, False )  # ปิดการปรับขนาด

    # ฟังก์ชันเริ่มต้นการทำงานของแอปพลิเคชัน
    def start( self ):
        self.app.mainloop()

    # ฟังก์ชันสำหรับกำหนดค่าการตั้งค่าของแอปพลิเคชัน
    def configure( self, options:ConfigureOption ):
        self.app.title( options.get('name') or "Custom TKinter Application" )  # ตั้งชื่อแอป
        self.app.geometry( options.get('size') or "450x240+420+200" )  # ตั้งขนาดหน้าต่าง

# จุดเริ่มต้นของโปรแกรม
if __name__ == "__main__":
    app = InitializeApplication( tk.CTk() )  # สร้างอินสแตนซ์ของแอปพลิเคชัน
    app.configure( { 'name':'YouTube Downloader' } )  # ตั้งค่าชื่อแอป
    app.disbleResize()  # ปิดการปรับขนาด
    app.start()  # เริ่มต้นแอปพลิเคชัน
