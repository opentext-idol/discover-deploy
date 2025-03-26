{{- define "image" -}}
{{- if .custom -}}
image: {{ .Values.docker.customRegistry.root }}{{ .Values.docker.customRegistry.nameSeparator }}{{ .imageName }}{{ .Values.docker.customRegistry.versionSeparator }}{{ .version }}
{{- else -}}
image: {{ .Values.docker.registry.root }}{{ .Values.docker.registry.nameSeparator }}{{ .imageName }}{{ .Values.docker.registry.versionSeparator }}{{ .version }}
{{- end -}}
{{- end -}}
