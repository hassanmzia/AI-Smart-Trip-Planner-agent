from django.db import models
from django.conf import settings
from django.utils import timezone


class AgentSession(models.Model):
    """Track multi-agent AI conversation sessions."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agent_sessions'
    )

    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Session metadata
    conversation_context = models.JSONField(default=dict, blank=True)
    user_intent = models.TextField(blank=True)
    detected_entities = models.JSONField(default=dict, blank=True)

    # Session stats
    total_executions = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    # Timestamps
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agent_sessions'
        ordering = ['-started_at']
        verbose_name = 'Agent Session'
        verbose_name_plural = 'Agent Sessions'
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['session_id']),
        ]

    def __str__(self):
        return f"Session {self.session_id} - {self.user.email} ({self.status})"

    def mark_completed(self):
        """Mark session as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def mark_failed(self):
        """Mark session as failed."""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.save()


class AgentExecution(models.Model):
    """Track individual agent executions within a session."""

    AGENT_TYPE_CHOICES = [
        ('orchestrator', 'Orchestrator Agent'),
        ('flight_search', 'Flight Search Agent'),
        ('hotel_search', 'Hotel Search Agent'),
        ('car_rental', 'Car Rental Agent'),
        ('itinerary_planner', 'Itinerary Planner Agent'),
        ('booking', 'Booking Agent'),
        ('recommendation', 'Recommendation Agent'),
        ('customer_support', 'Customer Support Agent'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
    ]

    session = models.ForeignKey(
        AgentSession,
        on_delete=models.CASCADE,
        related_name='executions'
    )

    execution_id = models.CharField(max_length=100, unique=True, db_index=True)
    agent_type = models.CharField(max_length=50, choices=AGENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Execution details
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    # Agent configuration
    agent_config = models.JSONField(default=dict, blank=True)
    model_used = models.CharField(max_length=100, blank=True)

    # Performance metrics
    tokens_used = models.IntegerField(default=0)
    execution_time_ms = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    # Tool/function calls made by the agent
    tools_called = models.JSONField(default=list, blank=True)
    function_calls = models.JSONField(default=list, blank=True)

    # Timestamps
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agent_executions'
        ordering = ['-started_at']
        verbose_name = 'Agent Execution'
        verbose_name_plural = 'Agent Executions'
        indexes = [
            models.Index(fields=['session', '-started_at']),
            models.Index(fields=['agent_type', '-started_at']),
            models.Index(fields=['status']),
            models.Index(fields=['execution_id']),
        ]

    def __str__(self):
        return f"{self.agent_type} - {self.execution_id} ({self.status})"

    def mark_completed(self, output_data=None):
        """Mark execution as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if output_data:
            self.output_data = output_data
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds() * 1000
            self.execution_time_ms = int(duration)
        self.save()

        # Update session stats
        self.session.total_executions += 1
        self.session.total_tokens_used += self.tokens_used
        self.session.total_cost += self.cost
        self.session.save()

    def mark_failed(self, error_message):
        """Mark execution as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds() * 1000
            self.execution_time_ms = int(duration)
        self.save()


class AgentLog(models.Model):
    """Detailed logging for agent operations."""

    LOG_LEVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    execution = models.ForeignKey(
        AgentExecution,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True
    )

    session = models.ForeignKey(
        AgentSession,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    log_level = models.CharField(max_length=20, choices=LOG_LEVEL_CHOICES, default='info')
    message = models.TextField()

    # Structured log data
    log_data = models.JSONField(default=dict, blank=True)

    # Context
    agent_type = models.CharField(max_length=50, blank=True)
    function_name = models.CharField(max_length=200, blank=True)
    line_number = models.IntegerField(null=True, blank=True)

    # Exception details if error
    exception_type = models.CharField(max_length=200, blank=True)
    exception_traceback = models.TextField(blank=True)

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'agent_logs'
        ordering = ['-timestamp']
        verbose_name = 'Agent Log'
        verbose_name_plural = 'Agent Logs'
        indexes = [
            models.Index(fields=['session', '-timestamp']),
            models.Index(fields=['execution', '-timestamp']),
            models.Index(fields=['log_level', '-timestamp']),
        ]

    def __str__(self):
        return f"[{self.log_level.upper()}] {self.agent_type} - {self.message[:50]}"
