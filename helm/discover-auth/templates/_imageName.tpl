{{- define "idolsolutions.auth.image" -}}
{{- $registry := .registry -}}
{{- $imageName := .repo -}}
{{- $version := .version -}}
{{ print  $registry "/" $imageName ":" $version }}
{{- end -}}