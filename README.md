# EXAMEN COMPARTAMOS

El presente proyecto es una resolucion al problema descrito en el archivo enviado con el examen de Compartamos.

El proyecto ya esta subido en la nube de AWS utilizando el servicio de API Gateway, asi como el de RDS para alojar la instancia de la BD de PostgreSQL que utilice para almacenar los datos. La direccion del endpoint de API Gateway es: ```https://ul9bncvbk5.execute-api.us-east-1.amazonaws.com/dev/``` mas el complemento del API solicitado.

COMO EJECUTAR EL PROYECTO LOCALMENTE

1. Clonar el proyecto desde el repositorio o desde el archivo zip enviado.
2. Utilizar la herramienta Pipenv para crear un ambiente virtual aislado que permita instalar las librerias necesarias para ejecutar el proyecto. Mas informacion aqui (https://pipenv-es.readthedocs.io/es/latest/)
3. Una vez configurado el ambiente, es necesario cerrar la terminal y volver a abrirla.
4. Luego, hay que entrar al shell de Pipenv con el comando: ```pipenv shell```
5. Una vez dentro del shell del ambiente virtual, hay que instalar las librerias necesarias del proyecto, para esto ejecutamos: ```pipenv install flask flask_cors boto3 psycopg2-binary```
6. Una vez instaladas todas las dependencias, ya es posible correr el proyecto con el comando ```flask run```
7. Las peticiones locales apuntan a la direccion ```http://localhost:5000/``` mas el complemento del API a ejecutar. En la documentacion de Swagger que les comparto esta cada uno de los endpoints requeridos. Tambien adjunto la coleccion de Postman si es requerida.
8. Nota: En el codigo esta hardcodeadas las credenciales de la BD en la cual se almacena la informacion del proyecto. Conozco que las practicas recomendadas dicen evitar hacer eso y conozco las consecuencias que eso puede tener, pero las deje ahi para que ustedes se puedan conectar y verificar el almacenamiento de la informacion.
