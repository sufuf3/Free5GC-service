# Free5GC-service

## Install
### 0. Before

```sh
helm install -n xos-core cord/xos-core --version 2.3.3
helm install -n kubernetes cord/kubernetes
```

### 1. Run Synchronizer Container
```sh
kubectl create -f free5gcservice-synchronizer.yaml
```
### 2. Prepares
#### 1. Create namespace

```sh
kubectl create -f deploy/namespace.yaml
```
#### 2. Create mongodb
1. Update `deploy/mongodb/pv.yaml`
```sh
sed -i "s/192.168.26.11/${NFS_SERVER_IP}/g" deploy/mongodb/pv.yaml
```
2. Create mongodb
```sh
kubectl create -f deploy/mongodb/pv.yaml
kubectl create -f deploy/mongodb/statefulset.yaml
kubectl create -f deploy/mongodb/service-NP.yaml
```

#### 3. Create webui

```sh
kubectl create -f deploy/webui-deployment.yaml
kubectl create -f deploy/webui-service-NP.yaml
```
PS. Using NodePort

Access NODE_IP:31727 via web browser.

#### 4. Create Services
```sh
kubectl create -f deploy/smf-service-NP.yaml
kubectl create -f deploy/pcrf-service.yaml
```

#### 5. Submit TOSCA

```sh
cd xos/free5gcs && sh apply_tosca.sh
```

---

## Note

If we want to re-deploy synchronizer, restart XOS.

```sh
helm delete xos-core --purge
helm install -n xos-core cord/xos-core --set xos_projectName="M-CORD"
kubectl delete -f free5gcservice-synchronizer.yaml
kubectl apply -f free5gcservice-synchronizer.yaml
```

---

## 正規做法
在 [Synchronizer](xos/synchronizer/model_policies/model_policy_free5gcserviceinstance.py) 的程式中定義好 handle_update，之後用 xos/free5gcs/free5gcservice-tosca.yaml 定義好要送的 yaml 檔。 (但 Free5GC 的 yaml 檔太多，這樣 free5gcservice-tosca.yaml 會爆長， Synchronizer 也不好寫)
 
### Run Synchronizer Container
```sh
kubectl create -f free5gcservice-synchronizer.yaml
```

### Submit TOSCA
```sh
cd xos/free5gcs && sh apply_tosca.sh
```

## 各種髒法
1. 不管 free5gcservice-tosca.yaml ，直接寫好 yaml 檔，在佈 Synchronizer 時，就直接也一起部署。不過之後要用 tosca ～沒門～
2. Synchronizer 呼叫 Helm ，tosca 內在定義 values 即可。
<!--
helm dep update Free5GC-service
helm install Free5GC-service -n free5gc-service
-->

Ref:  

- https://guide.opencord.org/cord-6.0/simpleexampleservice/simple-example-service.html
- https://guide.xosproject.org/tutorials/basic_synchronizer.html
