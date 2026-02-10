import os, sys, django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_agent.settings')
django.setup()

from apps.agents.agent_tools import HotelSearchTool, UtilityBasedEvaluator
from datetime import datetime, timedelta

check_in = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
check_out = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')

hotel_results = HotelSearchTool.search_hotels(
    location='Los Angeles Airport',
    check_in_date=check_in,
    check_out_date=check_out,
    adults=1
)

hotels = hotel_results.get('hotels', [])[:1]

print("="*80)
print("HOTEL DATA FLOW TEST - WHERE DOES DATA DISAPPEAR?")
print("="*80)

if hotels:
    hotel = hotels[0]
    print(f"\n1. PARSED HOTEL:")
    print(f"   name/hotel_name: {hotel.get('hotel_name')}")
    print(f"   price_per_night: {hotel.get('price_per_night')}")
    print(f"   total_rate: {hotel.get('total_rate')}")
    print(f"   images count: {len(hotel.get('images', []))}")
    print(f"   star_rating: {hotel.get('star_rating')}")
    
    # Evaluate
    evaluated = UtilityBasedEvaluator.evaluate_hotel_comprehensive(hotel)
    
    print(f"\n2. AFTER EVALUATION:")
    print(f"   name: {evaluated.get('name')}")
    print(f"   hotel_name: {evaluated.get('hotel_name')}")
    print(f"   price: {evaluated.get('price')}")
    print(f"   price_per_night: {evaluated.get('price_per_night')}")
    print(f"   total_rate: {evaluated.get('total_rate')}")
    print(f"   images count: {len(evaluated.get('images', []))}")
    print(f"   stars: {evaluated.get('stars')}")
    print(f"   star_rating: {evaluated.get('star_rating')}")
    print(f"   utility_score: {evaluated.get('utility_score')}")
    
    print(f"\n3. ANALYSIS:")
    if evaluated.get('price') == 0 or evaluated.get('price_per_night') == 0:
        print(f"   ❌ PRICE BECAME ZERO AFTER EVALUATION!")
    else:
        print(f"   ✅ Price preserved: ${evaluated.get('price')}")
        
    if not evaluated.get('images'):
        print(f"   ❌ IMAGES LOST AFTER EVALUATION!")
    else:
        print(f"   ✅ Images preserved: {len(evaluated.get('images'))} images")
else:
    print("\n❌ No hotels found!")
