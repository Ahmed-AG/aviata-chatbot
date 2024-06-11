# Kubernetes Deployment Tutorial for GenAI Chat App

This tutorial guides you through deploying a Aviata-chatbot on Kubernetes. Aviata-chatbot is a basic GenAI chat application. The app consists of three components:
- Weaviate (a vector database)
- A backend  built using Python and FastAPI
- A frontend using NGINX to host a HTML and JavaScript UI.

## TASK 1: Setting up Minikube
### Installing Minikube
From inside your LAB VM execute the following:

```bash
curl -sLo /tmp/minikube-linux-amd64 https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install -m 0755 /tmp/minikube-linux-amd64 /usr/local/bin/minikube
```

These commands download the latest Minikube binary to the /tmp directory and installs it to /usr/local/bin

### Configuring DNS
The following command appends a range of IP addresses (192.168.49.200 to 192.168.49.220) with corresponding hostnames (lb-200.sans.labs to lb-220.sans.labs) to the /etc/hosts file.
Execute the following:

```bash
(for i in {200..220}; do echo "192.168.49.$i  lb-${i}.sans.labs"; done ) | sudo tee -a /etc/hosts
```

### Starting Minikube
The next step would be to start Minikube. We also need to enable `metalLB` which will allow us to map/expose our services externally.

```bash
minikube delete
minikube start --subnet='192.168.49.0/24' --kubernetes-version=v1.28.4
minikube addons enable metallb
```
Check your work:

```bash
minikube status
kubectl cluster-info
kubectl get nodes
```

This is the first time we use the `kubectl` command tool. This is the tool that communicates with Kubernetes API server to execute Kubernetes commands.

Now that we have Minikube running, let us clone the `aviata-chatbot` app repository. This repository contains the application source code as well as the Kubernetes deployment scripts that we meed.

Execute the following commands to clone the repo and configure `MetalLB`:

```bash
cd ~/code
git clone https://github.com/Ahmed-AG/aviata-chatbot.git
cd aviata-chatbot
kubectl apply -f deploy-k8s/metallb-config.yaml
```
Congratulations, your environment is ready!

## TASK 2: Creating the essentials

### Creating a Namespace in Kubernetes

The first step you have to do is to create a namespace. Namespaces help in organizing and managing resources within your Kubernetes cluster. They logically separate your applications so that you can apply security controls later on. In Kubernetes, namespaces provide a way to divide cluster resources between multiple users or teams.

To create a namespace for your application, use the following command:

```bash
kubectl create namespace aviata-chatbot
```

### Creating a secret in Kubernetes

Secrets in Kubernetes are indispensable for securely managing sensitive information like passwords, API tokens, and SSH keys within the cluster. Utilizing Kubernetes' built-in encryption and access control mechanisms, secrets are securely stored and accessible to authorized applications and users, ensuring data confidentiality and integrity. They facilitate secure interactions between applications and external services or resources without compromising sensitive data. By abstracting the complexities of secret management, Kubernetes streamlines the deployment and management of secure containerized applications at scale.

For our specific use case, we require a secret key to interface with OpenAI APIs. The OpenAI key is to be provided by the instructor. Replace `<OPENAI_API_KEY>` with the correct key and execute the following command to create this secret in Kubernetes:

```bash
echo "<OPENAI_API_KEY>" > ~/openai_api.key
kubectl create secret -n aviata-chatbot generic openai --from-literal=openai-key=$(cat ~/openai_api.key) 
```

Different components of the application will utilize this key for communication with OpenAI.

To verify your work, execute the following:

```bash
kubectl -n aviata-chatbot get secrets
```
### Creating a ConfigMap

In Kubernetes, not all shared data between application components needs to be kept secret; `ConfigMap` provides an alternative method for sharing information. Execute the following command to apply the configuration defined in the `configmap.yaml` file within the `aviata-chatbot` namespace:

```bash
cd ~/code/aviata-chatbot
kubectl -n aviata-chatbot apply -f deploy-k8s/configmap.yaml
```

Examine the contents of `deploy-k8s/configmap.yaml`:

