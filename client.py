import socket
import os
import time
import csv
import struct

CONFIG_FILE_PATH = 'config.txt'
BUFFER_SIZE = 1024  # Pode ser ajustado conforme necessário

def read_config(config_path):
    with open(config_path, 'r') as file:
        lines = file.readlines()
        config = {}
        for line in lines:
            key, value = line.strip().split('=')
            config[key] = value
        return config

def gravar_metricas_csv(operacao, tamanho_buffer, tamanho_bytes, tempo_milissegundos):

    print(f"operacao: {operacao}")
    print(f"buffer:{tamanho_buffer}")
    print(f"tamanho em bytes:{tamanho_bytes}")
    print(f"tempo em milisecs:{tempo_milissegundos}")

    if tempo_milissegundos > 0:
        throughput = (tamanho_bytes / tempo_milissegundos) * 1000  # Bytes por segundo
    else:
        throughput = 0

    with open('metricas_desempenho.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([operacao, tamanho_buffer, tamanho_bytes, tempo_milissegundos, throughput])


def download_file(s, file_name):
    file_path = os.path.join(r'C:\Users\Pichau\PycharmProjects\camilleRedes\received_files', file_name)
    print(f"Baixando arquivo: {file_name}")

    # Primeiro, leia o tamanho do arquivo
    file_size = struct.unpack('Q', s.recv(8))[0]
    print(f"Tamanho do arquivo: {file_size}")

    total_bytes = 0

    with open(file_path, 'wb') as file:
        start_time = time.time()
        print("Começou o relógio.")
        while total_bytes < file_size:
            bytes_read = s.recv(BUFFER_SIZE)
            print("leu o buffer_size.")
            print(f"Leu: {bytes_read}")
            if not bytes_read:
                break
            file.write(bytes_read)
            print("Escreveu o arquivo.")

            print(f"total_bytes: {total_bytes}")
            print(f"file_size: {file_size}")
            total_bytes += len(bytes_read)
        end_time = time.time()
        print("Parou o relógio.")

    tempo_milissegundos = (end_time - start_time) * 1000  # Convertendo para milissegundos

    gravar_metricas_csv('DOWNLOAD', BUFFER_SIZE, total_bytes, tempo_milissegundos)
    print("Download concluído.")

def upload_file(s, file_name):
    file_path = os.path.join(r'C:\Users\Pichau\PycharmProjects\camilleRedes\received_files', file_name)
    print(f"Enviando arquivo: {file_name}")
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        # Envie o tamanho do arquivo primeiro
        s.sendall(struct.pack('Q', file_size))
        print("Enviou o tamanho do arquivo.")

        start_time = time.time()
        total_bytes = 0
        with open(file_path, 'rb') as file:
            while True:
                bytes_read = file.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
                print("Enviou os bytes finais.")
                total_bytes += len(bytes_read)
        end_time = time.time()

        tempo_milissegundos = (end_time - start_time) * 1000  # Convertendo para milissegundos
        gravar_metricas_csv('UPLOAD', BUFFER_SIZE, total_bytes, tempo_milissegundos)
        print("Upload concluído.")
    else:
        print("Arquivo não encontrado para upload.")

def client_interface(server_ip, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, server_port))
        print(f"Conexão estabelecida com {server_ip}:{server_port}")

        while True:
            command = input("Digite um comando (LIST, DOWNLOAD <file>, UPLOAD <file>, EXIT): ")
            s.send(command.encode())

            if command == "EXIT":
                print("Saindo...")
                break
            elif command == "LIST":
                response = s.recv(1024).decode()
                print("Arquivos disponíveis:\n" + response)
            elif command.startswith("DOWNLOAD"):
                file_name = command.split()[1]
                download_file(s, file_name)
            elif command.startswith("UPLOAD"):
                file_name = command.split()[1]
                upload_file(s, file_name)

if __name__ == "__main__":
    config = read_config(CONFIG_FILE_PATH)
    client_interface(config['IP_ADDRESS'], int(config['PORT']))
