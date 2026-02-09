from rest_framework import serializers
from .models import AgentSession, AgentExecution, AgentLog


class AgentLogSerializer(serializers.ModelSerializer):
    """Serializer for AgentLog model."""

    class Meta:
        model = AgentLog
        fields = [
            'id', 'log_level', 'message', 'log_data', 'agent_type',
            'function_name', 'line_number', 'exception_type',
            'exception_traceback', 'timestamp', 'created_at'
        ]
        read_only_fields = ['id', 'timestamp', 'created_at']


class AgentExecutionSerializer(serializers.ModelSerializer):
    """Serializer for AgentExecution model."""

    logs = AgentLogSerializer(many=True, read_only=True)
    agent_type_display = serializers.CharField(source='get_agent_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = AgentExecution
        fields = [
            'id', 'execution_id', 'agent_type', 'agent_type_display',
            'status', 'status_display', 'input_data', 'output_data',
            'error_message', 'agent_config', 'model_used', 'tokens_used',
            'execution_time_ms', 'duration_seconds', 'cost', 'tools_called',
            'function_calls', 'started_at', 'completed_at', 'created_at',
            'updated_at', 'logs'
        ]
        read_only_fields = [
            'id', 'execution_id', 'execution_time_ms', 'started_at',
            'completed_at', 'created_at', 'updated_at'
        ]

    def get_duration_seconds(self, obj):
        """Calculate duration in seconds."""
        if obj.started_at and obj.completed_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None


class AgentExecutionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for AgentExecution list views."""

    agent_type_display = serializers.CharField(source='get_agent_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AgentExecution
        fields = [
            'id', 'execution_id', 'agent_type', 'agent_type_display',
            'status', 'status_display', 'tokens_used', 'execution_time_ms',
            'cost', 'started_at', 'completed_at'
        ]
        read_only_fields = fields


class AgentSessionSerializer(serializers.ModelSerializer):
    """Serializer for AgentSession model."""

    executions = AgentExecutionListSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    average_execution_time = serializers.SerializerMethodField()

    class Meta:
        model = AgentSession
        fields = [
            'id', 'session_id', 'status', 'status_display',
            'conversation_context', 'user_intent', 'detected_entities',
            'total_executions', 'total_tokens_used', 'total_cost',
            'started_at', 'completed_at', 'last_activity_at',
            'duration_seconds', 'average_execution_time',
            'created_at', 'updated_at', 'executions'
        ]
        read_only_fields = [
            'id', 'session_id', 'total_executions', 'total_tokens_used',
            'total_cost', 'started_at', 'completed_at', 'last_activity_at',
            'created_at', 'updated_at'
        ]

    def get_duration_seconds(self, obj):
        """Calculate session duration in seconds."""
        if obj.started_at and obj.completed_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return None

    def get_average_execution_time(self, obj):
        """Calculate average execution time across all executions."""
        executions = obj.executions.filter(status='completed')
        if not executions.exists():
            return None
        avg_time = executions.aggregate(models.Avg('execution_time_ms'))['execution_time_ms__avg']
        return avg_time


class AgentSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for AgentSession list views."""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    execution_count = serializers.SerializerMethodField()

    class Meta:
        model = AgentSession
        fields = [
            'id', 'session_id', 'status', 'status_display', 'user_intent',
            'total_executions', 'total_tokens_used', 'total_cost',
            'started_at', 'completed_at', 'execution_count'
        ]
        read_only_fields = fields

    def get_execution_count(self, obj):
        """Get count of executions by status."""
        return {
            'total': obj.executions.count(),
            'completed': obj.executions.filter(status='completed').count(),
            'failed': obj.executions.filter(status='failed').count(),
            'running': obj.executions.filter(status='running').count(),
        }


class AgentSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new agent sessions."""

    class Meta:
        model = AgentSession
        fields = ['user_intent', 'conversation_context', 'detected_entities']


class AgentExecutionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new agent executions."""

    class Meta:
        model = AgentExecution
        fields = [
            'agent_type', 'input_data', 'agent_config', 'model_used'
        ]
