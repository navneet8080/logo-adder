import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
from image_processor import add_logo_to_images, get_resource_path # Import our processing logic
from PIL import ImageTk, Image

class LogoAdderApp:
    def __init__(self, master):
        self.master = master
        master.title("Logo Adder")
        master.geometry("500x450") # Set initial window size
        master.resizable(True, True) # Make window resizable

        # === Add this section to set the window icon ===
        try:
            # Load the logo using PIL and convert it to a PhotoImage
            # Use the get_resource_path helper function to ensure it works after building
            logo_path_icon = get_resource_path(os.path.join("assets", "logo.png"))
            logo_image = Image.open(logo_path_icon)
            logo_photo = ImageTk.PhotoImage(logo_image)
            master.iconphoto(False, logo_photo)
        except Exception as e:
            # You can handle the error here, e.g., print a message
            print(f"Could not set window icon: {e}")
        # ===============================================

        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.logo_path = tk.StringVar()
        self.logo_percentage = tk.IntVar(value=15) # Default logo size to 15%

        # --- Styling ---
        self.style = ttk.Style()
        self.style.theme_use('clam') # Or 'alt', 'default', 'classic'
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=6)
        self.style.configure('TEntry', font=('Arial', 10))
        self.style.configure('Horizontal.TScale', background='#f0f0f0')


        # --- Input Folder ---
        frame_input = ttk.Frame(master, padding="10")
        frame_input.pack(fill='x', pady=5)

        ttk.Label(frame_input, text="Input Folder:").pack(side='left', padx=(0, 10))
        ttk.Entry(frame_input, textvariable=self.input_folder, width=40, state='readonly').pack(side='left', fill='x', expand=True)
        ttk.Button(frame_input, text="Browse", command=self.browse_input_folder).pack(side='right', padx=(10,0))

        # --- Output Folder ---
        frame_output = ttk.Frame(master, padding="10")
        frame_output.pack(fill='x', pady=5)

        ttk.Label(frame_output, text="Output Folder:").pack(side='left', padx=(0, 10))
        ttk.Entry(frame_output, textvariable=self.output_folder, width=40, state='readonly').pack(side='left', fill='x', expand=True)
        ttk.Button(frame_output, text="Browse", command=self.browse_output_folder).pack(side='right', padx=(10,0))
        
        # --- Logo File ---
        frame_logo = ttk.Frame(master, padding="10")
        frame_logo.pack(fill='x', pady=5)

        ttk.Label(frame_logo, text="Logo File:").pack(side='left', padx=(0, 10))
        ttk.Entry(frame_logo, textvariable=self.logo_path, width=40, state='readonly').pack(side='left', fill='x', expand=True)
        ttk.Button(frame_logo, text="Browse", command=self.browse_logo_file).pack(side='right', padx=(10,0))

        # --- Logo Size Percentage ---
        frame_logo_size = ttk.Frame(master, padding="10")
        frame_logo_size.pack(fill='x', pady=5)
        
        ttk.Label(frame_logo_size, text="Logo Size (% of image width):").pack(side='left')
        ttk.Scale(frame_logo_size, from_=5, to=50, orient='horizontal', 
                  variable=self.logo_percentage, command=self.update_logo_percentage_label,
                  length=150).pack(side='left', padx=10)
        self.logo_percentage_label = ttk.Label(frame_logo_size, text=f"{self.logo_percentage.get()}%")
        self.logo_percentage_label.pack(side='left')

        # --- Process Button ---
        self.process_button = ttk.Button(master, text="Start Processing", command=self.start_processing_thread)
        self.process_button.pack(pady=20)

        # --- Progress Bar ---
        self.progress_label = ttk.Label(master, text="Ready to process images.")
        self.progress_label.pack(pady=(10, 5))
        
        self.progress_bar = ttk.Progressbar(master, orient='horizontal', length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        # --- Output Log (Text Widget) ---
        self.log_text = tk.Text(master, height=8, state='disabled', wrap='word', bg='#e2e2e2', font=('Arial', 9))
        self.log_text.pack(padx=10, pady=10, fill='both', expand=True)
        self.log_text.yview_moveto(1.0) # Auto-scroll to bottom

        # Set default paths (optional, but good for testing)
        self.input_folder.set(os.path.join(os.getcwd(), "input_images"))
        self.output_folder.set(os.path.join(os.getcwd(), "output_images"))
        self.logo_path.set(os.path.join(os.getcwd(), "assets", "logo.png"))
        self.append_log("Application started. Please select folders and logo, then click 'Start Processing'.")

    def append_log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # Auto-scroll to bottom
        self.log_text.config(state='disabled')
        self.master.update_idletasks() # Update GUI immediately

    def update_logo_percentage_label(self, val):
        self.logo_percentage_label.config(text=f"{int(float(val))}%")

    def browse_input_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.input_folder.set(folder_selected)
            self.append_log(f"Input folder selected: {folder_selected}")

    def browse_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder.set(folder_selected)
            self.append_log(f"Output folder selected: {folder_selected}")

    def browse_logo_file(self):
        file_selected = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_selected:
            self.logo_path.set(file_selected)
            self.append_log(f"Logo file selected: {file_selected}")

    def start_processing_thread(self):
        # Disable button to prevent multiple clicks
        self.process_button.config(state='disabled', text="Processing...")
        self.progress_bar.config(mode='indeterminate')
        self.progress_bar.start()
        self.append_log("Starting image processing...")

        # Create a new thread for processing to keep the GUI responsive
        processing_thread = threading.Thread(target=self._process_images)
        processing_thread.start()

    def _process_images(self):
        input_f = self.input_folder.get()
        output_f = self.output_folder.get()
        logo_p = self.logo_path.get()
        logo_perc = self.logo_percentage.get()

        def show_error(title, msg):
            messagebox.showerror(title, msg)
            self.reset_gui_for_new_process()

        if not all([input_f, output_f, logo_p]):
            self.master.after(0, show_error, "Error", "Please select all required folders and logo file.")
            return
        
        if not os.path.exists(input_f):
            self.master.after(0, show_error, "Error", f"Input folder does not exist: {input_f}")
            return

        try:
            # Pass a lambda function as the message_callback
            add_logo_to_images(input_f, output_f, logo_p, logo_perc, 
                               lambda msg: self.master.after(0, self.append_log, msg))
            
            # Schedule success message and GUI reset on the main thread
            self.master.after(0, self.processing_finished_successfully)
        except Exception as e:
            # Schedule error message and GUI reset on the main thread
            self.master.after(0, show_error, "Processing Error", f"An error occurred: {e}")

    def processing_finished_successfully(self):
        messagebox.showinfo("Success", "All images processed successfully!")
        self.append_log("Image processing finished.")
        self.reset_gui_for_new_process()

    def reset_gui_for_new_process(self):
        self.process_button.config(state='normal', text="Start Processing")
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate', value=0)


if __name__ == "__main__":
    root = tk.Tk()
    app = LogoAdderApp(root)
    root.mainloop()