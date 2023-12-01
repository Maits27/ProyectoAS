<h1>PROYECTO FLASK</h1>

<h2>Requirements</h2>
En la carpeta 'mensajeria' hace falta un fichero llamado 't_gmail.py' con el token de nuestro correo electronico para que funcionen los emails. Para conseguir el token del correo electrónico que se vaya a usar, se deben seguir los pasos establecidos al principio del siguiente enlace:

https://recursospython.com/guias-y-manuales/enviar-correo-electronico-via-gmail-y-smtp/

<h2>Recomendaciones Docker</h2>

Antes de iniciar los contenedores, se recomienda hacer una limpieza de todas las imágenes y volúmenes de Docker que puedan estar activos de alguna forma u ocupando alguno de los puertos necesarios para el correcto funcionamiento de la aplicación. Para ello seguir los siguientes pasos:

```bash
// Parar todos los contenedores que puedan estar en uso
docker stop $(docker ps -aq)

// Eliminar cualquier imagen y volumen no usados y contenedores detenidos:
docker system prune -a

// Eliminar los volúmenes restantes después del anterior comando (volúmenes persistentes)
docker volume prune -a

```

<h2>Recomendaciones Kubernetes</h2>

Para desplegar la aplicación en el entorno Kubernetes, solo serán necesarios los ficheros .yaml de la carpeta 'Kubernetes'. El orden correcto para ejecutarlos sería el siguiente (una vez dentro de la carpeta):

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
