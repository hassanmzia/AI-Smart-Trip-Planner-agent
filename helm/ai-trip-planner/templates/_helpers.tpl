{{/*
Expand the name of the chart.
*/}}
{{- define "ai-trip-planner.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "ai-trip-planner.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ai-trip-planner.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ai-trip-planner.labels" -}}
helm.sh/chart: {{ include "ai-trip-planner.chart" . }}
{{ include "ai-trip-planner.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: ai-trip-planner
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ai-trip-planner.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ai-trip-planner.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "ai-trip-planner.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ai-trip-planner.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Secret name to use
*/}}
{{- define "ai-trip-planner.secretName" -}}
{{- if .Values.secrets.existingSecret }}
{{- .Values.secrets.existingSecret }}
{{- else }}
{{- include "ai-trip-planner.fullname" . }}-secrets
{{- end }}
{{- end }}

{{/*
PostgreSQL host
*/}}
{{- define "ai-trip-planner.postgresHost" -}}
{{- if .Values.postgresql.external.enabled }}
{{- .Values.postgresql.external.host }}
{{- else if .Values.postgresql.enabled }}
{{- include "ai-trip-planner.fullname" . }}-postgres
{{- end }}
{{- end }}

{{/*
PostgreSQL port
*/}}
{{- define "ai-trip-planner.postgresPort" -}}
{{- if .Values.postgresql.external.enabled }}
{{- .Values.postgresql.external.port | toString }}
{{- else }}
{{- .Values.postgresql.port | toString }}
{{- end }}
{{- end }}

{{/*
PostgreSQL database
*/}}
{{- define "ai-trip-planner.postgresDatabase" -}}
{{- if .Values.postgresql.external.enabled }}
{{- .Values.postgresql.external.database }}
{{- else }}
{{- .Values.postgresql.database }}
{{- end }}
{{- end }}

{{/*
PostgreSQL username
*/}}
{{- define "ai-trip-planner.postgresUsername" -}}
{{- if .Values.postgresql.external.enabled }}
{{- .Values.postgresql.external.username }}
{{- else }}
{{- .Values.postgresql.username }}
{{- end }}
{{- end }}

{{/*
Redis host
*/}}
{{- define "ai-trip-planner.redisHost" -}}
{{- if .Values.redis.external.enabled }}
{{- .Values.redis.external.host }}
{{- else if .Values.redis.enabled }}
{{- include "ai-trip-planner.fullname" . }}-redis
{{- end }}
{{- end }}

{{/*
Redis port
*/}}
{{- define "ai-trip-planner.redisPort" -}}
{{- if .Values.redis.external.enabled }}
{{- .Values.redis.external.port | toString }}
{{- else }}
{{- .Values.redis.port | toString }}
{{- end }}
{{- end }}

{{/*
RabbitMQ host
*/}}
{{- define "ai-trip-planner.rabbitmqHost" -}}
{{- if .Values.rabbitmq.external.enabled }}
{{- .Values.rabbitmq.external.host }}
{{- else if .Values.rabbitmq.enabled }}
{{- include "ai-trip-planner.fullname" . }}-rabbitmq
{{- end }}
{{- end }}

{{/*
RabbitMQ port
*/}}
{{- define "ai-trip-planner.rabbitmqPort" -}}
{{- if .Values.rabbitmq.external.enabled }}
{{- .Values.rabbitmq.external.port | toString }}
{{- else }}
{{- .Values.rabbitmq.port | toString }}
{{- end }}
{{- end }}

{{/*
RabbitMQ username
*/}}
{{- define "ai-trip-planner.rabbitmqUsername" -}}
{{- if .Values.rabbitmq.external.enabled }}
{{- .Values.rabbitmq.external.username }}
{{- else }}
{{- .Values.rabbitmq.username }}
{{- end }}
{{- end }}

{{/*
Database URL
*/}}
{{- define "ai-trip-planner.databaseUrl" -}}
postgresql://{{ include "ai-trip-planner.postgresUsername" . }}:$(POSTGRES_PASSWORD)@{{ include "ai-trip-planner.postgresHost" . }}:{{ include "ai-trip-planner.postgresPort" . }}/{{ include "ai-trip-planner.postgresDatabase" . }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "ai-trip-planner.redisUrl" -}}
redis://:$(REDIS_PASSWORD)@{{ include "ai-trip-planner.redisHost" . }}:{{ include "ai-trip-planner.redisPort" . }}/0
{{- end }}

{{/*
RabbitMQ URL
*/}}
{{- define "ai-trip-planner.rabbitmqUrl" -}}
amqp://{{ include "ai-trip-planner.rabbitmqUsername" . }}:$(RABBITMQ_PASSWORD)@{{ include "ai-trip-planner.rabbitmqHost" . }}:{{ include "ai-trip-planner.rabbitmqPort" . }}/
{{- end }}

{{/*
Namespace
*/}}
{{- define "ai-trip-planner.namespace" -}}
{{- default .Release.Namespace .Values.global.namespace }}
{{- end }}

{{/*
Image pull secrets
*/}}
{{- define "ai-trip-planner.imagePullSecrets" -}}
{{- if .Values.global.imagePullSecrets }}
imagePullSecrets:
{{- range .Values.global.imagePullSecrets }}
  - name: {{ . }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Storage class
*/}}
{{- define "ai-trip-planner.storageClass" -}}
{{- if .Values.global.storageClass }}
storageClassName: {{ .Values.global.storageClass }}
{{- end }}
{{- end }}
