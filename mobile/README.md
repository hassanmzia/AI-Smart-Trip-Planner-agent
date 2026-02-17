# AI Trip Planner - Mobile App

React Native mobile app for the AI Smart Trip Planner platform. Runs natively on both **iOS** and **Android**.

## Screenshots

The app features:
- **Gradient hero headers** with animated transitions
- **AI Chat interface** for trip planning
- **Flight/Hotel search** with AI scoring badges
- **Itinerary management** with day-by-day timeline
- **Bottom tab navigation** with notification badges
- **Professional cards** with shadows, images, and badges

## Architecture

```
mobile/
├── App.tsx                    # Root component
├── index.js                   # Entry point
├── src/
│   ├── components/
│   │   ├── common/            # Button, Input, Card, Badge, ScreenWrapper, EmptyState
│   │   └── cards/             # FlightCard, HotelCard, BookingCard, ItineraryCard
│   ├── screens/
│   │   ├── auth/              # Login, Register, ForgotPassword
│   │   ├── home/              # Home, AIPlanner
│   │   ├── flights/           # FlightSearch, FlightResults
│   │   ├── hotels/            # HotelSearch, HotelResults
│   │   ├── itineraries/       # Itineraries list
│   │   ├── bookings/          # Bookings list
│   │   ├── explore/           # Explore (Restaurants, Attractions, Weather, etc.)
│   │   ├── profile/           # Profile with settings
│   │   └── notifications/     # Notifications list
│   ├── navigation/            # AuthNavigator, MainTabNavigator, RootNavigator
│   ├── services/              # API client, auth, flights, hotels, bookings, etc.
│   ├── store/                 # Zustand stores (auth, search, notifications)
│   ├── types/                 # TypeScript type definitions
│   └── utils/                 # Theme, constants, helpers
```

## Prerequisites

- **Node.js** >= 18
- **npm** or **yarn**
- **Xcode** 15+ (for iOS, macOS only)
- **Android Studio** (for Android)
- **CocoaPods** (for iOS): `gem install cocoapods`
- **JDK** 17 (for Android)

## Quick Start

### 1. Install Dependencies

```bash
cd mobile
npm install
```

### 2. iOS Setup (macOS with Apple Silicon)

```bash
# Install CocoaPods dependencies
cd ios && pod install && cd ..

# Run on iOS Simulator
npm run ios

# Run on a specific device
npx react-native run-ios --device "iPhone 15 Pro"
```

### 3. Android Setup

```bash
# Start Metro bundler
npm start

# In another terminal, run on Android emulator
npm run android
```

### 4. Connect to Backend

The app auto-detects the platform for API URLs:
- **iOS Simulator**: `http://localhost:8109`
- **Android Emulator**: `http://10.0.2.2:8109` (Android's localhost alias)

Make sure your backend is running:
```bash
# From project root - either Docker or local
make up              # Docker
make local           # Local venv
make local-sqlite    # Simplest local setup
```

## Building for Production

### iOS (Apple Silicon Mac)

```bash
# 1. Open Xcode workspace
open ios/AITripPlanner.xcworkspace

# 2. Select your development team in Signing & Capabilities
# 3. Select a physical device or "Any iOS Device"
# 4. Product → Archive
# 5. Distribute via TestFlight or App Store

# Or build from command line:
cd ios
xcodebuild -workspace AITripPlanner.xcworkspace \
  -scheme AITripPlanner \
  -configuration Release \
  -sdk iphoneos \
  -archivePath build/AITripPlanner.xcarchive \
  archive

# Export for distribution:
xcodebuild -exportArchive \
  -archivePath build/AITripPlanner.xcarchive \
  -exportOptionsPlist ExportOptions.plist \
  -exportPath build/release
```

### Android

```bash
# Generate a release APK
cd android
./gradlew assembleRelease

# The APK will be at:
# android/app/build/outputs/apk/release/app-release.apk

# Generate a release AAB (for Play Store):
./gradlew bundleRelease
```

## Deploying to a Physical iPhone

1. Connect your iPhone via USB
2. Open `ios/AITripPlanner.xcworkspace` in Xcode
3. Select your iPhone as the build target
4. Go to **Signing & Capabilities** → select your Apple Developer Team
5. Click **Run** (or Cmd+R)
6. On first run, trust the developer on iPhone: Settings → General → VPN & Device Management

## Configuration

### API URL

Edit `src/utils/constants.ts` to change the backend URL:

```typescript
export const API_BASE_URL = 'https://your-backend.com';
```

Or for production builds, set environment variables before building.

### App Icons & Splash Screen

Replace the placeholder assets:
- **iOS**: `ios/AITripPlanner/Images.xcassets/AppIcon.appiconset/`
- **Android**: `android/app/src/main/res/mipmap-*/`

## Key Libraries

| Library | Purpose |
|---------|---------|
| react-native 0.74 | Core framework |
| @react-navigation | Navigation (stack + tabs) |
| zustand | State management |
| axios | HTTP client with JWT interceptors |
| react-native-reanimated | Smooth animations |
| react-native-linear-gradient | Gradient backgrounds |
| react-native-vector-icons | Material icons |
| react-native-toast-message | Toast notifications |
| socket.io-client | Real-time WebSocket |
| react-native-maps | Map integration |
| react-native-keychain | Secure token storage |
| lottie-react-native | Lottie animations |

## Project Initialization

If you need to regenerate the native projects (ios/android folders):

```bash
# Initialize React Native project
npx react-native init AITripPlanner --template react-native-template-typescript --directory .

# Then copy src/ files back and install dependencies
npm install
cd ios && pod install && cd ..
```
