/**
 * Flight search screen with origin/dest, dates, passengers, class
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';
import { useSearchStore } from '../../store/searchStore';
import { flightService } from '../../services/flightService';
import { Colors, Typography, Spacing, BorderRadius, Shadows } from '../../utils/theme';
import { TRAVEL_CLASSES } from '../../utils/constants';
import Toast from 'react-native-toast-message';

export const FlightSearchScreen = ({ navigation }: any) => {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [departureDate, setDepartureDate] = useState('');
  const [returnDate, setReturnDate] = useState('');
  const [passengers, setPassengers] = useState(1);
  const [travelClass, setTravelClass] = useState('economy');
  const [isRoundTrip, setIsRoundTrip] = useState(true);

  const { setFlightSearchParams, setFlightResults, setFlightSearching, setFlightError } =
    useSearchStore();

  const handleSearch = async () => {
    if (!origin.trim() || !destination.trim() || !departureDate.trim()) {
      Toast.show({ type: 'error', text1: 'Missing Fields', text2: 'Fill in origin, destination, and date' });
      return;
    }

    const params = {
      origin: origin.trim(),
      destination: destination.trim(),
      departure_date: departureDate,
      return_date: isRoundTrip ? returnDate : undefined,
      passengers,
      travel_class: travelClass,
    };

    setFlightSearchParams(params);
    setFlightSearching(true);
    setFlightError(null);

    try {
      const data = await flightService.search(params);
      setFlightResults(data.results || []);
      navigation.navigate('FlightResults', { params });
    } catch (error: any) {
      setFlightError(error.message);
      Toast.show({ type: 'error', text1: 'Search Failed', text2: error.message });
    } finally {
      setFlightSearching(false);
    }
  };

  const swapCities = () => {
    const temp = origin;
    setOrigin(destination);
    setDestination(temp);
  };

  return (
    <ScreenWrapper scroll keyboardAvoiding>
      <Text style={styles.title}>Search Flights</Text>
      <Text style={styles.subtitle}>Find the best deals for your journey</Text>

      {/* Trip type toggle */}
      <View style={styles.tripTypeRow}>
        <TouchableOpacity
          style={[styles.tripTypeBtn, isRoundTrip && styles.tripTypeBtnActive]}
          onPress={() => setIsRoundTrip(true)}
        >
          <Icon name="sync" size={18} color={isRoundTrip ? Colors.white : Colors.primary[600]} />
          <Text style={[styles.tripTypeText, isRoundTrip && styles.tripTypeTextActive]}>
            Round Trip
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tripTypeBtn, !isRoundTrip && styles.tripTypeBtnActive]}
          onPress={() => setIsRoundTrip(false)}
        >
          <Icon name="arrow-forward" size={18} color={!isRoundTrip ? Colors.white : Colors.primary[600]} />
          <Text style={[styles.tripTypeText, !isRoundTrip && styles.tripTypeTextActive]}>
            One Way
          </Text>
        </TouchableOpacity>
      </View>

      {/* Origin / Destination */}
      <Card variant="outlined" style={styles.routeCard}>
        <Input
          label="From"
          icon="flight-takeoff"
          placeholder="City or airport code"
          value={origin}
          onChangeText={setOrigin}
          containerStyle={{ marginBottom: 0 }}
        />
        <TouchableOpacity style={styles.swapButton} onPress={swapCities}>
          <Icon name="swap-vert" size={22} color={Colors.primary[600]} />
        </TouchableOpacity>
        <Input
          label="To"
          icon="flight-land"
          placeholder="City or airport code"
          value={destination}
          onChangeText={setDestination}
          containerStyle={{ marginBottom: 0 }}
        />
      </Card>

      {/* Dates */}
      <View style={styles.dateRow}>
        <Input
          label="Departure"
          icon="calendar-today"
          placeholder="YYYY-MM-DD"
          value={departureDate}
          onChangeText={setDepartureDate}
          containerStyle={{ flex: 1, marginRight: isRoundTrip ? Spacing.sm : 0 }}
        />
        {isRoundTrip && (
          <Input
            label="Return"
            icon="calendar-today"
            placeholder="YYYY-MM-DD"
            value={returnDate}
            onChangeText={setReturnDate}
            containerStyle={{ flex: 1 }}
          />
        )}
      </View>

      {/* Passengers & Class */}
      <View style={styles.dateRow}>
        <View style={{ flex: 1, marginRight: Spacing.sm }}>
          <Text style={styles.fieldLabel}>Passengers</Text>
          <View style={styles.counterRow}>
            <TouchableOpacity
              style={styles.counterBtn}
              onPress={() => setPassengers(Math.max(1, passengers - 1))}
            >
              <Icon name="remove" size={20} color={Colors.primary[600]} />
            </TouchableOpacity>
            <Text style={styles.counterValue}>{passengers}</Text>
            <TouchableOpacity
              style={styles.counterBtn}
              onPress={() => setPassengers(Math.min(9, passengers + 1))}
            >
              <Icon name="add" size={20} color={Colors.primary[600]} />
            </TouchableOpacity>
          </View>
        </View>
        <View style={{ flex: 1 }}>
          <Text style={styles.fieldLabel}>Class</Text>
          <View style={styles.classRow}>
            {TRAVEL_CLASSES.slice(0, 2).map((tc) => (
              <TouchableOpacity
                key={tc.value}
                style={[styles.classBtn, travelClass === tc.value && styles.classBtnActive]}
                onPress={() => setTravelClass(tc.value)}
              >
                <Text
                  style={[styles.classText, travelClass === tc.value && styles.classTextActive]}
                  numberOfLines={1}
                >
                  {tc.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          <View style={styles.classRow}>
            {TRAVEL_CLASSES.slice(2).map((tc) => (
              <TouchableOpacity
                key={tc.value}
                style={[styles.classBtn, travelClass === tc.value && styles.classBtnActive]}
                onPress={() => setTravelClass(tc.value)}
              >
                <Text
                  style={[styles.classText, travelClass === tc.value && styles.classTextActive]}
                  numberOfLines={1}
                >
                  {tc.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>

      <Button
        title="Search Flights"
        onPress={handleSearch}
        variant="gradient"
        size="lg"
        fullWidth
        icon="search"
        style={{ marginTop: Spacing.lg }}
      />
    </ScreenWrapper>
  );
};

const styles = StyleSheet.create({
  title: {
    ...Typography.heading2,
    color: Colors.textPrimary,
    marginTop: Spacing.md,
  },
  subtitle: {
    ...Typography.body,
    color: Colors.textSecondary,
    marginBottom: Spacing.xl,
  },
  tripTypeRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
    marginBottom: Spacing.lg,
  },
  tripTypeBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: BorderRadius.md,
    borderWidth: 1.5,
    borderColor: Colors.primary[200],
    gap: Spacing.xs,
  },
  tripTypeBtnActive: {
    backgroundColor: Colors.primary[600],
    borderColor: Colors.primary[600],
  },
  tripTypeText: {
    ...Typography.bodySmall,
    fontWeight: '600',
    color: Colors.primary[600],
  },
  tripTypeTextActive: {
    color: Colors.white,
  },
  routeCard: {
    marginBottom: Spacing.base,
    position: 'relative',
  },
  swapButton: {
    position: 'absolute',
    right: 16,
    top: '50%',
    marginTop: -18,
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: Colors.primary[50],
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
    ...Shadows.sm,
  },
  dateRow: {
    flexDirection: 'row',
  },
  fieldLabel: {
    ...Typography.bodySmall,
    fontWeight: '600',
    color: Colors.gray[700],
    marginBottom: Spacing.xs,
  },
  counterRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: Colors.gray[200],
    borderRadius: BorderRadius.md,
    paddingVertical: 10,
    backgroundColor: Colors.gray[50],
    marginBottom: Spacing.base,
  },
  counterBtn: {
    paddingHorizontal: Spacing.base,
  },
  counterValue: {
    ...Typography.heading4,
    color: Colors.textPrimary,
    minWidth: 30,
    textAlign: 'center',
  },
  classRow: {
    flexDirection: 'row',
    gap: 4,
    marginBottom: 4,
  },
  classBtn: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: BorderRadius.sm,
    borderWidth: 1,
    borderColor: Colors.gray[200],
    alignItems: 'center',
  },
  classBtnActive: {
    backgroundColor: Colors.primary[600],
    borderColor: Colors.primary[600],
  },
  classText: {
    fontSize: 11,
    fontWeight: '600',
    color: Colors.gray[600],
  },
  classTextActive: {
    color: Colors.white,
  },
});
