#!/usr/bin/env bash
# =============================================================================
# Build & Distribute AI Trip Planner Mobile App
# =============================================================================
# Run this on your Apple Silicon MacBook.
#
# Usage:
#   ./build-mobile.sh setup       # One-time: install all prerequisites
#   ./build-mobile.sh ios-dev     # Run on iOS Simulator
#   ./build-mobile.sh ios-device  # Run on connected iPhone
#   ./build-mobile.sh ios-build   # Build .ipa for distribution
#   ./build-mobile.sh android     # Build Android .apk
#   ./build-mobile.sh all         # Build both iOS .ipa and Android .apk
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MOBILE_DIR="${SCRIPT_DIR}/mobile"
IOS_DIR="${MOBILE_DIR}/ios"
ANDROID_DIR="${MOBILE_DIR}/android"
BUILD_OUTPUT="${SCRIPT_DIR}/build-output"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_step()  { echo -e "${BLUE}[STEP]${NC}  $*"; }

ACTION="${1:-help}"

# =============================================================================
# STEP 0: Help
# =============================================================================
if [[ "$ACTION" == "help" || "$ACTION" == "-h" || "$ACTION" == "--help" ]]; then
  cat <<'HELP'

  AI Trip Planner - Mobile Build Script
  ======================================

  Usage:
    ./build-mobile.sh setup         One-time setup (install tools, deps, init RN)
    ./build-mobile.sh ios-dev       Run on iOS Simulator
    ./build-mobile.sh ios-device    Run on connected iPhone via USB
    ./build-mobile.sh ios-build     Build .ipa for TestFlight / Ad Hoc distribution
    ./build-mobile.sh android       Build Android .apk
    ./build-mobile.sh all           Build both .ipa and .apk

  Prerequisites (installed by 'setup'):
    - Xcode 15+ (from App Store)
    - Android Studio (for Android builds only)
    - Node.js 18+
    - CocoaPods
    - Apple Developer account (for device builds)

HELP
  exit 0
fi

# =============================================================================
# STEP 1: Setup (one-time)
# =============================================================================
if [[ "$ACTION" == "setup" ]]; then
  echo ""
  echo "======================================="
  echo "  Mobile App - One-Time Setup"
  echo "======================================="
  echo ""

  # Check macOS
  if [[ "$(uname)" != "Darwin" ]]; then
    log_error "This script must run on macOS (Apple Silicon Mac)"
    exit 1
  fi

  # Check Xcode
  log_step "Checking Xcode..."
  if ! xcode-select -p &>/dev/null; then
    log_warn "Xcode Command Line Tools not found. Installing..."
    xcode-select --install
    echo "After Xcode CLT install completes, run this script again."
    exit 1
  fi
  log_info "Xcode: $(xcodebuild -version | head -1)"

  # Check/install Homebrew
  if ! command -v brew &>/dev/null; then
    log_step "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
  log_info "Homebrew: $(brew --version | head -1)"

  # Check/install Node.js
  if ! command -v node &>/dev/null; then
    log_step "Installing Node.js..."
    brew install node@20
  fi
  log_info "Node.js: $(node --version)"

  # Check/install Watchman (recommended by React Native)
  if ! command -v watchman &>/dev/null; then
    log_step "Installing Watchman..."
    brew install watchman
  fi
  log_info "Watchman installed"

  # Check/install CocoaPods
  if ! command -v pod &>/dev/null; then
    log_step "Installing CocoaPods..."
    brew install cocoapods
  fi
  log_info "CocoaPods: $(pod --version)"

  # Check/install JDK (for Android)
  if ! command -v javac &>/dev/null; then
    log_step "Installing JDK 17 (for Android builds)..."
    brew install openjdk@17
    log_warn "Add to your shell profile:"
    log_warn '  export JAVA_HOME=$(/usr/libexec/java_home -v 17)'
  fi

  # Install npm dependencies
  log_step "Installing npm dependencies..."
  cd "${MOBILE_DIR}"
  npm install

  # Initialize React Native native projects if they don't exist
  if [[ ! -d "${IOS_DIR}/AITripPlanner.xcodeproj" ]]; then
    log_step "Initializing React Native native projects..."
    log_warn "This creates the ios/ and android/ folders with native code."

    # Create a temp RN project, then copy native folders
    TEMP_DIR=$(mktemp -d)
    cd "${TEMP_DIR}"
    npx @react-native-community/cli init AITripPlanner --version 0.74.5 --skip-install
    cp -R "${TEMP_DIR}/AITripPlanner/ios" "${MOBILE_DIR}/"
    cp -R "${TEMP_DIR}/AITripPlanner/android" "${MOBILE_DIR}/"
    rm -rf "${TEMP_DIR}"
    cd "${MOBILE_DIR}"

    log_info "Native projects initialized"
  fi

  # Install iOS pods
  log_step "Installing CocoaPods dependencies..."
  cd "${IOS_DIR}"
  pod install
  cd "${MOBILE_DIR}"

  log_info "Setup complete!"
  echo ""
  echo "======================================="
  echo "  Next steps:"
  echo "======================================="
  echo ""
  echo "  1. Run on iOS Simulator:"
  echo "     ./build-mobile.sh ios-dev"
  echo ""
  echo "  2. Run on your iPhone:"
  echo "     ./build-mobile.sh ios-device"
  echo ""
  echo "  3. Build .ipa for distribution:"
  echo "     ./build-mobile.sh ios-build"
  echo ""
  exit 0
fi

