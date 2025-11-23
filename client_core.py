import socket
import os
import sys

HOST = '127.0.0.1'
PORT = 5000
BUFFER_SIZE = 4096
SEPARATOR = "|"
CLIENT_FILES_DIR = 'client_downloads'

if not os.path.exists(CLIENT_FILES_DIR):
    os.makedirs(CLIENT_FILES_DIR)


def run_client():
    print(f"Seja Bem-vindo! Arquivos baixados em '{CLIENT_FILES_DIR}'.")
    print("Comandos Disponíveis: UPLOAD <arquivo> | DOWNLOAD <arquivo> | LIST | EXIT")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[CONECTANDO] Tentando conectar a {HOST}{PORT}...")

        s.connect((HOST, PORT))
        print("[SUCESSO] Conectado ao Servidor!")

    except Exception as e:
        print(f"[ERRO] Não foi possível conectar-se ao servidor: {e}")
        sys.exit(1)
    
    while True:
        try:
            command_line = input(">>>").strip()
            if not command_line:
                continue
            
            parts = command_line.split()
            cmd = parts[0].upper()

            if cmd == "EXIT":
                s.send("EXIT".encode())
                break

            elif cmd == "UPLOAD":
                if len(parts)< 2:
                    print("Uso: UPLOAD <nome_do_arquivo>")
                    continue
                filename = parts[1]
                upload_file(s, filename)

            elif cmd == "DOWNLOAD":
                if len(parts)< 2:
                    print("Uso: DOWNLOAD <nome_do_arquivo>")
                    continue
                filename = parts[1]
                download_file(s, filename)

            elif cmd == "LIST":
                list_files(s)

            else:
                print(f"Comando desconhecido: {cmd}. Use um dos comando disponíveis: UPLOAD, DOWNLOAD, LIST ou EXIT.")
    
        except Exception as e:
            print(f"[ERRO DE CONEXÃO {e}]")
            break
    
    s.close()
    print("[DESCONECTADO] A conexão foi encerrada.")

def upload_file(s, filename):
    try:
        filepath = os.path.join(os.getcwd(), filename)

        if not os.path.exists(filepath):
            print(f"[UPLOAD] Erro: aArquivo '{filename}' não encontrado no diretório atual.")
            return
        
        filesize = os.path.getsize(filepath)

        s.send(f"UPLOAD{SEPARATOR}{filename}{SEPARATOR}{filesize}".encode())

        confirmation = s.recv(1024).decode()
        if confirmation!= "OK":
            print("[UPLOAD] Servidor recusou a transferência")
            return
        
        with open(filepath, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
        
        final_status = s.recv(1024).decode()
        if final_status == "SUCCESS":
            print(f"[UPLOAD] Arquivo '{filename}' enviado com sucesso!")
        else:
            print(f"[UPLOAD] Erro ao salvar arquivo no servidor: {final_status}")

    except Exception as e:
        print(f"[ERRO - UPLOAD] Falha ao enviar arquivo: {e}")

def download_file(s, filename):
    try:
        s.send(f"DOWNLOAD{SEPARATOR}{filename}".encode())
        response = s.recv(BUFFER_SIZE).decode()

        resp_parts = response.split(SEPARATOR)
        status = resp_parts[0]

        if status == "EXISTS":
            filesize = int(resp_parts[1])
            print(f"[DOWNLOAD] Arquivo '{filename}' encontrado no servidor ({filesize} bytes).")
            s.send("READY".encode())

            filepath = os.path.join(CLIENT_FILES_DIR, filename)

            bytes_received = 0
            with open(filepath, "wb") as f:
                while bytes_received < filesize:
                    bytes_to_read = min(BUFFER_SIZE, filesize - bytes_received)
                    data = s.recv(bytes_to_read)

                    if not data:
                        break
                    
                    f.write(data)
                    bytes_received += len(data)
            if bytes_received == filesize:
                print(f"[DOWNLOAD] Arquivo '{filename}' salvo em '{CLIENT_FILES_DIR}' com sucesso.")
            else:
                print(f"[DOWNLOAD] Aviso: Arquivo '{filename}' recebido incompleto ({bytes_received}/{filesize} bytes).")

        elif status == "ERROR":
            error_msg = resp_parts[1] if len(resp_parts) > 1 else "Erro desconhecido."
            print(f"[DOWNLOAD] Erro: {error_msg}")
        else: 
            print(f"[DOWNLOAD] Resposta inesperada do servidor: {response}")

    except Exception as e:
        print(f"[ERRO - DOWNLOAD] Falha ao receber arquivo: {e}")

def list_files(s):

    try: 
        s.send("LIST".encode())
        response = s.recv(BUFFER_SIZE).decode()
        print("\n--- Arquivos no Servidor ---")

        if response == "Nenhum arquivo armazenado":
            print(response)
        elif response.startswith("Erro ao listar"):
            print(response)
        else: 
            files = response.split(";")
            for f in files:
                print(f"- {f}")
        print("----------------------------\n")

    except Exception as e:
        print(f"[ERRO - LIST] Falha ao listar arquivos: {e}")


if __name__ == "__main__":
    run_client()