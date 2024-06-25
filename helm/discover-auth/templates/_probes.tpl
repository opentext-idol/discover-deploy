{{- define "idolsolutions.auth.probe.postgres" -}}
exec:
  command:
    - psql
    - -U
    - {{ .username }}
    - --list
{{- end }}
{{- define "idolsolutions.auth.probe.keycloak" -}}
httpGet:
  port: 8080
  path: /health
{{- end }}
