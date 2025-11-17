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
```