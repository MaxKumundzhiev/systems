# Running cluster locally via minicube

This will create a local VM, provision Kubernetes, and create a local kubectl configu‐
ration that points to that cluster.
```bash
$ minikube start
```

When you are done with your cluster, you can stop the VM with:
```bash
$ minikube stop
```

If you want to remove the cluster, you can run:
```bash
$ minikube delete
```


The official Kubernetes client is kubectl: a command-line tool for interacting with the Kubernetes API. kubectl can be used to manage most Kubernetes objects, such as Pods, ReplicaSets, and Services. kubectl can also be used to explore and verify the overall health of the cluster.

# Definitions
Namespaces - k8s uses namespaces to organize objects in cluster. You can think of each namespace as a folder that holds a set of objects.


# kubectl (api to communicate with k8s) commands
```bash
$ kubectl get <resource-name> <obj-name> - If you want to get a specific resource

$ kubectl apply -f <file>.yaml (or <file>.json) - declarative management
    Purpose: Used to create, update, or modify resources to match a desired state defined in a configuration file.
    
    Behavior: kubectl apply reads the configuration file and determines what changes are needed to bring the live object in the cluster to the desired state. It can create a resource if it doesn't exist, or update it if it does. It also attempts to preserve any changes made directly to the live object (e.g., scaling a deployment manually).

    Use Cases: Recommended for managing the lifecycle of applications, applying configuration changes, and integrating with version control systems. It's the preferred method for maintaining the desired state of your cluster.

$ kubectl create -f <file>.yaml (or <file>.json) - imperative management
    Purpose: Primarily used for creating new resources or entirely replacing existing ones.
    
    Behavior: It directly instructs the Kubernetes API server to create an object based on the provided configuration. If the resource already exists, kubectl create will typically return an error.
    
    Use Cases: Suitable for initial deployments, creating temporary resources, or when you explicitly want to ensure a resource does not already exist before creation.
```