``` bash
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-deployment
data:
  db_url: http://weaviate.aviata-chatbot.svc.cluster.local:8080
  backend_url: http://aviata-backend.sans.labs:8000
```

In this ConfigMap we have two key-value pairs:
- db_url: Specifies the URL for accessing the database.
- backend_url: Specifies the URL for accessing the backend service.

These key-value pairs represent configuration parameters that can be used by various components of the application, such as backend services or pods, allowing them to dynamically access the specified URLs without hardcoding them into the application code. This flexibility enables easier configuration management and updates, as configuration changes can be made centrally in the ConfigMap without requiring changes to application code or container images.

Once applied, you can inspect your work using the following commands:

```bash
kubectl -n aviata-chatbot get configmap 
kubectl -n aviata-chatbot describe  configmap backend-deployment
```

These commands allow you to retrieve ConfigMaps within the namespace and provide detailed information about a specific ConfigMap named "backend-deployment". ConfigMaps facilitate the efficient sharing of non-sensitive data across different components of the application.

## TASK 3: Deploying your application

### Applying the VectoDB (Weaviate)

Now that we have the essential resources deployed, let us begin by deploying the first `deployment` and `service`, the weaviate Database:

```bash
kubectl -n aviata-chatbot apply -f deploy-k8s/weaviate-vectordb.yaml
```

Take a look at `deploy-k8s/weaviate-vectordb.yaml`. This file defines two Kubernetes resources. The first one is a Deployment, which specifies the configuration for the containers running within the pods. Within the Deployment, you'll find settings like the container image to use, the ports that the pods will be listening on, and a name for the containers.

```bash
    spec:
      containers:
      - name: weaviate-db
        image: semitechnologies/weaviate:1.23.9
        ports:
        - containerPort: 8080
        - containerPort: 50051
```

The deployment also includes environment variables that are essential for the Weaviate container to operate. Notably, there's the OpenAI key, which is crucial for the functionality of Weaviate.

```bash
        env:
        - name: OPENAI_KEY
          valueFrom: 
            secretKeyRef:
              name: openai
              key: openai-key
        - name: QUERY_DEFAULTS_LIMIT
          value: "25"
        - name: AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED
          value: "true"
        - name: PERSISTENCE_DATA_PATH
          value: "/var/lib/weaviate"
        - name: DEFAULT_VECTORIZER_MODULE
          value: "text2vec-openai"
        - name: ENABLE_MODULES
          value: "text2vec-openai,generative-openai"
        - name: CLUSTER_HOSTNAME
          value: "node1"
```
OpenAI key is set a creating an environment variable named `OPENAI_KEY` in the container, retrieving its value from a secret named `openai`, with the key `openai-key`.

The second resource that will be created is a `Service`.

```bash
apiVersion: v1
kind: Service
metadata:
  name: weaviate
spec:
  selector:
    app: weaviate
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
```

The above configuration defines a Kubernetes Service named `weaviate` that routes traffic to Pods labeled with `app: weaviate` on port 8080.

You can inspect your work using the following commands:

```bash
kubectl get service weaviate -n aviata-chatbot 
```
```bash
kubectl get service weaviate -n aviata-chatbot -o json
```

### Applying The Backend

The backend for the Aviata-chatbot is a Python-based API server that listens to requests from the Frontend, processes them, communicates with OpenAI (using the OpenAI key), and interacts with the Weaviate pods if necessary. 
To deploy the backend, execute the following command:


```bash
cd ~/code/aviata-chatbot
kubectl -n aviata-chatbot apply -f deploy-k8s/backend.yaml
```

Examine the `spec` section in `deploy-k8s/backend.yaml`:

```bash
    spec:
      containers:
      - name: backend
        image: ahmedag/aviata-backend
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_KEY
          valueFrom: 
            secretKeyRef:
              name: openai
              key: openai-key
        - name: DB_URL
          valueFrom: 
            configMapKeyRef:
              name: backend-deployment
              key: db_url
```

Notice that we have two environment variables being created: one for the OpenAI Secret Key and the other for the Weaviate Database URL.

