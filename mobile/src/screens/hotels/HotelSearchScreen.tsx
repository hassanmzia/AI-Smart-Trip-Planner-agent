/**
 * Hotel search screen
 */

import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { ScreenWrapper } from '../../components/common/ScreenWrapper';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { useSearchStore } from '../../store/searchStore';
import { hotelService } from '../../services/hotelService';
import { Colors, Typography, Spacing, BorderRadius } from '../../utils/theme';
import Toast from 'react-native-toast-message';

export const HotelSearchScreen = ({ navigation }: any) => {
  const [destination, setDestination] = useState('');
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [guests, setGuests] = useState(2);
  const [rooms, setRooms] = useState(1);

  const { setHotelSearchParams, setHotelResults, setHotelSearching, setHotelError } =
    useSearchStore();

  const handleSearch = async () => {
    if (!destination.trim() || !checkIn || !checkOut) {
      Toast.show({ type: 'error', text1: 'Missing Fields', text2: 'Fill in destination and dates' });
      return;
    }

    const params = {
      destination: destination.trim(),
      check_in_date: checkIn,
      check_out_date: checkOut,
      guests,
      rooms,
    };

    setHotelSearchParams(params);
    setHotelSearching(true);
    setHotelError(null);

    try {
      const data = await hotelService.search(params);
      setHotelResults(data.results || []);
      navigation.navigate('HotelResults', { params });
    } catch (error: any) {
      setHotelError(error.message);
      Toast.show({ type: 'error', text1: 'Search Failed', text2: error.message });
    } finally {
      setHotelSearching(false);
    }
  };

  const Counter = ({
    label,
    value,
    onInc,
    onDec,
    min = 1,
  }: {
    label: string;
    value: number;
    onInc: () => void;
    onDec: () => void;
    min?: number;
  }) => (
    <View style={styles.counter}>
      <Text style={styles.counterLabel}>{label}</Text>
      <View style={styles.counterControls}>
        <TouchableOpacity
          style={[styles.counterBtn, value <= min && styles.counterBtnDisabled]}
          onPress={onDec}
          disabled={value <= min}
        >
          <Icon name="remove" size={18} color={value <= min ? Colors.gray[300] : Colors.primary[600]} />
        </TouchableOpacity>
        <Text style={styles.counterValue}>{value}</Text>
        <TouchableOpacity style={styles.counterBtn} onPress={onInc}>
          <Icon name="add" size={18} color={Colors.primary[600]} />
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <ScreenWrapper scroll keyboardAvoiding>
      <Text style={styles.title}>Search Hotels</Text>
      <Text style={styles.subtitle}>Find the perfect stay for your trip</Text>

      <Input
        label="Destination"
        icon="location-on"
        placeholder="City, region, or hotel name"
        value={destination}
        onChangeText={setDestination}
      />

      <View style={styles.dateRow}>
        <Input
          label="Check-in"
          icon="calendar-today"
          placeholder="YYYY-MM-DD"
          value={checkIn}
          onChangeText={setCheckIn}
          containerStyle={{ flex: 1, marginRight: Spacing.sm }}
        />
        <Input
          label="Check-out"
          icon="calendar-today"
          placeholder="YYYY-MM-DD"
          value={checkOut}
          onChangeText={setCheckOut}
          containerStyle={{ flex: 1 }}
        />
      </View>

      <View style={styles.countersRow}>
        <Counter
          label="Guests"
          value={guests}
          onInc={() => setGuests(Math.min(10, guests + 1))}
          onDec={() => setGuests(Math.max(1, guests - 1))}
        />
        <Counter
          label="Rooms"
          value={rooms}
          onInc={() => setRooms(Math.min(5, rooms + 1))}
          onDec={() => setRooms(Math.max(1, rooms - 1))}
        />
      </View>

      <Button
        title="Search Hotels"
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
  dateRow: {
    flexDirection: 'row',
  },
  countersRow: {
    flexDirection: 'row',
    gap: Spacing.lg,
    marginBottom: Spacing.base,
  },
  counter: {
    flex: 1,
  },
  counterLabel: {
    ...Typography.bodySmall,
    fontWeight: '600',
    color: Colors.gray[700],
    marginBottom: Spacing.sm,
  },
  counterControls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: Colors.gray[200],
    borderRadius: BorderRadius.md,
    paddingVertical: 12,
    backgroundColor: Colors.gray[50],
  },
  counterBtn: {
    paddingHorizontal: Spacing.base,
  },
  counterBtnDisabled: {
    opacity: 0.4,
  },
  counterValue: {
    ...Typography.heading4,
    color: Colors.textPrimary,
    minWidth: 30,
    textAlign: 'center',
  },
});
