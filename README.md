# Free5GC-service

## Prerequisites

### Softwares

- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) version v1.13.5.
- [ONOS](https://onosproject.org/) v1.13.5 (Helm chart onos-1.1.0).
- [Helm](https://helm.sh/) v2.9.1.


### Install Steps

#### 1. Install Helm

```sh
curl -L https://storage.googleapis.com/kubernetes-helm/helm-v2.9.1-linux-amd64.tar.gz > helm-v2.9.1-linux-amd64.tar.gz && tar -zxvf helm-v2.9.1-linux-a
md64.tar.gz && chmod +x linux-amd64/helm && sudo mv linux-amd64/helm /usr/local/bin/helm
rm -rf /home/$USER/helm-v2.9.1-linux-amd64.tar.gz
helm init
kubectl create serviceaccount --namespace kube-system tiller
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
kubectl patch deploy --namespace kube-system tiller-deploy -p '{"spec":{"template":{"spec":{"serviceAccount":"tiller"}}}}'
```

#### 2. Install ONOS

```sh
helm repo add cord https://charts.opencord.org
helm repo update
helm install -n onos cord/onos
```

#### 3. Install XOS & base-kubernetes

```sh
git clone https://github.com/sufuf3/Free5GC-service.git && cd Free5GC-service/
kubectl create -f deploy/k8s-default-to-admin-privilege.yaml
kubectl create -f deploy/k8s-default-to-basek8s-privilege.yaml
```

```sh
mkdir ~/cord
cd ~/cord && git clone https://gerrit.opencord.org/helm-charts
cd ~/cord/helm-charts
git checkout 495b62510a5fdd7909330c7b294e8ef88eaa7421
helm dep update cos-core
helm install xos-core -n xos-core --version 2.3.8
helm dep update xos-profiles/base-kubernetes
helm install xos-profiles/base-kubernetes -n base-kubernetes --version 1.0.3
```

#### 4. Verification
```sh
$ helm list
NAME           	REVISION	UPDATED                 	STATUS  	CHART                	NAMESPACE
base-kubernetes	1       	Fri Jun 21 18:19:46 2019	DEPLOYED	base-kubernetes-1.0.3	default
onos           	1       	Sat Jun  1 12:03:18 2019	DEPLOYED	onos-1.1.0           	default
xos-core       	1       	Fri Jun 21 18:19:44 2019	DEPLOYED	xos-core-2.3.8       	default

$ kubectl get po
NAME                                          READY   STATUS      RESTARTS   AGE
base-kubernetes-kubernetes-dc9769bbf-c46mp    1/1     Running     0          4h18m
base-kubernetes-tosca-loader-r524w            0/1     Completed   3          4h18m
onos-7c78695c6-jdb4v                          2/2     Running     2          20d
xos-chameleon-cdd6968df-b9wnk                 1/1     Running     0          4h18m
xos-core-84ff9b6965-4sp76                     1/1     Running     0          4h18m
xos-db-5b58f49b97-5l4cl                       1/1     Running     0          4h18m
xos-gui-68977b7b4c-49lxv                      1/1     Running     0          4h18m
xos-tosca-7fb8457d8d-m57hg                    1/1     Running     0          4h18m
xos-ws-6c9f8fb949-fxhvk                       1/1     Running     0          4h18m 
```

#### 5. Update `/etc/kubernetes/kubelet.env`

1. Add `--allowed-unsafe-sysctls 'kernel.msg*,net.ipv4.*,net.ipv6.*' \` into `/etc/kubernetes/kubelet.env`.
2. `sudo systemctl restart kubelet`
3. `sudo systemctl status kubelet`

#### 6. Install NFS Server

On node-1.

```sh
sudo apt-get install -qqy nfs-kernel-server
sudo mkdir -p /nfsshare/mongodb
echo "/nfsshare *(rw,sync,no_root_squash)" | sudo tee /etc/exports
sudo exportfs -r
sudo showmount -e
```

#### 7. Network Setup
##### 1. Config free5gc.network

```sh
sudo sh -c "cat << EOF > /etc/systemd/network/99-free5gc.netdev
[NetDev]
Name=uptun
Kind=tun
EOF"

sudo systemctl enable systemd-networkd
sudo systemctl restart systemd-networkd

sudo sh -c "echo 'net.ipv6.conf.uptun.disable_ipv6=0' > /etc/sysctl.d/30-free5gc.conf"
sudo sysctl -p /etc/sysctl.d/30-free5gc.conf
sudo sh -c "cat << EOF > /etc/systemd/network/99-free5gc.network
[Match]
Name=uptun
[Network]
Address=45.45.0.1/16
EOF"
```

##### 2. SR-IOV serup

**a. Setup VF num on SR-IOV device & create CRD**

```sh
$ ip a
5: ens11f3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq portid 8cea1b30da42 state UP group default qlen 1000
    link/ether 8c:ea:1b:30:da:42 brd ff:ff:ff:ff:ff:ff
    inet 192.188.2.99/24 brd 192.188.2.255 scope global ens11f3
       valid_lft forever preferred_lft forever
    inet6 fe80::8eea:1bff:fe30:da42/64 scope link
       valid_lft forever preferred_lft forever
$ echo 30 | sudo tee -a /sys/class/net/ens11f3/device/sriov_numvfs
$ kubectl createa -f deploy/crdnetwork.yaml
$ kubectl create -f deploy/sriov-crd.yaml
$ kubectl get net-attach-def
NAME                   AGE
sriov-net1             4h
```
**b. Build and run SRIOV network device plugin**  

Ref: https://github.com/intel/sriov-network-device-plugin#build-and-run-sriov-network-device-plugin  

```sh
$ git clone https://github.com/intel/sriov-network-device-plugin.git && cd sriov-network-device-plugin
$ make
$ make image
```

**c. Setup /etc/pcidp/config.json**  

First, use `lspci | grep -i Ethernet` to check interface's sysfs pci address.  
Then, edit /etc/pcidp/config.json as following:  
```sh
{
    "resourceList":
    [
        {
            "resourceName": "sriov_net",
            "rootDevices": ["01:00.3"],
            "sriovMode": true,
            "deviceType": "netdevice"
        }
    ]
}
```

**d. Deploy sriov-network-device-plugin on k8s**  

```sh
$ kubectl create -f deploy/sriovdp-deploy.yaml
```

**e. Check**  
```sh
$ kubectl get node kubecord-a -o json | jq '.status.allocatable'
{
  "cpu": "31800m",
  "ephemeral-storage": "226240619760",
  "hugepages-1Gi": "8Gi",
  "intel.com/sriov_net": "30",
  "memory": "56931140Ki",
  "pods": "110"
}
```

## Installation

### 1. Create namespace

```sh
kubectl create -f deploy/namespace.yaml
```
### 2. Create mongodb
1. Update `deploy/nctu5GC/mongodb/pv.yaml`
```sh
sed -i "s/192.168.26.11/${NFS_SERVER_IP}/g" deploy/mongodb/pv.yaml
```
2. Create mongodb
```sh
kubectl create -f deploy/mongodb/pv.yaml
kubectl create -f deploy/mongodb/statefulset.yaml
kubectl create -f deploy/mongodb/service-NP.yaml
```

### 3. Create webui

```sh
kubectl create -f deploy/webui-deployment.yaml
kubectl create -f deploy/webui-service-NP.yaml
```
PS. Using NodePort

Access NODE_IP:31727 via web browser.

### 4. Run Synchronizer Container

```sh
kubectl create -f free5gcservice-synchronizer.yaml
```

Verification  

```sh
$ kubectl get po
NAME                                          READY   STATUS      RESTARTS   AGE
base-kubernetes-kubernetes-dc9769bbf-c46mp    1/1     Running     0          4h18m
base-kubernetes-tosca-loader-r524w            0/1     Completed   3          4h18m
free5gcservice-synchronizer-df74fd97b-qztnc   1/1     Running     0          4h16m
onos-7c78695c6-jdb4v                          2/2     Running     2          20d
sriov-device-plugin-576f57b897-jddlt          1/1     Running     0          4h10m
xos-chameleon-cdd6968df-b9wnk                 1/1     Running     0          4h18m
xos-core-84ff9b6965-4sp76                     1/1     Running     0          4h18m
xos-db-5b58f49b97-5l4cl                       1/1     Running     0          4h18m
xos-gui-68977b7b4c-49lxv                      1/1     Running     0          4h18m
xos-tosca-7fb8457d8d-m57hg                    1/1     Running     0          4h18m
xos-ws-6c9f8fb949-fxhvk                       1/1     Running     0          4h18m
```


## Usage

There are two ways:

### 1. Use XOS Web UI

Fill-in all the information of free5gc

![](https://i.imgur.com/iu3AiAF.png)


### 2. Use TOSCA

Modify `xos/free5gcs/free5gcservice-tosca.yaml`, then  

```sh
sh apply_tosca.sh
```

### Check
```sh
$ kubectl get deploy -n free5gc
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
amf-deployment            1/1     1            1           3m55s
nextepc-hss-deployment    1/1     1            1           3m55s
pcrf-nextepc-deployment   1/1     1            1           3m55s
smf-deployment            1/1     1            1           3m55s
upf-deployment            1/1     1            1           3m55s
webui-deployment          1/1     1            1           32m

$ kubectl get cm -n free5gc
NAME                       DATA   AGE
free5gc-config             1      109s
freediameter-amf-config    1      109s
freediameter-hss-config    1      109s
freediameter-pcrf-config   1      109s
freediameter-smf-config    1      109s
hss-config                 1      109s
pcrf-config                1      109s
```

Ref:  

- https://guide.opencord.org/cord-6.0/simpleexampleservice/simple-example-service.html
- https://guide.xosproject.org/tutorials/basic_synchronizer.html
- https://github.com/opencord/kubernetes-service