You can inspect your work using the following commands:
```bash
kubectl -n aviata-chatbot  get service
```

```bash
kubectl -n aviata-chatbot  get po
```

Sample Output:
```bash
% kubectl -n aviata-chatbot  get service

NAME       TYPE           CLUSTER-IP     EXTERNAL-IP                                                   PORT(S)          AGE
backend    LoadBalancer   172.20.79.5    ac9b315XXXXX.us-east-2.elb.amazonaws.com                      8000:31865/TCP   50s
weaviate   ClusterIP      172.20.68.35   <none>                                                        8080/TCP         105s
% kubectl -n aviata-chatbot  get po     

NAME                                READY   STATUS    RESTARTS   AGE
backend-deployment-7c795694-652cp   1/1     Running   0          54s
weaviate-db-97f46c9b6-ps8sr         1/1     Running   0          109s
```

### Applying the Frontend

Lastly, we'll deploy our frontend, which consists of an `Nginx` server running basic HTML and JavaScript, serving as our user interface.

Execute the command:

```bash
kubectl -n aviata-chatbot apply -f deploy-k8s/frontend.yaml
```

Within our JavaScript code, there's a reference to our backend server that requires updating. While this task can be automated within a pipeline, for our lab purposes, we'll perform it manually by executing the following command.

You can inspect your work using the following commands:

```bash
kubectl -n aviata-chatbot get service
```

Sample output should look like this:

```bash
student@ace135.sans.labs ~/code/aviata-chatbot (main)$ kubectl -n aviata-chatbot get service
NAME       TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)          AGE
backend    LoadBalancer   10.103.47.225   192.168.49.200   8000:31620/TCP   2m12s
frontend   LoadBalancer   10.99.1.241     192.168.49.201   80:30000/TCP     65s
weaviate   ClusterIP      10.111.132.56   <none>           8080/TCP         4m7s
student@ace135.sans.labs ~/code/aviata-chatbot (main)$ 
```

Notice that the `backend` and the `frontend` both have an external IP. however, the `weaviate` DB does not. 

Great work so far! Let us review what we have created so far:

```bash
kubectl -n aviata-chatbot get deployment -o wide
kubectl -n aviata-chatbot get pods -o wide
kubectl -n aviata-chatbot get service -o wide
kubectl -n aviata-chatbot get configmap
kubectl -n aviata-chatbot get secrets
```
Sample output:

```bash
student@ace135.sans.labs ~/code/aviata-chatbot (main)$ kubectl -n aviata-chatbot get deployment -o wide
NAME                  READY   UP-TO-DATE   AVAILABLE   AGE     CONTAINERS    IMAGES                             SELECTOR
backend-deployment    1/1     1            1           4m20s   backend       ahmedag/backend                    app=backend
frontend-deployment   1/1     1            1           3m13s   backend       ahmedag/frontend                   app=frontend
weaviate-db           1/1     1            1           6m15s   weaviate-db   semitechnologies/weaviate:1.23.9   app=weaviate
student@ace135.sans.labs ~/code/aviata-chatbot (main)$ kubectl -n aviata-chatbot get pods -o wide
NAME                                   READY   STATUS    RESTARTS   AGE     IP           NODE       NOMINATED NODE   READINESS GATES
backend-deployment-74876d5497-sfrv6    1/1     Running   0          4m20s   10.244.0.5   minikube   <none>           <none>
frontend-deployment-6fbfd49487-nx8hz   1/1     Running   0          3m13s   10.244.0.6   minikube   <none>           <none>
weaviate-db-97f46c9b6-n29l5            1/1     Running   0          6m15s   10.244.0.4   minikube   <none>           <none>
student@ace135.sans.labs ~/code/aviata-chatbot (main)$ kubectl -n aviata-chatbot get service -o wide
NAME       TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)          AGE     SELECTOR
backend    LoadBalancer   10.103.47.225   192.168.49.200   8000:31620/TCP   4m20s   app=backend
frontend   LoadBalancer   10.99.1.241     192.168.49.201   80:30000/TCP     3m13s   app=frontend
weaviate   ClusterIP      10.111.132.56   <none>           8080/TCP         6m15s   app=weaviate
student@ace135.sans.labs ~/code/aviata-chatbot (main)$ kubectl -n aviata-chatbot get configmap
NAME                 DATA   AGE
backend-deployment   2      6m57s
kube-root-ca.crt     1      9m50s
student@ace135.sans.labs ~/code/aviata-chatbot (main)$ kubectl -n aviata-chatbot get secrets
NAME     TYPE     DATA   AGE
openai   Opaque   1      9m7s
student@ace135.sans.labs ~/code/aviata-chatbot (main)$ 
```

