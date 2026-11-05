from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import fitz
from PIL import Image
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter.font as tkfont


class PDFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF → JPG 변환기")
        self.root.geometry("1200x800")
        self.root.minsize(1100, 750)

        self.pdf_files = set()

        self.file_cards = {}

        self.selected_file = None

        self.create_ui()

    def create_ui(self):

        BG = "#0f1117"
        CARD = "#161b22"
        HOVER = "#21262d"
        BORDER = "#30363d"
        TEXT = "#f0f6fc"
        SUB = "#8b949e"
        ACCENT = "#3b82f6"

        self.root.configure(bg=BG)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Modern.TButton",
            background=ACCENT,
            foreground="white",
            borderwidth=0,
            padding=(18, 10),
            font=("Arial", 10)
        )

        style.map(
            "Modern.TButton",
            background=[("active", "#2563eb")]
        )

        style.configure(
            "Secondary.TButton",
            background=HOVER,
            foreground=TEXT,
            borderwidth=0,
            padding=(18, 10)
        )

        style.map(
            "Secondary.TButton",
            background=[("active", "#2d333b")]
        )

        style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor="#1c2128",
            background=ACCENT,
            borderwidth=0,
            thickness=8
        )

        style.configure(
            "Success.Horizontal.TProgressbar",
            troughcolor="#1c2128",
            background="#22c55e",
            borderwidth=0,
            thickness=8
        )

        STATUS_FONT = ("Arial", 15)

        # ==========================
        # HEADER
        # ==========================

        header = tk.Frame(
            self.root,
            bg=BG
        )
        header.pack(
            fill="x",
            padx=30,
            pady=(25, 15)
        )

        tk.Label(
            header,
            text="PDF → JPG Converter",
            font=("Arial", 24),
            fg=TEXT,
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Drag PDFs and convert instantly.",
            font=("Arial", 10),
            fg=SUB,
            bg=BG
        ).pack(anchor="w")


        # ==========================
        # 저장위치
        # ==========================

        save_frame = tk.Frame(
            self.root,
            bg=BG
        )

        save_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 20)
        )

        tk.Label(
            save_frame,
            text="Save Location",
            fg=SUB,
            bg=BG,
            font=("Arial", 9)
        ).pack(anchor="w")

        self.save_option = tk.StringVar(
            value="pdf"
        )

        radio_frame = tk.Frame(
            save_frame,
            bg=BG
        )

        radio_frame.pack(anchor="w", pady=5)

        tk.Radiobutton(
            radio_frame,
            text="Original Folder",
            variable=self.save_option,
            value="pdf",
            bg=BG,
            fg=TEXT,
            selectcolor=CARD,
            activebackground=BG,
            activeforeground=TEXT
        ).pack(side="left")

        tk.Radiobutton(
            radio_frame,
            text="Desktop",
            variable=self.save_option,
            value="desktop",
            bg=BG,
            fg=TEXT,
            selectcolor=CARD,
            activebackground=BG,
            activeforeground=TEXT
        ).pack(
            side="left",
            padx=20
        )

        content_frame = tk.Frame(
            self.root,
            bg=BG
        )

        content_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0,20)
        )

        left_panel = tk.Frame(
            content_frame,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        left_panel.pack(
            side="left",
            fill="both",
            expand=True
        )

        drop_container = tk.Frame(
            left_panel,
            bg=CARD
        )

        drop_container.place(
            relx=0.5,
            rely=0.42,
            anchor="center"
        )

        tk.Label(
            drop_container,
            text="⬇",
            font=("Segoe UI Emoji",52),
            bg=CARD,
            fg=ACCENT
        ).pack()

        tk.Label(
            drop_container,
            text="Drop PDF Files",
            font=("Arial",20),
            bg=CARD,
            fg=TEXT
        ).pack()

        tk.Label(
            drop_container,
            text="Drag files or folders here",
            bg=CARD,
            fg=SUB
        ).pack()

        left_panel.drop_target_register(DND_FILES)

        left_panel.dnd_bind(
            "<<Drop>>",
            self.on_drop
        )

        right_panel = tk.Frame(
            content_frame,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1,
            width=420
        )

        right_panel.pack(
            side="left",
            fill="y",
            padx=(15,0)
        )

        right_panel.pack_propagate(False)

        self.file_header = tk.Label(
            right_panel,
            text="Files (0)",
            bg=CARD,
            fg=TEXT,
            font=("Arial",12)
        )

        self.file_header.pack(
            anchor="w",
            padx=15,
            pady=15
        )

        canvas = tk.Canvas(
            right_panel,
            bg=CARD,
            highlightthickness=0
        )



        self.file_container = tk.Frame(
            canvas,
            bg=CARD
        )

        self.file_container.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window(
            (0,0),
            window=self.file_container,
            anchor="nw"
        )



        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )



        # ==========================
        # PROGRESS
        # ==========================

        self.progress = ttk.Progressbar(
            self.root,
            style="Modern.Horizontal.TProgressbar",
            mode="determinate"
        )

        self.progress.pack(
            fill="x",
            padx=30
        )

        self.progress_label = tk.Label(
            self.root,
            text="READY",
            bg=BG,
            fg="#8b949e",
            font=STATUS_FONT
        )

        self.progress_label.pack(
            anchor="w",
            padx=30,
            pady=(5, 15)
        )

        # ==========================
        # BUTTON
        # ==========================

        button_frame = tk.Frame(
            self.root,
            bg=BG
        )

        button_frame.pack(
            fill="x",
            padx=30,
            pady=(0, 25)
        )

        ttk.Button(
            button_frame,
            text="Remove Selected",
            style="Secondary.TButton",
            command=self.remove_selected_file
        ).pack(
            side="right",
            padx=10
        )

        ttk.Button(
            button_frame,
            text="Clear All",
            style="Secondary.TButton",
            command=self.clear_list
        ).pack(
            side="right",
            padx=10
        )

        ttk.Button(
            button_frame,
            text="Convert",
            style="Modern.TButton",
            command=self.convert_files
        ).pack(
            side="right"
        )

        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(
                int(-e.delta/120),
                "units"
            )
        )


    def update_count(self):

        count = len(self.pdf_files)

        self.file_header.config(
            text=f"Files ({count})"
        )

    def add_pdf(self, pdf_path):

        pdf_path = str(Path(pdf_path))

        if pdf_path not in self.pdf_files:

            self.pdf_files.add(pdf_path)

            self.add_file_card(pdf_path)


    def on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)

        for item in paths:
            path = Path(item)

            if path.is_file():
                if path.suffix.lower() == ".pdf":
                    self.add_pdf(path)

            elif path.is_dir():
                for pdf_file in path.rglob("*.pdf"):
                    self.add_pdf(pdf_file)

        self.update_count()

    def clear_list(self):

        self.pdf_files.clear()

        for card in self.file_cards.values():
            card.destroy()

        self.file_cards.clear()

        self.update_count()

    def convert_pdf(self, pdf_path, output_folder):
        pdf_name = pdf_path.stem

        document = fitz.open(pdf_path)

        for page_number in range(len(document)):
            page = document.load_page(page_number)

            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False
            )

            image = Image.frombytes(
                "RGB",
                (pix.width, pix.height),
                pix.samples
            )

            image_path = output_folder / f"{pdf_name}_{page_number + 1:03d}.jpg"

            image.save(
                image_path,
                "JPEG",
                quality=95
            )

        document.close()

    def convert_files(self):
        if not self.pdf_files:
            messagebox.showwarning(
                "알림",
                "PDF 파일을 추가하세요."
            )
            return

        desktop = Path.home() / "Desktop"

        success_count = 0
        failed_files = []

        self.progress["maximum"] = len(self.pdf_files)
        self.progress["value"] = 0

        self.progress_label.config(
            text="CONVERTING...",
            fg="#3b82f6"
        )


        for index, pdf_file in enumerate(self.pdf_files, start=1):
            try:
                pdf_path = Path(pdf_file)
                pdf_name = pdf_path.stem

                if self.save_option.get() == "desktop":
                    save_root = desktop
                else:
                    save_root = pdf_path.parent

                output_folder = save_root / pdf_name
                output_folder.mkdir(
                    parents=True,
                    exist_ok=True
                )

                self.convert_pdf(
                    pdf_path,
                    output_folder
                )

                success_count += 1

            except Exception as ex:
                failed_files.append(
                    f"{pdf_file}\n{ex}"
                )

            self.progress["value"] = index
            self.root.update_idletasks()

        result_message = (
            f"변환 완료\n\n"
            f"성공 : {success_count}\n"
            f"실패 : {len(failed_files)}"
        )

        if failed_files:
            log_path = desktop / "PDF_JPG_실패목록.txt"

            with open(log_path, "w", encoding="utf-8") as file:
                file.write("\n\n".join(failed_files))

            result_message += f"\n\n실패목록 저장:\n{log_path}"

        if len(failed_files) == 0:

            self.progress.configure(
                style="Success.Horizontal.TProgressbar"
            )

            self.progress_label.config(
                text=f"✅ SUCCESS! ({success_count} Files)",
                fg="#22c55e"
            )

            self.show_success_popup(
                success_count
            )

        else:

            self.progress_label.config(
                text=f"⚠ COMPLETED WITH ERRORS ({len(failed_files)})",
                fg="#fbbf24"
            )

    def add_file_card(self, pdf_path):

        if pdf_path in self.file_cards:
            return

        card = tk.Frame(
            self.file_container,
            bg="#1d2530",
            highlightbackground="#30363d",
            highlightthickness=1
        )

        card.pack(
            fill="x",
            padx=6,
            pady=4
        )

        file_name = Path(pdf_path).name

        parent_dir = str(
            Path(pdf_path).parent
        )

        if len(parent_dir) > 40:
            parent_dir = "..." + parent_dir[-40:]

        title = tk.Label(
            card,
            text=f"📄 {file_name}",
            anchor="w",
            justify="left",
            bg="#1d2530",
            fg="#f0f6fc",
            font=("Arial", 9)
        )

        title.pack(
            fill="x",
            padx=10,
            pady=(6, 0)
        )

        path_label = tk.Label(
            card,
            text=parent_dir,
            anchor="w",
            bg="#1d2530",
            fg="#8b949e",
            font=("Arial", 8)
        )

        path_label.pack(
            fill="x",
            padx=10,
            pady=(0, 6)
        )

        for widget in (card, title, path_label):
            widget.bind(
                "<Button-1>",
                lambda e, p=pdf_path:
                self.select_file(p)
            )

        self.file_cards[pdf_path] = card

    def select_file(self, pdf_path):

        self.selected_file = pdf_path

        for path, card in self.file_cards.items():

            if path == pdf_path:
                card.configure(
                    highlightbackground="#3b82f6",
                    highlightthickness=2
                )
            else:
                card.configure(
                    highlightbackground="#30363d",
                    highlightthickness=1
                )

    def remove_selected_file(self):

        if not hasattr(self, "selected_file"):
            return

        path = self.selected_file

        if path not in self.pdf_files:
            return

        self.pdf_files.remove(path)

        self.file_cards[path].destroy()

        del self.file_cards[path]

        self.selected_file = None

        self.update_count()

    def show_success_popup(self, success_count):

        self.root.update_idletasks()

        popup = tk.Toplevel(self.root)

        popup.configure(
            bg="#161b22"
        )

        popup.title("Completed")

        popup.resizable(False, False)

        width = 360
        height = 230

        x = (
            self.root.winfo_x()
            + (self.root.winfo_width() // 2)
            - (width // 2)
        )

        y = (
            self.root.winfo_y()
            + (self.root.winfo_height() // 2)
            - (height // 2)
        )

        popup.geometry(
            f"{width}x{height}+{x}+{y}"
        )

        tk.Label(
            popup,
            text="✅",
            font=("Segoe UI Emoji", 42),
            bg="#161b22",
            fg="#22c55e"
        ).pack(
            pady=(20, 0)
        )

        tk.Label(
            popup,
            text="CONVERSION COMPLETED",
            font=("Arial", 16),
            bg="#161b22",
            fg="#22c55e"
        ).pack()

        tk.Label(
            popup,
            text="Successfully converted "
                f"{success_count} PDF files",
            font=("Arial", 10),
            bg="#161b22",
            fg="#c9d1d9"
        ).pack(
            pady=(10, 20)
        )

        tk.Button(
            popup,
            text="Close",
            bg="#22c55e",
            fg="white",
            relief="flat",
            activebackground="#16a34a",
            padx=25,
            pady=6,
            command=popup.destroy
        ).pack()




if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFConverterApp(root)
    root.mainloop()