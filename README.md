# Jóvenes contralores

## Implementación

### Prerrequisitos

- Base de datos PostgreSQL v12 o superior
- Python 3.10 o superior
- Nginx (para proxy reverso)

### Pasos para el despliegue

#### Parte 1: preparación del proyecto

1. Desde un terminal, navegar a la carpeta raíz del proyecto

2. Instalar pipenv (si todavía no esta instalado)
   ```bash
   $ pip3 install pipenv
   ```

3. Instalar las dependencias del proyecto
    ```bash
   $ PIPENV_VENV_IN_PROJECT=1 pipenv install 
   ```

4. Crear un archivo `.env` que contenga las siguientes variables de entorno
    ```bash
    SECRET_KEY=<cadena aleatoria con letras, numeros y caracteres especiales de longitud 50 o superior>
    ENVIRONMENT=production
    DEBUG=false
    ALLOWED_HOSTS=educaciontransparente.org.py,www.educaciontransparente.org.py
    DB_HOST=<IP_SERVIDOR_POSTGRESQL>
    DB_PORT=<PUERTO_POSTGRESQL>
    DB_NAME=<NOMBRE_BD>
    DB_USER=<USUARIO_POSTGRESQL>
    DB_PASSWORD=<PASSWORD_POSTGRESQL>
    EMAIL_HOST_USER=<EMAIL_REMITENTE>
    EMAIL_HOST=<SERVIDOR_ENVIO_EMAILS>
    EMAIL_HOST_PASSWORD=<PASSWORD_EMAIL_REMITENTE>
    ```
   Reemplazar las variables según necesidad

5. Preparar la base de datos
    ```bash
   $ pipenv run python manage.py migrate
    ```

6. Recolectar los archivos estáticos
    ```bash
   $ pipenv run python manage.py collectstatic
    ```

7. Crear un superusuario
   ```bash
   $ pipenv run python manage.py createsuperuser
   ```

#### Parte 2: Configuración de servicios

Los pasos a continuación utilizan systemd para la gestión de servicios. Realice los ajustes necesarios si utiliza un
software distinto

1. Crear un archivo socket `educacion.socket`
    ```
    [Unit]
    Description=Educacion Socket
    
    [Socket]
    ListenStream=/run/educacion.sock
    
    [Install]
    WantedBy=sockets.target
   ```

2. Crear un servicio vinculado al socket `educacion.service`
   ```
   [Unit]
   Description=Educacion Daemon
   Requires=educacion.socket
   After=network.target
   
   [Service]
   User=<usuario con permisos para acceder al proyecto>
   WorkingDirectory=<directorio_del_proyecto>
   ExecStart=<directorio_del_proyecto>/.venv/bin/gunicorn \
       --env DJANGO_SETTINGS_MODULE=educaciontransparente.settings \
       --access-logfile - \
       --workers 3 \
       --bind unix:/run/educacion.sock \
       educaciontransparente.wsgi:application
   
   [Install]
   WantedBy=multi-user.target
   ```

3. Iniciar el servicio
   ```bash
   $ systemctl enable --now educacion
   ```

4. Crear un servidor en Nginx con la siguiente configuración
   ```
   server {
    server_name educaciontransparente.org.py www.educaciontransparente.org.py;

    client_max_body_size 100M;

    location /static/ {
        alias <directorio_del_proyecto>/static/;
        expires 86400;
        log_not_found off;
    }
   
   location /media/ {
      alias <directorio_del_proyecto/media/;
      expires 86400;
      log_not_found off;
   }

    location / {
        proxy_pass http://unix:/run/educacion.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $host;
    }


    listen 443 ssl;
    ssl_certificate <directorio del certificado>/fullchain.pem;
    ssl_certificate_key <directorio del certificado>/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

   }
   server {
       if ($host = educaciontransparente.org.py) {
           return 301 https://$host$request_uri;
       } # managed by Certbot
   
       if ($host = www.educaciontransparente.org.py) {
           return 301 https://$host$request_uri;
       } # managed by Certbot

       server_name educaciontransparente.org.py www.educaciontransparente.org.py;
   
       listen 80;
       return 404; # managed by Certbot
   }
   ```

5. Probar la configuración
   ```bash
   $ sudo nginx -t
   ```

6. Reiniciar Nginx
   ```bash
   $ sudo systemctl restart nginx
   ```
