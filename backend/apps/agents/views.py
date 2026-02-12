from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Sum, Count, Q
from django.conf import settings
from django.utils import timezone
import json
import logging
import uuid

from .models import AgentSession, AgentExecution, AgentLog
from .serializers import (
    AgentSessionSerializer,
    AgentSessionListSerializer,
    AgentSessionCreateSerializer,
    AgentExecutionSerializer,
    AgentExecutionListSerializer,
    AgentExecutionCreateSerializer,
    AgentLogSerializer
)

logger = logging.getLogger(__name__)


class AgentSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AgentSession model.
    Provides CRUD operations for agent sessions.
    """

    queryset = AgentSession.objects.all()
    serializer_class = AgentSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['session_id', 'user_intent']
    filterset_fields = ['status', 'started_at']
    ordering_fields = ['started_at', 'completed_at', 'total_executions', 'total_cost']
    ordering = ['-started_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return AgentSessionListSerializer
        elif self.action == 'create':
            return AgentSessionCreateSerializer
        return AgentSessionSerializer

    def get_queryset(self):
        """Filter queryset to only show authenticated user's sessions unless staff."""
        if self.request.user.is_staff:
            return AgentSession.objects.all()
        return AgentSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create session with generated session_id."""
        session_id = f"session_{uuid.uuid4().hex[:16]}"
        serializer.save(user=self.request.user, session_id=session_id)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark session as completed."""
        session = self.get_object()
        session.mark_completed()
        serializer = self.get_serializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        """Mark session as failed."""
        session = self.get_object()
        session.mark_failed()
        serializer = self.get_serializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get analytics for a specific session."""
        session = self.get_object()
        executions = session.executions.all()

        analytics = {
            'total_executions': executions.count(),
            'completed_executions': executions.filter(status='completed').count(),
            'failed_executions': executions.filter(status='failed').count(),
            'total_tokens': session.total_tokens_used,
            'total_cost': float(session.total_cost),
            'average_execution_time': executions.filter(
                status='completed'
            ).aggregate(Avg('execution_time_ms'))['execution_time_ms__avg'],
            'agents_used': executions.values('agent_type').distinct().count(),
            'execution_by_agent': list(
                executions.values('agent_type').annotate(
                    count=Count('id'),
                    avg_time=Avg('execution_time_ms'),
                    total_tokens=Sum('tokens_used')
                )
            ),
        }
        return Response(analytics)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get overall statistics for user's sessions."""
        sessions = self.get_queryset()

        stats = {
            'total_sessions': sessions.count(),
            'active_sessions': sessions.filter(status='active').count(),
            'completed_sessions': sessions.filter(status='completed').count(),
            'failed_sessions': sessions.filter(status='failed').count(),
            'total_executions': sessions.aggregate(Sum('total_executions'))['total_executions__sum'] or 0,
            'total_tokens_used': sessions.aggregate(Sum('total_tokens_used'))['total_tokens_used__sum'] or 0,
            'total_cost': float(sessions.aggregate(Sum('total_cost'))['total_cost__sum'] or 0),
        }
        return Response(stats)


class AgentExecutionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AgentExecution model.
    Provides CRUD operations for agent executions.
    """

    queryset = AgentExecution.objects.all()
    serializer_class = AgentExecutionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['execution_id', 'agent_type']
    filterset_fields = ['session', 'agent_type', 'status', 'started_at']
    ordering_fields = ['started_at', 'completed_at', 'execution_time_ms', 'cost']
    ordering = ['-started_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return AgentExecutionListSerializer
        elif self.action == 'create':
            return AgentExecutionCreateSerializer
        return AgentExecutionSerializer

    def get_queryset(self):
        """Filter queryset to only show authenticated user's executions unless staff."""
        if self.request.user.is_staff:
            return AgentExecution.objects.all()
        return AgentExecution.objects.filter(session__user=self.request.user)

    def perform_create(self, serializer):
        """Create execution with generated execution_id."""
        session_id = self.request.data.get('session_id')
        try:
            session = AgentSession.objects.get(
                session_id=session_id,
                user=self.request.user
            )
        except AgentSession.DoesNotExist:
            raise serializers.ValidationError({'session_id': 'Invalid session_id'})

        execution_id = f"exec_{uuid.uuid4().hex[:16]}"
        serializer.save(session=session, execution_id=execution_id)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark execution as completed."""
        execution = self.get_object()
        output_data = request.data.get('output_data', {})
        tokens_used = request.data.get('tokens_used', 0)
        cost = request.data.get('cost', 0)

        execution.tokens_used = tokens_used
        execution.cost = cost
        execution.mark_completed(output_data)

        serializer = self.get_serializer(execution)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        """Mark execution as failed."""
        execution = self.get_object()
        error_message = request.data.get('error_message', 'Unknown error')
        execution.mark_failed(error_message)

        serializer = self.get_serializer(execution)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_agent_type(self, request):
        """Get executions grouped by agent type."""
        executions = self.get_queryset()
        agent_type = request.query_params.get('agent_type')

        if agent_type:
            executions = executions.filter(agent_type=agent_type)

        stats = executions.values('agent_type').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            failed=Count('id', filter=Q(status='failed')),
            avg_time=Avg('execution_time_ms'),
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('cost')
        )

        return Response(stats)


class AgentLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for AgentLog model.
    Provides read-only access to agent logs.
    """

    queryset = AgentLog.objects.all()
    serializer_class = AgentLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message', 'agent_type', 'function_name']
    filterset_fields = ['session', 'execution', 'log_level', 'agent_type', 'timestamp']
    ordering_fields = ['timestamp', 'log_level']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Filter queryset to only show authenticated user's logs unless staff."""
        if self.request.user.is_staff:
            return AgentLog.objects.all()
        return AgentLog.objects.filter(session__user=self.request.user)

    @action(detail=False, methods=['get'])
    def errors(self, request):
        """Get all error and critical logs."""
        logs = self.get_queryset().filter(
            log_level__in=['error', 'critical']
        )
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_session(self, request):
        """Get logs for a specific session."""
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response(
                {'error': 'session_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = AgentSession.objects.get(
                session_id=session_id,
                user=request.user
            )
        except AgentSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        logs = self.get_queryset().filter(session=session)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


def _synthesize_narrative(*, result, origin, destination, departure_date,
                         return_date, passengers, budget, cuisine):
    """Use LLM to generate a day-by-day narrative itinerary from all agent results."""
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage

    rec = result.get('recommendation', {})

    # ── Flight information ──
    flight_summary = ''
    if rec.get('recommended_flight'):
        f = rec['recommended_flight']
        flight_summary = (
            f"Best Flight: {f.get('airline', '')} {f.get('flight_number', '')} "
            f"from {f.get('departure_airport_code', origin)} to {f.get('arrival_airport_code', destination)}, "
            f"${f.get('price', 'N/A')}, {f.get('stops', 0)} stops, "
            f"departs {f.get('departure_time', '')}, arrives {f.get('arrival_time', '')}, "
            f"duration: {f.get('duration', 'N/A')} min, class: {f.get('travel_class', 'Economy')}"
        )
    if rec.get('alternative_flight'):
        af = rec['alternative_flight']
        flight_summary += (
            f"\nAlternative Flight: {af.get('airline', '')} {af.get('flight_number', '')} "
            f"${af.get('price', 'N/A')}, {af.get('stops', 0)} stops"
        )

    # ── Hotel information ──
    hotel_summary = ''
    if rec.get('recommended_hotel'):
        h = rec['recommended_hotel']
        hotel_summary = (
            f"Top Hotel: {h.get('name') or h.get('hotel_name', '')}, "
            f"${h.get('price') or h.get('price_per_night', 'N/A')}/night, "
            f"{h.get('stars') or h.get('star_rating', '')} stars, "
            f"address: {h.get('address', '')}"
        )
    # Include top 5 hotel alternatives
    top_hotels = rec.get('top_5_hotels', [])
    if top_hotels and len(top_hotels) > 1:
        hotel_summary += "\nOther Hotel Options:"
        for idx, h in enumerate(top_hotels[1:4], 2):
            hotel_summary += (
                f"\n  {idx}. {h.get('name') or h.get('hotel_name', '')} - "
                f"${h.get('price') or h.get('price_per_night', 'N/A')}/night, "
                f"{h.get('stars') or h.get('star_rating', '')} stars"
            )

    # ── Restaurant information ──
    restaurant_summary = ''
    if rec.get('recommended_restaurant'):
        r = rec['recommended_restaurant']
        restaurant_summary = (
            f"Top Restaurant: {r.get('name', '')}, "
            f"{r.get('cuisine_type', '')} cuisine, "
            f"${r.get('average_cost_per_person', 'N/A')}/person, "
            f"rating: {r.get('rating', 'N/A')}/5, "
            f"address: {r.get('address', '')}"
        )
    # Include top 5 restaurant alternatives
    top_restaurants = rec.get('top_5_restaurants', [])
    if top_restaurants:
        restaurant_summary += "\nAll Recommended Restaurants:"
        for idx, r in enumerate(top_restaurants[:5], 1):
            restaurant_summary += (
                f"\n  {idx}. {r.get('name', '')} - {r.get('cuisine_type', '')} cuisine, "
                f"${r.get('average_cost_per_person', 'N/A')}/person, "
                f"rating: {r.get('rating', 'N/A')}/5, {r.get('address', '')}"
            )

    # ── Car rental information ──
    car_summary = ''
    if rec.get('recommended_car'):
        c = rec['recommended_car']
        car_summary = (
            f"Top Car Rental: {c.get('rental_company', '')} - {c.get('vehicle', c.get('car_type', ''))}, "
            f"${c.get('price_per_day', 'N/A')}/day, total: ${c.get('total_price', 'N/A')}, "
            f"rating: {c.get('rating', 'N/A')}"
        )
    top_cars = rec.get('top_5_cars', [])
    if top_cars and len(top_cars) > 1:
        car_summary += "\nOther Car Rental Options:"
        for idx, c in enumerate(top_cars[1:4], 2):
            car_summary += (
                f"\n  {idx}. {c.get('rental_company', '')} - {c.get('car_type', '')}, "
                f"${c.get('price_per_day', 'N/A')}/day"
            )

    # ── Budget analysis ──
    budget_summary = ''
    budget_analysis = rec.get('budget_analysis', {})
    total_cost = rec.get('total_estimated_cost')
    if total_cost:
        budget_summary = f"Total Estimated Trip Cost: ${total_cost}"
    if budget_analysis:
        cheapest = budget_analysis.get('cheapest flight', {})
        if cheapest:
            budget_summary += f"\nCheapest flight: ${cheapest.get('price', 'N/A')} ({cheapest.get('status', '')})"

    # ── Weather information (from WeatherTool) ──
    weather_summary = ''
    try:
        from .agent_tools import WeatherTool
        weather_data = WeatherTool.get_weather(location=destination, date=departure_date)
        if weather_data and not weather_data.get('error'):
            weather_summary = (
                f"Weather at {destination}: {weather_data.get('temperature', 'N/A')}, "
                f"{weather_data.get('condition', 'N/A')}, "
                f"humidity: {weather_data.get('humidity', 'N/A')}, "
                f"wind: {weather_data.get('wind_speed', 'N/A')}"
            )
    except Exception as e:
        logger.debug(f"Weather fetch for narrative: {e}")

    # ── Collect all flight options for context ──
    all_flights_summary = ''
    flights_data = result.get('flights', {})
    if isinstance(flights_data, dict):
        all_flights = flights_data.get('flights', [])
        if all_flights:
            all_flights_summary = f"Total flights found: {len(all_flights)}"

    # ── Collect restaurant search context ──
    all_restaurants_summary = ''
    restaurant_data = result.get('restaurants', {})
    if isinstance(restaurant_data, dict):
        all_restaurants = restaurant_data.get('restaurants', [])
        if all_restaurants:
            all_restaurants_summary = f"Total restaurants found: {len(all_restaurants)}"

    prompt = f"""Create a comprehensive, detailed day-by-day travel itinerary in markdown format.
You are an expert travel planner creating a real, actionable trip plan.

## Trip Details
- Origin: {origin}
- Destination: {destination}
- Dates: {departure_date} to {return_date or departure_date}
- Passengers: {passengers}
- Budget: ${budget or 'flexible'}
{f'- Cuisine preference: {cuisine}' if cuisine else ''}

## Flight Options
{flight_summary or 'No specific flight data available - suggest checking major airlines.'}
{all_flights_summary}

## Accommodation
{hotel_summary or 'No specific hotel data available - suggest checking major hotel booking sites.'}

## Dining Options
{restaurant_summary or 'No specific restaurant data available - suggest local dining.'}
{all_restaurants_summary}

## Transportation
{car_summary or 'No specific car rental data available - suggest public transit or ride-sharing.'}

## Weather & Climate
{weather_summary or f'Check weather for {destination} closer to travel dates.'}

## Budget Analysis
{budget_summary or 'No budget analysis available.'}

---

Please create a comprehensive day-by-day itinerary that includes:

1. **Trip Overview** - A brief, exciting summary of the trip highlighting key experiences

2. **Day-by-day schedule** - For EACH day of the trip:
   - Morning activities with times (e.g., "8:00 AM - Breakfast at [restaurant name]")
   - Afternoon activities with times (sightseeing, tours, attractions specific to {destination})
   - Evening activities with times (dinner, entertainment, nightlife)
   - Include specific place names, famous landmarks, and popular attractions in {destination}
   - Suggest specific restaurants from the data above for meals
   - Include estimated costs for each activity
   - Add transportation notes between activities

3. **Practical Tips** - Local customs, tipping, language, safety tips for {destination}

4. **Budget Summary** - Complete breakdown:
   - Flights cost
   - Accommodation cost (per night × number of nights)
   - Daily food budget
   - Transportation/car rental
   - Activities and attractions
   - Total estimated trip cost vs. planned budget

Use markdown ## for day headings (e.g., "## Day 1: Arrival in {destination}").
Use specific times like "8:00 AM", "12:30 PM", "7:00 PM".
Be specific with real place names, real attractions, and real restaurant suggestions for {destination}.
This should read like a professional travel guide."""

    model = ChatOpenAI(
        model=settings.AGENT_CONFIG.get('MODEL', 'gpt-4o-mini'),
        temperature=0.7,
        api_key=settings.OPENAI_API_KEY,
    )

    response = model.invoke([HumanMessage(content=prompt)])
    return response.content


@api_view(['POST'])
@permission_classes([AllowAny])
def plan_travel(request):
    """
    Main endpoint to run the multi-agent travel planning system.
    
    Request body:
    {
        "query": "I want to travel from Paris to Berlin",
        "origin": "CDG",
        "destination": "BER", 
        "departure_date": "2025-10-10",
        "return_date": "2025-10-15",
        "passengers": 2,
        "budget": 500.0
    }
    """
    try:
        # Get request data
        query = request.data.get('query', 'Plan my travel')
        origin = request.data.get('origin')
        destination = request.data.get('destination')
        departure_date = request.data.get('departure_date')
        return_date = request.data.get('return_date')
        passengers = request.data.get('passengers', 1)
        budget = request.data.get('budget')
        cuisine = request.data.get('cuisine')

        # Validate required fields
        if not all([origin, destination, departure_date]):
            return Response({
                'success': False,
                'error': 'origin, destination, and departure_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get the travel system
        from .multi_agent_system import get_travel_system
        travel_system = get_travel_system()

        # Run the multi-agent system
        result = travel_system.run(
            user_query=query,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            passengers=passengers,
            budget=budget,
            cuisine=cuisine
        )

        # Generate LLM day-by-day narrative itinerary
        if result.get('success') and settings.OPENAI_API_KEY:
            try:
                result['itinerary_text'] = _synthesize_narrative(
                    result=result,
                    origin=origin,
                    destination=destination,
                    departure_date=departure_date,
                    return_date=return_date,
                    passengers=passengers,
                    budget=budget,
                    cuisine=cuisine,
                )
            except Exception as e:
                logger.warning(f"LLM narrative generation failed: {e}")
                result['itinerary_text'] = None

        # Create session record if user is authenticated
        if request.user.is_authenticated:
            try:
                session = AgentSession.objects.create(
                    user=request.user,
                    session_id=f"session_{uuid.uuid4().hex[:16]}",
                    user_intent=query,
                    context_data={
                        'origin': origin,
                        'destination': destination,
                        'departure_date': departure_date,
                        'return_date': return_date,
                        'passengers': passengers,
                        'budget': budget,
                        'cuisine': cuisine
                    },
                    status='completed' if result.get('success') else 'failed'
                )
                result['session_id'] = session.session_id
            except Exception as e:
                # Don't fail the request if session creation fails
                print(f"Session creation error: {e}")

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    Chat endpoint for conversational travel planning.
    
    Request body:
    {
        "message": "I need a cheap flight to Berlin next month",
        "session_id": "session_abc123" (optional, for continuing a conversation)
    }
    """
    try:
        message = request.data.get('message')
        session_id = request.data.get('session_id')

        if not message:
            return Response({
                'success': False,
                'error': 'message is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # TODO: Implement NLP to extract travel parameters from message
        # For now, return a helpful response
        return Response({
            'success': True,
            'message': 'Chat interface coming soon! Please use the search form for now.',
            'suggestion': 'Use the /api/agents/plan endpoint with specific origin, destination, and dates.'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
