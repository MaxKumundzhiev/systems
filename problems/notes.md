8th Nov
- Stack vs Queue (LIFO vs FIFO)                 (done)
- Implemented Stack using 2 queues              (done)
- recursion 3rd chapter                         (done)
- conquer and divide (approach)                 (done)
- tail recursion                                (done)
- quick sort                                    (done)
- 4th chapter conquer and divide + quick sort   (done)


9th Nov + 10th Nov
- 5th chapter (hash table)                              (done)
    - hashtable from scratch (array + hash function)    (done)
    - LRU cache (OrderedDict)                           (done)
    - Items catalog (search + put API)                  (done)
- 6 problems from algocode and leetcode (hash table)
    - duplicates                                        (done)     
    - 2Sum                                              (done)
    - Symmetry on Y axe                                 (done)
    - Isomorphic strings                                (done с подглядыванием)  (перенос на 11 ноября)
    - Tourist route                                     (done с подглядыванием)  (перенос на 11 ноября)
- k8s intro + creating and running containers           (перенос на 11 ноября)


11th Nov
- k8s intro                                             (done) (перенос на 12 ноября)
- revamp knowledge (trees + traversals)                 (перенос на 12 ноября)
- 6th chapter (BFS)                                     (перенос на 12 ноября)


12th Nov
- k8s (chapter 2) creating and running containers       (done)
    - dockerfiles                                       (done)
    - optimize docker container image size              (done)
        - In general, you want to order your layers from least likely to change to most likely to change in order to optimize the image size for pushing and pulling. 
        - https://devopscube.com/reduce-docker-image-size/
    - security                                          (done)
    - multistage builds                                 (done)
        - main idea is to separate "build" and "run | deployment" stages due to nature of how docker works
        - multi stage approach uses "build" image for "deployment"
        - https://github.com/aivor7ex/docker-multistage-practice/tree/main
    - storing in remote                                 (done)
    - container runtime                                 (done)
        - Container Runtime Interface (CRI) определяет API между Kubernetes и Container Runtime (средой выполнения контейнеров).
        - https://habr.com/ru/companies/domclick/articles/566224/
    - limiting resourses                                (done)
- trees (algocode)                                      (postponeds)
- binary search (algocode)                              (postponeds)

15th Nov
- 6th chapter (BFS)                                     (done)
- 7th chapter (Dekstra)                                 (done)


16th Nov
- chapter 3 (deploying k8s cluster)                     (done)
- deploy sample app to k8s cluster                      (done)
    https://dev.to/bravinsimiyu/how-to-dockerize-and-deploy-a-fast-api-application-to-kubernetes-cluster-35a9
- chapter 4 (kubectl commands)                          (done)
- 8th chapter (greedy algorithms)                       (postponed)
- binary search (2 problems)                            (postponed)
- graphs (bfs) (3 problems)                             (postponed)


17th November
- binary search (2 problems)                            (done)
    - search target in sorted array     (done)
    - search target in sorted 2d array  (done)

- 8th chapter (greedy algorithms)                       ()
- graphs (bfs) (3 problems)                             ()
- chapter 5 (Pods)                                      ()
- backend service + database
    use case: user generates events on client side and client sends them to backend
              whereas backend writes them to queue and consumer at some point reads from queue and write to storage (click house)
    tech stack:
        backend: fastapi (producer (to queue) + consumer (from queue))
        queue:  kafka
        storage: clickhouse
        running: k8s


Use cases:
    - get a video and cast it to diff languages (offline | online)


