# Repositorio principal de la aplicación Face Detection

## Installation

Actualizamos la lista de paquetes y el sistema

```bash
sudo apt-get update
sudo apt-get safe-upgrade
```

Instalamos las dependencias de la plataforma:

```bash
sudo apt-get install git-core libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev libxml2-dev libxslt1-dev python3-dev libssl-dev python3-pip libwv-dev wv libpq-dev gettext python3-psycopg2
```

Instalamos Postgres9.6 desde los Repos Oficiales (Debian 10 por default trae PostgreSQL 11):

```bash
sudo apt-get install curl ca-certificates gnupg
curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
sudo apt-get update && sudo apt-get install postgresql-9.6
```

Actualizamos pip:

```bash
sudo pip3 install pip --upgrade
```

Instalamos virtualenv:

```bash
sudo pip3 install virtualenv
```

Creamos el entorno virtual:

```bash
virtualenv env --python=python3
```

Configuramos PostgreSQL

```bash
sudo su - postgres
psql
postgres@wagtail-sandbox:~$ psql
# psql (9.3.10)
# Type "help" for help.
postgres=# CREATE DATABASE facedb;
postgres=# CREATE USER faceuser WITH PASSWORD 'facepass';
postgres=# ALTER ROLE faceuser SET client_encoding TO 'utf8';
postgres=# ALTER ROLE faceuser  SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE faceuser  SET timezone TO 'UTC';
postgres=# GRANT ALL PRIVILEGES ON DATABASE facedb TO faceuser;
postgres=# \q
```

Clonamos el repositorio en la carpeta:

```bash
git clone https://github.com/lenineduar/faceDetection.git
```

Activamos el entorno virtual e instalamos los requerimientos de la plataforma:

```bash
source env/bin/activate
(env)$ cd face_detection/
(env)$ pip3 install -r requirements/local.txt
```

Creamos un archivo .env con las configuración del entorno en src/config/settings/.env, con el siguiente contenido:

```bash
DATABASE_URL="postgres://faceuser:facepass@127.0.0.1/facedb"
```

Aplicamos las migraciones del proyecto:

```bash
python manage.py migrate
```

Corremos el servidor de desarrollo:

```bash
python manage.py runserver 0.0.0.0:8000
```

Accedemos con el navegador a [IP]:8000, donde [IP] es la dirección ip de la máquina donde esta corriendo el servidor de desarrollo:

```bash
firefox http://localhost:8000/

```