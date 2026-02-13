"""
NLP-powered feedback analysis service.

Uses LLM (OpenAI) for sentiment analysis, emotion detection, toxicity
checking, and topic extraction from user trip feedback comments.
Falls back to rule-based heuristics when LLM is unavailable.
"""
import json
import logging
import re
from typing import Dict, Any, List

from django.conf import settings

logger = logging.getLogger(__name__)


class FeedbackAnalyzer:
    """Analyze trip feedback text using NLP techniques."""

    # ── Keyword-based fallback dictionaries ──

    POSITIVE_WORDS = {
        'amazing', 'wonderful', 'fantastic', 'excellent', 'beautiful', 'love',
        'loved', 'great', 'perfect', 'awesome', 'incredible', 'delightful',
        'memorable', 'stunning', 'paradise', 'recommend', 'best', 'superb',
        'spectacular', 'enjoyable', 'pleasant', 'marvelous', 'outstanding',
        'brilliant', 'blissful', 'magical', 'charming', 'cozy', 'fun',
    }

    NEGATIVE_WORDS = {
        'terrible', 'awful', 'horrible', 'worst', 'hate', 'hated', 'dirty',
        'disgusting', 'rude', 'overpriced', 'disappointing', 'disappointed',
        'uncomfortable', 'noisy', 'crowded', 'scam', 'boring', 'bad',
        'poor', 'mediocre', 'unsafe', 'dangerous', 'expensive', 'cold',
        'broken', 'unfriendly', 'regret', 'waste', 'never again',
    }

    EMOTION_KEYWORDS = {
        'joy': {'happy', 'joy', 'delighted', 'thrilled', 'excited', 'ecstatic', 'bliss', 'fun', 'wonderful', 'loved'},
        'surprise': {'surprised', 'unexpected', 'wow', 'amazed', 'shocked', 'astonished', 'incredible'},
        'gratitude': {'grateful', 'thankful', 'appreciate', 'blessed', 'lucky'},
        'nostalgia': {'miss', 'memories', 'remember', 'nostalgic', 'reminds'},
        'frustration': {'frustrated', 'annoying', 'irritating', 'hassle', 'inconvenient', 'difficult'},
        'disappointment': {'disappointed', 'letdown', 'underwhelming', 'expected more', 'mediocre'},
        'anger': {'angry', 'furious', 'outraged', 'unacceptable', 'ridiculous', 'scam'},
        'sadness': {'sad', 'upset', 'unhappy', 'regret', 'depressing'},
        'relaxation': {'relaxing', 'peaceful', 'calm', 'serene', 'tranquil', 'soothing'},
        'adventure': {'adventurous', 'thrilling', 'exciting', 'exhilarating', 'adrenaline'},
    }

    TOXIC_PATTERNS = [
        r'\b(hate|stupid|idiot|trash|garbage|suck|disgusting|pathetic)\b',
        r'\b(worst ever|never again|total waste|rip off|ripoff)\b',
        r'[!]{3,}',  # excessive exclamation marks
    ]

    TOPIC_KEYWORDS = {
        'beach': {'beach', 'ocean', 'sea', 'sand', 'swim', 'snorkel', 'surf', 'coast', 'shore'},
        'culture': {'culture', 'cultural', 'tradition', 'heritage', 'history', 'historical', 'museum'},
        'food': {'food', 'restaurant', 'cuisine', 'meal', 'dinner', 'lunch', 'breakfast', 'delicious', 'tasty'},
        'nature': {'nature', 'mountain', 'hiking', 'forest', 'lake', 'waterfall', 'scenic', 'landscape', 'garden'},
        'nightlife': {'nightlife', 'bar', 'club', 'pub', 'party', 'dancing', 'cocktail'},
        'shopping': {'shopping', 'market', 'bazaar', 'souvenir', 'shop', 'mall', 'store'},
        'architecture': {'architecture', 'building', 'cathedral', 'palace', 'castle', 'monument', 'temple', 'mosque'},
        'art': {'art', 'gallery', 'painting', 'sculpture', 'exhibit', 'creative'},
        'adventure': {'adventure', 'extreme', 'kayak', 'zip', 'climb', 'dive', 'safari', 'trek'},
        'relaxation': {'spa', 'relax', 'pool', 'resort', 'massage', 'wellness'},
        'transportation': {'transport', 'taxi', 'uber', 'metro', 'bus', 'train', 'flight', 'airport'},
        'accommodation': {'hotel', 'room', 'bed', 'stay', 'hostel', 'airbnb', 'accommodation'},
        'value': {'price', 'cost', 'expensive', 'cheap', 'value', 'money', 'budget', 'afford'},
        'service': {'service', 'staff', 'helpful', 'rude', 'friendly', 'attentive', 'professional'},
        'weather': {'weather', 'rain', 'sun', 'hot', 'cold', 'warm', 'humid', 'cloudy'},
    }

    @classmethod
    def analyze(cls, feedback) -> Dict[str, Any]:
        """
        Analyze feedback text and return NLP results.

        Args:
            feedback: TripFeedback model instance

        Returns:
            Dict with sentiment, emotions, toxicity, topics, and preferences
        """
        # Combine all text fields for analysis
        all_text = ' '.join(filter(None, [
            feedback.loved_most,
            feedback.would_change,
            feedback.additional_comments,
        ]))

        if not all_text.strip():
            return cls._empty_result()

        # Try LLM-powered analysis first
        if getattr(settings, 'OPENAI_API_KEY', None):
            try:
                return cls._analyze_with_llm(all_text, feedback.overall_rating)
            except Exception as e:
                logger.warning(f"LLM feedback analysis failed, falling back to rules: {e}")

        # Fall back to rule-based analysis
        return cls._analyze_with_rules(all_text, feedback.overall_rating)

    @classmethod
    def _empty_result(cls) -> Dict[str, Any]:
        return {
            'sentiment': 'neutral',
            'sentiment_score': 0.0,
            'emotions': {},
            'is_toxic': False,
            'toxicity_score': 0.0,
            'extracted_topics': [],
            'learned_preferences': {},
        }

    @classmethod
    def _analyze_with_llm(cls, text: str, overall_rating: int) -> Dict[str, Any]:
        """Use OpenAI to analyze feedback text."""
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=settings.OPENAI_API_KEY,
        )

        prompt = f"""Analyze this trip feedback text and return a JSON object with the following fields:

1. "sentiment": one of "very_positive", "positive", "neutral", "negative", "very_negative"
2. "sentiment_score": float from -1.0 (very negative) to 1.0 (very positive)
3. "emotions": object mapping emotion names to confidence scores (0.0-1.0). Possible emotions: joy, surprise, gratitude, nostalgia, frustration, disappointment, anger, sadness, relaxation, adventure, excitement
4. "is_toxic": boolean - true if text contains hate speech, extreme profanity, or abusive language
5. "toxicity_score": float from 0.0 (not toxic) to 1.0 (very toxic)
6. "extracted_topics": array of topics mentioned (e.g., ["beach", "food", "culture", "hotel", "nightlife"])
7. "learned_preferences": object with preference signals derived from the feedback, e.g.:
   - "hotel_priority": what matters most for hotels (location/cleanliness/price/amenities)
   - "activity_interests": array of activity types they enjoyed
   - "budget_sensitivity": float 0.0-1.0 (1.0 = very price-conscious)
   - "avoid": array of things they didn't like
   - "preferred_pace": "relaxed" or "packed" or "moderate"

Overall rating given: {overall_rating}/5

Feedback text:
\"\"\"
{text[:2000]}
\"\"\"

Return ONLY valid JSON, no other text."""

        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        # Extract JSON from the response
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()

        result = json.loads(content)

        # Ensure all expected keys exist
        return {
            'sentiment': result.get('sentiment', 'neutral'),
            'sentiment_score': float(result.get('sentiment_score', 0.0)),
            'emotions': result.get('emotions', {}),
            'is_toxic': bool(result.get('is_toxic', False)),
            'toxicity_score': float(result.get('toxicity_score', 0.0)),
            'extracted_topics': result.get('extracted_topics', []),
            'learned_preferences': result.get('learned_preferences', {}),
        }

    @classmethod
    def _analyze_with_rules(cls, text: str, overall_rating: int) -> Dict[str, Any]:
        """Rule-based fallback analysis using keyword matching."""
        words = set(re.findall(r'\b\w+\b', text.lower()))

        # Sentiment
        pos_count = len(words & cls.POSITIVE_WORDS)
        neg_count = len(words & cls.NEGATIVE_WORDS)
        total = pos_count + neg_count or 1
        raw_score = (pos_count - neg_count) / total

        # Weight with star rating
        rating_score = (overall_rating - 3) / 2  # -1.0 to 1.0
        sentiment_score = round((raw_score * 0.4 + rating_score * 0.6), 2)
        sentiment_score = max(-1.0, min(1.0, sentiment_score))

        if sentiment_score >= 0.5:
            sentiment = 'very_positive'
        elif sentiment_score >= 0.1:
            sentiment = 'positive'
        elif sentiment_score >= -0.1:
            sentiment = 'neutral'
        elif sentiment_score >= -0.5:
            sentiment = 'negative'
        else:
            sentiment = 'very_negative'

        # Emotions
        emotions = {}
        for emotion, keywords in cls.EMOTION_KEYWORDS.items():
            overlap = len(words & keywords)
            if overlap > 0:
                emotions[emotion] = round(min(overlap / 3, 1.0), 2)

        # Toxicity
        toxicity_hits = sum(
            1 for pattern in cls.TOXIC_PATTERNS
            if re.search(pattern, text.lower())
        )
        toxicity_score = round(min(toxicity_hits / 3, 1.0), 2)
        is_toxic = toxicity_score >= 0.5

        # Topics
        extracted_topics = []
        for topic, keywords in cls.TOPIC_KEYWORDS.items():
            if words & keywords:
                extracted_topics.append(topic)

        # Learned preferences (basic inference)
        learned_preferences: Dict[str, Any] = {}
        if 'value' in extracted_topics or neg_count > 0 and any(w in words for w in {'expensive', 'overpriced', 'cost'}):
            learned_preferences['budget_sensitivity'] = 0.8
        if 'accommodation' in extracted_topics:
            if any(w in words for w in {'location', 'central', 'walkable'}):
                learned_preferences['hotel_priority'] = 'location'
            elif any(w in words for w in {'clean', 'cleanliness'}):
                learned_preferences['hotel_priority'] = 'cleanliness'
        activity_interests = [t for t in extracted_topics if t in {'beach', 'culture', 'nature', 'adventure', 'art', 'nightlife', 'shopping'}]
        if activity_interests:
            learned_preferences['activity_interests'] = activity_interests
        avoid = []
        if any(w in words for w in {'crowded', 'tourist trap', 'noisy'}):
            avoid.append('crowded_places')
        if any(w in words for w in {'expensive', 'overpriced'}):
            avoid.append('expensive_options')
        if avoid:
            learned_preferences['avoid'] = avoid

        return {
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'emotions': emotions,
            'is_toxic': is_toxic,
            'toxicity_score': toxicity_score,
            'extracted_topics': extracted_topics,
            'learned_preferences': learned_preferences,
        }
