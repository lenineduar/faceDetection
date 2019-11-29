import subprocess

def run():
    command = r'env\Scripts\activate && cd face_detection && python manage.py runscript recognition_face'
    resultado = subprocess.run(command, shell=True)
    resultado.check_returncode()

if __name__ == '__main__':
    # Corre el Servidor de Streamig
    run()
