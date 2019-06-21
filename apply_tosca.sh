#
# $ curl -H "xos-username: $USERNAME" -H "xos-password: $PASSWORD" -X POST --data-binary @$TOSCA_FN $TOSCA_URL/run
# Created models: ['service#kubernetes', 'free5gcserviceinstance']
#
# $ kubectl get deploy -n free5gc
# NAME                      READY   UP-TO-DATE   AVAILABLE   AGE
# amf-deployment            0/1     1            0           3m55s
# nextepc-hss-deployment    1/1     1            1           3m55s
# pcrf-nextepc-deployment   1/1     1            1           3m55s
# smf-deployment            1/1     1            1           3m55s
# upf-deployment            0/1     1            0           3m55s
# webui-deployment          1/1     1            1           32m
# 
# $ kubectl get cm -n free5gc
# NAME                       DATA   AGE
# free5gc-config             1      109s
# freediameter-amf-config    1      109s
# freediameter-hss-config    1      109s
# freediameter-pcrf-config   1      109s
# freediameter-smf-config    1      109s
# hss-config                 1      109s
# pcrf-config                1      109s

USERNAME=admin@opencord.org
PASSWORD=letmein
TOSCA_URL=http://$( hostname ):30007
TOSCA_FN=~/Free5GC-service/xos/free5gcs/free5gcservice-tosca.yaml
curl -H "xos-username: $USERNAME" -H "xos-password: $PASSWORD" -X POST --data-binary @$TOSCA_FN $TOSCA_URL/run
