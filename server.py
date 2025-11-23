import socket
import threading
import os

HOST = '0.0.0.0' 
PORT = 5000
BUFFER_SIZE = 4096
SEPARATOR = "|"
STORAGE_DIR = 'server_files'

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def handle_upload(conn, filename, filesize):
    filepath = os.path.join(STORAGE_DIR, filename)

    conn.send("OK".encode())

    try:
        with open(filepath, "wb") as f:
            bytes_received = 0
            while bytes_received < filesize:
                bytes_to_read = min(BUFFER_SIZE, filesize - bytes_received)
                data = conn.recv(bytes_to_read)

                if not data:
                    break

                f.write(data)
                bytes_received += len(data)

        print(f"[UPLOAD] Arquivo {filename} recebido com sucesso")
        conn.send("SUCCESS".encode())
    except Exception as e:
        print(f"[ERRO - UPLOAD] {e}")
        conn.send("ERROR".encode())

def handle_download(conn, filename):
    filepath = os.path.join(STORAGE_DIR, filename)

    if os.path.exists(filepath):
        filesize = os.path.getsize(filepath)
        conn.send(f"EXISTS{SEPARATOR}{filesize}".encode())

        conn.recv(1024)

        try:
            with open(filepath, "rb") as f:
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    conn.sendall(bytes_read)
            
            print(f"[DOWNLOAD] Arquivo {filename} enviado")
        except Exception as e:
            print(f"[ERRO DOWNLOAD] {e}")
    else:
        conn.send(f"ERROR{SEPARATOR}Arquivo não encontrado".encode())

def handle_list(conn):
    try:
        files = os.listdir(STORAGE_DIR)
        files_str = ";".join(files) if files else "Nenhum arquivo armazenado"
        conn.send(files_str.encode())
    except Exception as e:
        conn.send(f"Erro ao listar: {e}".encode())


def handle_client(conn, addr):
    print(f"[NOVA CONEXÃO] {addr} conectado.")
    
    connected = True
    while connected:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            cmd = data.split()[0]

            cmd_parts = cmd.split(SEPARATOR)
            cmd = cmd_parts[0]

            if cmd == 'UPLOAD':
                filename = os.path.basename(cmd_parts[1])
                filesize = int(cmd_parts[2])
                handle_upload(conn, filename, filesize)
            
            elif cmd == 'DOWNLOAD':
                filename = os.path.basename(cmd_parts[1])
                handle_download(conn, filename)
            
            elif cmd == 'LIST':
                handle_list(conn)
                pass

            elif cmd == "EXIT":
                connected = False

        except Exception as e:
            print(f"[ERRO] Erro na conexão com {addr}: {e}")
            connected = False
    
    conn.close()
    print(f"[DESCONECTADO] {addr} saiu.")

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[OUVINDO] Servidor rodando em {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ATIVAS] Conexões ativas: {threading.active_count() - 1}")

if __name__ == "__main__":
    start()