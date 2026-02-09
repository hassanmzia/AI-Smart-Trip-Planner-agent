from django.contrib import admin
from django.utils.html import format_html
from .models import AgentSession, AgentExecution, AgentLog


class AgentExecutionInline(admin.TabularInline):
    """Inline admin for AgentExecution."""

    model = AgentExecution
    extra = 0
    fields = ['execution_id', 'agent_type', 'status', 'tokens_used', 'execution_time_ms', 'cost']
    readonly_fields = ['execution_id', 'tokens_used', 'execution_time_ms', 'cost']
    can_delete = False


class AgentLogInline(admin.TabularInline):
    """Inline admin for AgentLog."""

    model = AgentLog
    extra = 0
    fields = ['log_level', 'agent_type', 'message', 'timestamp']
    readonly_fields = ['log_level', 'agent_type', 'message', 'timestamp']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AgentSession)
class AgentSessionAdmin(admin.ModelAdmin):
    """Admin interface for AgentSession model."""

    list_display = [
        'session_id', 'user', 'status', 'total_executions',
        'total_tokens_used', 'total_cost', 'started_at', 'duration'
    ]
    list_filter = ['status', 'started_at']
    search_fields = ['session_id', 'user__email', 'user_intent']
    readonly_fields = [
        'session_id', 'total_executions', 'total_tokens_used', 'total_cost',
        'started_at', 'completed_at', 'last_activity_at', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'started_at'
    inlines = [AgentExecutionInline, AgentLogInline]

    fieldsets = (
        ('Session Info', {
            'fields': ('user', 'session_id', 'status')
        }),
        ('Context & Intent', {
            'fields': ('user_intent', 'conversation_context', 'detected_entities'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_executions', 'total_tokens_used', 'total_cost')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'last_activity_at', 'created_at', 'updated_at')
        }),
    )

    def duration(self, obj):
        """Calculate and display session duration."""
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            seconds = duration.total_seconds()
            if seconds < 60:
                return f"{seconds:.1f}s"
            elif seconds < 3600:
                return f"{seconds/60:.1f}m"
            else:
                return f"{seconds/3600:.1f}h"
        return "-"
    duration.short_description = 'Duration'

    def has_add_permission(self, request):
        """Disable manual creation through admin."""
        return False


@admin.register(AgentExecution)
class AgentExecutionAdmin(admin.ModelAdmin):
    """Admin interface for AgentExecution model."""

    list_display = [
        'execution_id', 'session', 'agent_type', 'status_badge',
        'tokens_used', 'execution_time', 'cost', 'started_at'
    ]
    list_filter = ['agent_type', 'status', 'started_at']
    search_fields = ['execution_id', 'session__session_id', 'agent_type']
    readonly_fields = [
        'execution_id', 'execution_time_ms', 'started_at', 'completed_at',
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'started_at'
    inlines = [AgentLogInline]

    fieldsets = (
        ('Execution Info', {
            'fields': ('session', 'execution_id', 'agent_type', 'status')
        }),
        ('Input/Output', {
            'fields': ('input_data', 'output_data', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('agent_config', 'model_used'),
            'classes': ('collapse',)
        }),
        ('Performance Metrics', {
            'fields': ('tokens_used', 'execution_time_ms', 'cost', 'tools_called', 'function_calls')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at')
        }),
    )

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'pending': '#6c757d',
            'running': '#0dcaf0',
            'completed': '#198754',
            'failed': '#dc3545',
            'timeout': '#ffc107',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def execution_time(self, obj):
        """Display execution time in human-readable format."""
        if obj.execution_time_ms:
            if obj.execution_time_ms < 1000:
                return f"{obj.execution_time_ms}ms"
            else:
                return f"{obj.execution_time_ms/1000:.2f}s"
        return "-"
    execution_time.short_description = 'Exec Time'

    def has_add_permission(self, request):
        """Disable manual creation through admin."""
        return False


@admin.register(AgentLog)
class AgentLogAdmin(admin.ModelAdmin):
    """Admin interface for AgentLog model."""

    list_display = [
        'timestamp', 'log_level_badge', 'agent_type',
        'function_name', 'short_message', 'session', 'execution'
    ]
    list_filter = ['log_level', 'agent_type', 'timestamp']
    search_fields = ['message', 'agent_type', 'function_name', 'session__session_id']
    readonly_fields = [
        'session', 'execution', 'log_level', 'message', 'log_data',
        'agent_type', 'function_name', 'line_number', 'exception_type',
        'exception_traceback', 'timestamp', 'created_at'
    ]
    date_hierarchy = 'timestamp'

    fieldsets = (
        ('Log Info', {
            'fields': ('log_level', 'agent_type', 'message')
        }),
        ('Context', {
            'fields': ('session', 'execution', 'function_name', 'line_number')
        }),
        ('Data', {
            'fields': ('log_data',),
            'classes': ('collapse',)
        }),
        ('Exception Details', {
            'fields': ('exception_type', 'exception_traceback'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'created_at')
        }),
    )

    def log_level_badge(self, obj):
        """Display log level as colored badge."""
        colors = {
            'debug': '#6c757d',
            'info': '#0dcaf0',
            'warning': '#ffc107',
            'error': '#dc3545',
            'critical': '#8b0000',
        }
        color = colors.get(obj.log_level, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.log_level.upper()
        )
    log_level_badge.short_description = 'Level'

    def short_message(self, obj):
        """Display truncated message."""
        if len(obj.message) > 100:
            return f"{obj.message[:100]}..."
        return obj.message
    short_message.short_description = 'Message'

    def has_add_permission(self, request):
        """Disable manual creation through admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Make logs read-only."""
        return False