### Testing connectivity
With all application components deployed, it's time to test the connectivity between them. We'll start by accessing a shell on the frontend container and attempting to reach the backend.

```bash
kubectl -n aviata-chatbot get po -o wide
```

Make a note of the IP address associated with the Backend container. Once done, execute the following to get shell access on the Frontend container

```bash
FRONTEND_POD_NAME=$(kubectl -n aviata-chatbot get po -o json |jq -r '.items[].metadata.name' | grep frontend)
echo $FRONTEND_POD_NAME

kubectl -n aviata-chatbot exec -ti $FRONTEND_POD_NAME -- /bin/sh
```

Once you are inside the container, execute the following command replacing `<BACKEND_IP>` with the correct IP address:
```bash
curl http://<BACKEND_IP>:8000/api/llm?q=who%20are%20you?
```

Sample output:
```bash
{"message":"I am a helpful assistant here to provide you with information and assistance to the best of my abilities. How can I help you today?","Your prompt is":"who are you?"}
```

If you received a message like that, congratulations! This indicates that your frontend successfully accessed your backend, and your backend was able to communicate successfully with the OpenAI API.

Exit the container by executing:
```bash
exit
```

### Set DNS configuration

To be able to access Aviata-chatbot's UI, run the following command and open the link in your browser:

```bash
BACKEND_IP=$(kubectl -n aviata-chatbot get service backend -o json |jq -r '.status.loadBalancer.ingress[].ip')
echo $BACKEND_IP
sudo -- sh -c "echo \"$BACKEND_IP  aviata-backend.sans.labs\" >> /etc/hosts"
cat /etc/hosts
```

```bash
FRONTEND_IP=$(kubectl -n aviata-chatbot get service frontend -o json |jq -r '.status.loadBalancer.ingress[].ip')
echo $FRONTEND_IP
sudo -- sh -c "echo \"$FRONTEND_IP  aviata-chatbot.sans.labs\" >> /etc/hosts"
cat /etc/hosts
```

This sequence of commands retrieves the IP addresses for the backend and frontend services in the aviata-chatbot namespace from their respective Kubernetes load balancers and stores them in the BACKEND_IP and FRONTEND_IP variables. It then updates the /etc/hosts file with these IP addresses, associating them with the hostnames aviata-backend.sans.labs and aviata-chatbot.sans.labs respectively, using sudo to gain the necessary permissions.

Use your browser to access `http://aviata-chatbot.sans.labs`. 

You can also access the back end going to `http://aviata-backend.sans.labs:8000/api/llm?q="tell me a story"`

## TASK 4: Network control




## Cleanup
```bash
kubectl -n aviata-chatbot delete -f deploy-k8s/weaviate-vectordb.yaml
kubectl -n aviata-chatbot delete -f deploy-k8s/backend.yaml
kubectl -n aviata-chatbot delete -f deploy-k8s/frontend.yaml
kubectl -n aviata-chatbot delete -f deploy-k8s/configmap.yaml
kubectl delete namespace aviata-chatbot

```
## Fast Deploy
```bash
kubectl create namespace aviata-chatbot
kubectl -n aviata-chatbot apply -f deploy-k8s/configmap.yaml
kubectl -n aviata-chatbot apply -f deploy-k8s/weaviate-vectordb.yaml
kubectl -n aviata-chatbot apply -f deploy-k8s/backend.yaml
kubectl -n aviata-chatbot apply -f deploy-k8s/frontend.yaml

kubectl -n aviata-chatbot get all
kubectl -n aviata-chatbot get po
