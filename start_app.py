import sys
import time
import subprocess

if __name__ == '__main__':
    # Corre el Servidor de Streamig
    subprocess.Popen([sys.executable, '1run_stream_server.py'],
    	stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(7)
    print("Stream Server start")

    subprocess.Popen([sys.executable, '2run_web_server.py'],
    	stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(5)
    print("Web Server start")

    #subprocess.Popen([sys.executable, '3run_recognition.py'],
    #	stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #print("Recognition start")