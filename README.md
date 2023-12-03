<h1>PROYECTO FLASK</h1>

<h2>Docker</h2>

<h3>Requisitos</h3>

En la carpeta 'mensajeria' hace falta un fichero llamado 't_gmail.py' con el token de nuestro correo electronico para que funcionen los emails. Para conseguir el token del correo electrónico que se va a utilizar, deben seguirse los pasos detallados al principio del siguiente enlace:

https://recursospython.com/guias-y-manuales/enviar-correo-electronico-via-gmail-y-smtp/

Los ficheros 'config.py' de las carpetas 'api' y 'app' contienen las claves necesarias para acceder a la base de datos y hashear las contraseñas, por lo que **no se pueden borrar ni alterar**.

<h3>Recomendaciones</h3>

Antes de iniciar los contenedores, se recomienda hacer una limpieza de todas las imágenes y volúmenes de Docker que puedan estar activos de alguna forma u ocupando alguno de los puertos necesarios para el correcto funcionamiento de la aplicación. Para ello seguir los siguientes pasos:

```bash
// Parar todos los contenedores que puedan estar en uso
docker stop $(docker ps -aq)

// Eliminar cualquier imagen y volumen no usados y contenedores detenidos:
docker system prune -a

// Eliminar los volúmenes restantes después del anterior comando (volúmenes persistentes)
docker volume prune -a

```

Una vez eliminados todos los objetos que pudiesen resultar en conflicto, se puede iniciar el entorno Docker:

```bash
docker compose up -d

// O si se quieren ver los logs:
docker compose up
```

Cuando todos los servicios muestren un _Started_ o _Healthy_ se podrá acceder a http://localhost:80 para la aplicación, en el http://localhost:8080 a los dashboards de Traefik y en el http://localhost:8085 a phpMyAdmin.

Todas las carpetas del repositorio menos la de 'Kubernetes' son necesarias a la hora de hacer el docker compose. En caso de querer utilizar las imágenes ya creadas habría que añadir las siguientes en el docker-compose.yml:

* APP: https://hub.docker.com/repository/docker/maits27/app/general → maits27/app
* API: https://hub.docker.com/repository/docker/maits27/api/general → maits27/api
* Mensajería: https://hub.docker.com/repository/docker/maits27/mensajeria/general → maits27/mensajeria

Para detener los contenedores:

```bash
docker compose down
```

<h2>Kubernetes</h2>

<h3>Requisitos</h3>

Para desplegar la aplicación en el entorno Kubernetes, solo serán necesarios los ficheros .yaml de la carpeta 'Kubernetes'.

En caso de querer cambiar el email desde el que se quieren enviar correos, se debería subir a Docker Hub la imagen creada en el apartado anterior y sustituir la imagen del fichero _deployment_mensajeria.yaml_ llamada 'maits27/mensajeria' por la nueva imagen de Docker Hub.

<h3>Recomendaciones</h3>

El cluster se puede desplegar en GKE, sin embargo, se recomienda hacer uso del Kubernetes proporcionado por Docker Desktop, debido a que el proceso de creación del cluster y la puesta en marcha de los servicios es prácticamente inmediata, a diferencia de en GKE.

El orden correcto para ejecutarlos sería el siguiente (una vez dentro de la carpeta):

```bash
kubectl apply -f .\deployment_bd.yaml
kubectl apply -f .\deployment_api.yaml
kubectl apply -f .\deployment_mensajeria.yaml
kubectl apply -f .\deployment_app.yaml
```

Especialmente importante ejecutar primero la base de datos de forma que se carguen correctamente los datos. Dentro de cada .yaml vienen en orden los servicios que se ejecutarán, entre ellos los ClusterIP, LoadBalancer, Deployments, ConfigMap...

Para ver que todo funciona correctamente se pueden hacer uso de los siguientes comandos donde todas las instancias deberían estar _Running_:

```bash
// Muestra los Deployment generados
kubectl get deploy

// Muestra los Pods creados por cada Deployment
kubectl get pods

// Muestra los ClusterIP y LoadBalancer 
kubectl get svc 
```

Para eliminar algún deployment o quitar el entorno seguir los siguientes comandos:

```bash
kubectl delete -f .\deployment_app.yaml
kubectl delete -f .\deployment_api.yaml
kubectl delete -f .\deployment_mensajeria.yaml
kubectl delete -f .\deployment_bd.yaml
```
