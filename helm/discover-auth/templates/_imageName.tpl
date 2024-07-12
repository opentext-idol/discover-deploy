# BEGIN COPYRIGHT NOTICE
# Copyright 2023-2024 Open Text.
# 
# The only warranties for products and services of Open Text and its affiliates and licensors
# ("Open Text") are as may be set forth in the express warranty statements accompanying such
# products and services. Nothing herein should be construed as constituting an additional warranty.
# Open Text shall not be liable for technical or editorial errors or omissions contained herein.
# The information contained herein is subject to change without notice.
#
# END COPYRIGHT NOTICE

{{- define "idolsolutions.auth.image" -}}
{{- $registry := .registry.root -}}
{{- $nameSep := .registry.nameSeparator -}}
{{- $versionSep := .registry.versionSeparator -}}
{{- $imageName := .repo -}}
{{- $version := .version -}}
{{ print  $registry $nameSep $imageName $versionSep $version }}
{{- end -}}
