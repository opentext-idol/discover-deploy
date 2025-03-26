{{- define "probe.postgres" -}}
exec:
  command:
    - psql
    - -U
    - {{ .username }}
    - --list
{{- end }}
{{- define "probe.keycloak" -}}
httpGet:
  port: 8080
  path: /health
{{- end }}
{{- define "probe.seaweedfs" -}}
httpGet:
  port: 8333
  path: /status
{{- end }}
{{- define "probe.api" -}}
httpGet:
  port: 8080
  path: /meta/health/basic
{{- end }}
{{- define "probe.apiSchedule" -}}
timeoutSeconds: 2
exec:
  command:
    - bash
    - "-c"
    - "curl http://localhost:8081/healthcheck | grep UP"
{{- end }}
{{- define "probe.discover" -}}
httpGet:
  port: 80
  path: /assets/config.json
{{- end }}
{{- define "probe.nifi" -}}
httpGet:
  port: 8090
  path: /nifi
{{- end }}
{{- define "probe.contentHttps" -}}
httpGet:
  scheme: HTTPS
  port: 9100
  path: /a=getstatus
{{- end }}
{{- define "probe.content" -}}
httpGet:
  port: 9100
  path: /a=getstatus
{{- end }}
{{- define "probe.qms" -}}
httpGet:
  port: 16000
  path: /a=getstatus
{{- end }}
{{- define "probe.cassandra" -}}
timeoutSeconds: 5
exec:
  command:
    - bash
    - "-c"
    - "nodetool status | grep ^UN"
{{- end }}