# =============================================================================
# Common: ensure deps installed
# =============================================================================
if [[ ! -d "${MOBILE_DIR}/node_modules" ]]; then
  log_step "Installing npm dependencies..."
  cd "${MOBILE_DIR}" && npm install
fi

mkdir -p "${BUILD_OUTPUT}"

# =============================================================================
# iOS: Run on Simulator
# =============================================================================
if [[ "$ACTION" == "ios-dev" ]]; then
  log_step "Starting iOS app on Simulator..."
  cd "${MOBILE_DIR}"
  npx react-native run-ios --simulator "iPhone 16 Pro"
  exit 0
fi

# =============================================================================
# iOS: Run on Connected Device
# =============================================================================
if [[ "$ACTION" == "ios-device" ]]; then
  log_step "Building for connected iPhone..."
  echo ""
  log_warn "Requirements:"
  echo "  1. iPhone connected via USB"
  echo "  2. Apple Developer account configured in Xcode"
  echo "  3. Device trusted (Settings > General > VPN & Device Management)"
  echo ""

  cd "${MOBILE_DIR}"
  npx react-native run-ios --device

  echo ""
  log_info "App installed on device!"
  log_warn "If this is the first time, go to:"
  log_warn "  iPhone Settings > General > VPN & Device Management"
  log_warn "  > Trust your developer certificate"
  exit 0
fi

# =============================================================================
# iOS: Build .ipa for Distribution
# =============================================================================
if [[ "$ACTION" == "ios-build" || "$ACTION" == "all" ]]; then
  log_step "Building iOS .ipa..."
  echo ""

  cd "${IOS_DIR}"

  # Ensure pods are installed
  pod install

  # Build archive
  log_step "Creating Xcode archive..."
  xcodebuild -workspace AITripPlanner.xcworkspace \
    -scheme AITripPlanner \
    -configuration Release \
    -sdk iphoneos \
    -archivePath "${BUILD_OUTPUT}/AITripPlanner.xcarchive" \
    archive \
    CODE_SIGN_IDENTITY="" \
    CODE_SIGNING_REQUIRED=NO \
    CODE_SIGNING_ALLOWED=NO \
    2>&1 | tail -5

  # If code signing is set up, create the .ipa
  if [[ -d "${BUILD_OUTPUT}/AITripPlanner.xcarchive" ]]; then
    log_info "Archive created at: ${BUILD_OUTPUT}/AITripPlanner.xcarchive"

    # Create ExportOptions for Ad Hoc or Development distribution
    cat > "${BUILD_OUTPUT}/ExportOptions.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>development</string>
    <key>compileBitcode</key>
    <false/>
    <key>stripSwiftSymbols</key>
    <true/>
</dict>
</plist>
PLIST

    log_step "Exporting .ipa..."
    xcodebuild -exportArchive \
      -archivePath "${BUILD_OUTPUT}/AITripPlanner.xcarchive" \
      -exportOptionsPlist "${BUILD_OUTPUT}/ExportOptions.plist" \
      -exportPath "${BUILD_OUTPUT}/ios" \
      2>&1 | tail -5 || log_warn "Export failed - see manual signing instructions below"

    if [[ -f "${BUILD_OUTPUT}/ios/AITripPlanner.ipa" ]]; then
      log_info "iOS .ipa built: ${BUILD_OUTPUT}/ios/AITripPlanner.ipa"
    else
      echo ""
      log_warn "Auto-export failed. To build manually with code signing:"
      echo ""
      echo "  1. Open: ${IOS_DIR}/AITripPlanner.xcworkspace"
      echo "  2. Select your Team in Signing & Capabilities"
      echo "  3. Product > Archive"
      echo "  4. Window > Organizer > Distribute App"
      echo "  5. Choose: Development / Ad Hoc / App Store"
      echo ""
    fi
  fi
fi

# =============================================================================
# Android: Build .apk
# =============================================================================
if [[ "$ACTION" == "android" || "$ACTION" == "all" ]]; then
  log_step "Building Android .apk..."

  if [[ ! -d "${ANDROID_DIR}" ]]; then
    log_error "Android project not found. Run './build-mobile.sh setup' first."
    exit 1
  fi

  cd "${ANDROID_DIR}"

  # Build release APK
  ./gradlew assembleRelease 2>&1 | tail -10

  APK_PATH="${ANDROID_DIR}/app/build/outputs/apk/release/app-release.apk"
  if [[ -f "$APK_PATH" ]]; then
    cp "$APK_PATH" "${BUILD_OUTPUT}/AITripPlanner.apk"
    log_info "Android APK built: ${BUILD_OUTPUT}/AITripPlanner.apk"
  else
    # Try unsigned
    APK_PATH="${ANDROID_DIR}/app/build/outputs/apk/release/app-release-unsigned.apk"
    if [[ -f "$APK_PATH" ]]; then
      cp "$APK_PATH" "${BUILD_OUTPUT}/AITripPlanner-unsigned.apk"
      log_info "Android APK (unsigned): ${BUILD_OUTPUT}/AITripPlanner-unsigned.apk"
    fi
  fi
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "======================================="
echo "  Build Output: ${BUILD_OUTPUT}/"
echo "======================================="
ls -lh "${BUILD_OUTPUT}/" 2>/dev/null || true
echo ""
echo "  Upload to:"
echo "    - TestFlight:    Xcode Organizer > Distribute (recommended for iOS)"
echo "    - Google Drive:  Upload .ipa / .apk manually"
echo "    - AWS S3:        aws s3 cp ${BUILD_OUTPUT}/AITripPlanner.apk s3://your-bucket/"
echo "    - Play Store:    Use .aab (bundleRelease) for Google Play"
echo "======================================="
