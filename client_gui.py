import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import socket
import sys
import os
import io
import threading
import client_core

class FileClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Arquivos Distribuído - Cliente")
        self.root.geometry("600x520")
        
        self.socket = None
        self.connected = False

        self.setup_ui()

    def setup_ui(self):
        frame_conn = ttk.LabelFrame(self.root, text="Conexão", padding=(10, 5))
        frame_conn.pack(fill="x", padx=10, pady=5)

        self.lbl_status = ttk.Label(frame_conn, text="Status: Desconectado", foreground="red")
        self.lbl_status.pack(side="left", padx=5)

        self.btn_connect = ttk.Button(frame_conn, text="Conectar ao Servidor", command=self.connect_server)
        self.btn_connect.pack(side="right", padx=5)

        frame_main = ttk.Frame(self.root)
        frame_main.pack(fill="both", expand=True, padx=10, pady=5)

        frame_list = ttk.LabelFrame(frame_main, text="Arquivos no Servidor", padding=(5, 5))
        frame_list.pack(side="left", fill="both", expand=True)

        self.listbox = tk.Listbox(frame_list, height=15)
        self.listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        frame_actions = ttk.Frame(frame_main, padding=(10, 0))
        frame_actions.pack(side="right", fill="y")

        self.btn_list = ttk.Button(frame_actions, text="Atualizar Lista (LIST)", command=self.list_files, state="disabled")
        self.btn_list.pack(fill="x", pady=5)
        
        self.btn_down = ttk.Button(frame_actions, text="Baixar (DOWNLOAD)", command=self.download_file, state="disabled")
        self.btn_down.pack(fill="x", pady=5)
        
        ttk.Separator(frame_actions, orient="horizontal").pack(fill="x", pady=10)
        
        self.btn_up = ttk.Button(frame_actions, text="Enviar (UPLOAD)", command=self.upload_file, state="disabled")
        self.btn_up.pack(fill="x", pady=5)

        frame_log = ttk.LabelFrame(self.root, text="Log de Operações", padding=(5, 5))
        frame_log.pack(fill="x", padx=10, pady=5)

        self.txt_log = scrolledtext.ScrolledText(frame_log, height=8, state='disabled', font=("Consolas", 8))
        self.txt_log.pack(fill="both")

    def log(self, message):
        self.txt_log.config(state='normal')
        self.txt_log.insert(tk.END, f"{message}\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state='disabled')

    def set_status(self, text, color):
        self.lbl_status.config(text=text, foreground=color)

    def capture_core_output(self, func, *args):
        buffer = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = buffer
        
        try:
            func(*args)
        except Exception as e:
            print(f"[ERRO GUI] {e}")
        finally:
            sys.stdout = original_stdout
        
        output = buffer.getvalue()
        self.log(output.strip())
        return output

    def connect_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((client_core.HOST, client_core.PORT))
            self.connected = True
            
            self.set_status("Status: Conectado", "green")
            self.btn_connect.config(state="disabled")
            self.btn_list.config(state="normal")
            self.btn_down.config(state="normal")
            self.btn_up.config(state="normal")
            
            self.log("[SISTEMA] Conectado ao Servidor!")
            self.list_files()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao conectar: {e}")

    def list_files(self):
        if not self.connected: return
        
        self.log("--- Atualizando Lista ---")
        output = self.capture_core_output(client_core.list_files, self.socket)
        
        self.listbox.delete(0, tk.END)
        lines = output.splitlines()
        for line in lines:
            if line.strip().startswith("- "):
                clean_name = line.replace("- ", "").strip()
                self.listbox.insert(tk.END, clean_name)

    def upload_file(self):
        if not self.connected: return

        filepath = filedialog.askopenfilename()
        if not filepath: return

        filename = os.path.basename(filepath)
        dirname = os.path.dirname(filepath)
        original_dir = os.getcwd()

        try:
            os.chdir(dirname)
            self.log(f"--- Iniciando Upload: {filename} ---")
            self.capture_core_output(client_core.upload_file, self.socket, filename)
            self.list_files()
        except Exception as e:
            self.log(f"[ERRO] {e}")
        finally:
            os.chdir(original_dir)

    def download_file(self):
        if not self.connected: return

        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um arquivo na lista.")
            return
        
        filename = self.listbox.get(selection[0])
        self.log(f"--- Iniciando Download: {filename} ---")
        self.capture_core_output(client_core.download_file, self.socket, filename)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileClientGUI(root)
    root.mainloop()