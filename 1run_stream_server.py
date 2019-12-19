import subprocess

def run():
    command = r"""cd node_stream_server && node stream_server.js"""
    resultado = subprocess.run(command, shell=True)
    resultado.check_returncode()

if __name__ == '__main__':
    # Corre el Servidor de Streamig
    run()
    
