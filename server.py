import socket
import threading
import os
import struct

CONFIG_FILE_PATH = 'config.txt'
BUFFER_SIZE = 1024  # Ajustável conforme necessário

def read_config(config_path):
    with open(config_path, 'r') as file:
        lines = file.readlines()
        config = {}
        for line in lines:
            key, value = line.strip().split('=')
            config[key] = value
        return config

def send_file(file_path, conn):
    # Obter o tamanho do arquivo
    file_size = os.path.getsize(file_path)
    # Enviar o tamanho do arquivo primeiro
    conn.sendall(struct.pack('Q', file_size))

    # Enviar o arquivo
    with open(file_path, 'rb') as file:
        while True:
            bytes_read = file.read(BUFFER_SIZE)
            if not bytes_read:
                break
            conn.sendall(bytes_read)
    print("Arquivo enviado.")

def receive_file(file_path, conn):
    print(f"Recebendo arquivo: {file_path}")
    with open(file_path, 'wb') as file:
        while True:
            bytes_read = conn.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            file.write(bytes_read)
    print("Recebimento concluído.")

def handle_client_connection(client_socket, server_directory):
    try:
        while True:
            command = client_socket.recv(BUFFER_SIZE).decode()
            print(f"Comando recebido: {command}")

            if command == 'LIST':
                files = os.listdir(server_directory)
                files_list = '\n'.join(files)
                client_socket.sendall(files_list.encode())
            elif command.startswith('DOWNLOAD'):
                file_name = command.split()[1]
                file_path = os.path.join(server_directory, file_name)
                print(f"Tentando enviar o arquivo: {file_path}")
                if os.path.exists(file_path):
                    print("Arquivo encontrado. Enviando...")
                    send_file(file_path, client_socket)
                else:
                    print("Arquivo não encontrado.")
                    client_socket.sendall("Arquivo não encontrado.".encode())
            elif command.startswith('UPLOAD'):
                file_name = command.split()[1]
                file_path = os.path.join(server_directory, file_name)
                receive_file(file_path, client_socket)
            elif command == 'EXIT':
                print("Comando de saída recebido. Fechando conexão.")
                break
    except Exception as e:
        print(f"Erro na conexão: {e}")
    finally:
        client_socket.close()

def start_server(config):
    server_ip = config['IP_ADDRESS']
    server_port = int(config['PORT'])
    server_directory = config['DIRECTORY']
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server_ip, server_port))
        s.listen()
        print(f"Servidor ouvindo em {server_ip}:{server_port}")

        while True:
            client_sock, addr = s.accept()
            print(f"Conexão estabelecida com {addr}")
            client_thread = threading.Thread(target=handle_client_connection, args=(client_sock, server_directory))
            client_thread.start()

if __name__ == "__main__":
    config = read_config(CONFIG_FILE_PATH)
    start_server(config)
