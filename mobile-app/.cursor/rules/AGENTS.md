# Blood Donation App - Cursor Rules

## Project Overview
This is a React Native Expo blood donation app with Firebase backend, featuring donor/patient modes, real-time requests, Stripe payments, and organization management. The app uses TypeScript, Expo Router for navigation, and follows a strict data access pattern through `lib/*` modules.

## Architecture & Patterns

### Core Architecture
- **Framework**: React Native with Expo SDK 53
- **Navigation**: Expo Router with file-based routing
- **State Management**: React Context (ThemeContext, ModeContext)
- **Backend**: Firebase Realtime Database
- **Payments**: Stripe integration
- **Styling**: StyleSheet with theme-aware colors
- **Type Safety**: Full TypeScript with strict mode

### File Structure Conventions
```
app/                    # Expo Router pages
├── (tabs)/            # Tab navigation screens
├── auth/              # Authentication flow
├── org/               # Organization console
├── organizations/     # Public organization pages
├── profile/           # User profile pages
├── request/           # Blood request pages
└── donations/         # Donation management

lib/                   # Data access layer (NO direct Firebase in UI)
├── users.ts          # User profile operations
├── requests.ts       # Blood request operations
├── donations.ts      # Donation tracking
├── organizations.ts  # Organization management
├── drives.ts         # Blood drive management
└── types.ts          # TypeScript type definitions

context/              # React Context providers
├── ThemeContext.tsx  # Theme management (light/dark/system)
└── ModeContext.tsx   # App mode (donor/patient)

components/           # Reusable UI components
├── ui/               # UI component library
└── SelectModal.tsx   # Custom modal components

constants/            # App constants
└── Colors.ts         # Theme-aware color definitions

database/             # Firebase configuration
└── firebase.ts       # Firebase setup and exports
```

## Code Standards

### TypeScript Rules
- **Strict Mode**: Always use strict TypeScript with proper type annotations
- **Type Definitions**: All data models defined in `lib/types.ts`
- **Path Aliases**: Use `@/` for imports from project root
- **No Any Types**: Avoid `any` - use proper typing or `unknown`
- **Interface vs Type**: Use `type` for data models, `interface` for component props

### Data Access Pattern
- **NEVER** import Firebase directly in UI components
- **ALWAYS** use `lib/*` modules for data operations
- **Authentication**: Check `auth.currentUser` before data operations
- **Error Handling**: Wrap data operations in try-catch blocks
- **Timestamps**: Use `Date.now()` for all timestamps (milliseconds)

### Component Patterns
- **Functional Components**: Use React functional components with hooks
- **Props Interface**: Define clear prop interfaces for all components
- **Theme Integration**: Always use `Colors[theme]` for styling
- **Mode Awareness**: Check `useMode()` for donor/patient specific logic
- **Responsive Design**: Use `Dimensions.get('window')` for responsive layouts
- **Scrollable Content**: All screens must support scrolling when content overflows

### Styling Guidelines
- **StyleSheet**: Use `StyleSheet.create()` for all styles
- **Theme Colors**: Reference `Colors[colorScheme]` for all colors
- **Consistent Spacing**: Use 8px grid system (8, 16, 24, 32px)
- **Border Radius**: Use 8px, 12px, or 16px for consistent rounded corners
- **Typography**: Use system fonts with consistent weight hierarchy

### State Management
- **Context Usage**: Use ThemeContext and ModeContext for global state
- **Local State**: Use `useState` for component-specific state
- **Async State**: Use loading states for async operations
- **Optimistic Updates**: Update UI immediately, reconcile on error

## Firebase Integration

### Database Structure
```
users/{uid}                    # User profiles
requests/{id}                  # Blood requests
donations/{uid}/{id}           # Blood donations
money_donations/{uid}/{id}     # Money donations
comments/{requestId}/{id}      # Request comments
```

### Data Operations
- **Path Safety**: Use `pathSafeKey()` for Firebase keys
- **Undefined Handling**: Strip undefined values before Firebase writes
- **Batch Operations**: Use `update()` for multiple field updates
- **Error Handling**: Always handle Firebase errors gracefully

### Security Rules
- **Authentication Required**: All write operations require authentication
- **Owner Access**: Users can only modify their own data
- **Public Read**: Most data is publicly readable
- **Admin Override**: Admin can modify verification flags

### Node.js Backend (Stripe Only)
- **Stripe Integration**: All Stripe secret key operations handled via Node.js backend
- **Payment Intents**: Create Stripe payment intents server-side for money donations
- **Webhook Handling**: Process Stripe webhooks to update database records
- **Environment Variables**: Store sensitive keys in Node.js backend environment
- **Error Handling**: Provide proper error responses for failed operations
- **Database Access**: Firebase Admin SDK for storing donation records after successful payments
- **Purpose**: Handle only Stripe payment processing, not general API operations

## Navigation & Routing

### Expo Router Conventions
- **File-based Routing**: Use folder structure for navigation
- **Tab Navigation**: Main app uses `(tabs)` layout
- **Auth Guards**: Redirect to login if not authenticated
- **Deep Linking**: Support deep links for requests and profiles

### Screen Patterns
- **Header Configuration**: Consistent header styling and actions
- **Loading States**: Show loading indicators for async operations
- **Error Boundaries**: Handle errors gracefully with user feedback
- **Empty States**: Provide meaningful empty state messages
- **Scrollable Layout**: Use ScrollView or FlatList for screens with potential content overflow

## Theme System

### Theme Implementation
- **System Respect**: Default to system theme preference
- **Manual Override**: Allow user to override theme in profile
- **Persistence**: Save theme preference to user profile and local storage
- **Complete App Theme**: Theme changes affect the entire app, not just navigation
- **Status Bar**: Update status bar style based on theme
- **Global Application**: All screens, components, and UI elements update with theme changes

### Color Usage
- **Light Theme**: Pure white backgrounds (#FFFFFF) with black text (#000000)
- **Dark Theme**: Pure black backgrounds (#000000) with white text (#FFFFFF)
- **Semantic Colors**: Use semantic color names (text, background, border)
- **Accessibility**: Ensure sufficient contrast ratios

## App Modes

### Donor Mode
- **Features**: Donor inbox, availability toggle, accept requests, view urgent requests
- **UI Changes**: Show donor-specific tabs and actions, hide Donors List and Request Blood tabs
- **Permissions**: Can accept blood requests and manage availability
- **Hidden Tabs**: Donors List and Request Blood tabs are not applicable for donors
- **Urgent Requests**: Can view and accept urgent blood requests
- **Automatic Donation Tracking**: Donation records are automatically created when accepting requests; no manual recording needed

### Patient Mode
- **Features**: Request blood, find donors, manage requests
- **UI Changes**: Show Donors List and Request Blood tabs, hide donor-specific features
- **Permissions**: Can create requests and contact donors
- **Visible Tabs**: Donors List and Request Blood tabs are only available for patients
- **Urgent Requests**: Cannot view urgent requests (not applicable for patients)

### Mode Switching
- **Persistence**: Save mode preference to user profile
- **UI Updates**: Update UI immediately when mode changes
- **Context Usage**: Use `useMode()` hook for mode-aware logic

## Payment Integration

### Stripe Configuration
- **Environment Variables**: Use `EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY` for client-side
- **Provider Setup**: Wrap app with `StripeProvider`
- **Payment Flows**: Money donations via Node.js backend
- **Security**: Never expose secret keys to client; use Node.js backend for all sensitive operations
- **Receipt Handling**: Store receipt URLs in database

### Payment Patterns
- **Payment Intent Creation**: Call Node.js backend to create Stripe payment intents for payments
- **Webhook Handling**: Handle payment confirmations via Node.js backend webhooks
- **Error Handling**: Provide clear error messages for payment failures
- **Security**: All Stripe secret key operations must be handled server-side via Node.js backend

## Performance & Optimization

### Best Practices
- **Batch Reads**: Minimize Firebase reads with batch operations
- **Debounce Search**: Debounce search inputs to reduce API calls
- **Image Optimization**: Use `expo-image` for optimized image loading
- **Lazy Loading**: Load data only when needed

### Memory Management
- **Cleanup**: Clean up listeners and subscriptions
- **State Updates**: Avoid unnecessary re-renders
- **Image Caching**: Use proper image caching strategies

## Error Handling

### Error Categories
- **Authentication**: `auth/not-authenticated`, `auth/forbidden`
- **Input Validation**: `input/invalid` with field hints
- **Data**: `data/not-found` for missing records
- **Network**: `net/unavailable` for connectivity issues

### User Feedback
- **Alert Dialogs**: Use `Alert.alert()` for important messages
- **Loading States**: Show loading indicators during operations
- **Error Recovery**: Provide retry options for failed operations

## Testing & Development

### Development Tools
- **ESLint**: Use Expo ESLint configuration
- **TypeScript**: Enable strict mode and path mapping
- **Hot Reload**: Use Expo development server
- **Debugging**: Use React Native debugger

### Seeding Data
- **Seed Script**: Use `scripts/seed.ts` for development data
- **Realistic Data**: Create realistic test data for all entities
- **Clean Slate**: Reset database before seeding

## Security Considerations

### Data Protection
- **Input Validation**: Validate all user inputs
- **Path Sanitization**: Sanitize Firebase paths
- **Authentication**: Verify user identity for all operations
- **Rate Limiting**: Implement rate limiting for API calls

### Privacy
- **PII Handling**: Handle personal information carefully
- **Data Retention**: Implement data retention policies
- **User Consent**: Get explicit consent for data collection

## Accessibility

### Guidelines
- **Touch Targets**: Minimum 44px touch targets
- **Color Contrast**: Ensure sufficient color contrast
- **Screen Readers**: Support screen reader navigation
- **Keyboard Navigation**: Support keyboard navigation where applicable

### Implementation
- **Semantic Elements**: Use semantic HTML elements
- **ARIA Labels**: Add ARIA labels for complex interactions
- **Focus Management**: Manage focus for modal dialogs
- **Text Scaling**: Support dynamic text scaling

## Common Patterns

### Data Fetching
```typescript
const [data, setData] = useState<Type[]>([]);
const [loading, setLoading] = useState(true);

useEffect(() => {
  (async () => {
    try {
      const result = await getData();
      setData(result);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  })();
}, []);
```

### Scrollable Screen Layout
```typescript
import { ScrollView } from 'react-native';

<ScrollView 
  style={styles.container}
  contentContainerStyle={styles.contentContainer}
  showsVerticalScrollIndicator={false}
>
  {/* Screen content */}
</ScrollView>
```

### Theme Integration
```typescript
const { theme } = useThemeCustom();
const colorScheme = useColorScheme() ?? 'light';

<View style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}>
  <Text style={[styles.text, { color: Colors[colorScheme].text }]}>
    Content
  </Text>
</View>
```

### Mode-Aware Logic
```typescript
const { mode } = useMode();

// Show/hide tabs based on mode
{mode === 'donor' && (
  <TouchableOpacity onPress={handleDonorAction}>
    <Text>Donor Action</Text>
  </TouchableOpacity>
)}

{mode === 'patient' && (
  <TouchableOpacity onPress={handlePatientAction}>
    <Text>Patient Action</Text>
  </TouchableOpacity>
)}
```

### Donation Tracking
```typescript
// Donation records are automatically created when donors accept requests
// No manual "Record Donation" button needed - this happens automatically
const handleAcceptRequest = async (requestId: string) => {
  await acceptRequest(requestId); // This automatically creates donation record
  // No additional donation recording step required
};
```

### Tab Visibility Logic
```typescript
// In tab layout configuration
const getVisibleTabs = (mode: 'donor' | 'patient') => {
  if (mode === 'donor') {
    return ['home', 'donate', 'history', 'inbox', 'profile'];
  } else {
    return ['home', 'donors', 'request', 'donate', 'history', 'profile'];
  }
};
```

### Urgent Requests Visibility
```typescript
// Show urgent requests only to donors
const { mode } = useMode();

{mode === 'donor' && (
  <UrgentRequestsSection />
)}
```

### Error Handling
```typescript
try {
  await performOperation();
  Alert.alert('Success', 'Operation completed successfully');
} catch (error: any) {
  Alert.alert('Error', error?.message ?? 'Operation failed');
}
```

### Node.js Backend Integration
```typescript
const BACKEND_URL = 'https://your-backend.herokuapp.com'; // or your domain

const createPaymentIntent = async (amount: number, purpose?: string) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/create-payment-intent`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userToken}` // Firebase auth token
      },
      body: JSON.stringify({ amount, purpose })
    });
    const result = await response.json();
    return result.clientSecret;
  } catch (error) {
    Alert.alert('Error', 'Failed to create payment intent');
  }
};

const confirmPayment = async (paymentIntentId: string, paymentMethodId: string) => {
  try {
    // Use Stripe SDK directly on client-side for payment confirmation
    const { error } = await stripe.confirmPayment({
      clientSecret: paymentIntentId,
      confirmParams: {
        payment_method: paymentMethodId,
      },
    });
    
    if (error) {
      throw new Error(error.message);
    }
    
    return true;
  } catch (error) {
    Alert.alert('Error', 'Failed to confirm payment');
    return false;
  }
};
```

## File Naming Conventions
- **Components**: PascalCase (e.g., `SelectModal.tsx`)
- **Pages**: kebab-case (e.g., `request-blood.tsx`)
- **Utilities**: camelCase (e.g., `formatDate.ts`)
- **Types**: PascalCase (e.g., `UserProfile`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_ENDPOINTS`)

## Import Organization
1. React and React Native imports
2. Third-party library imports
3. Expo imports
4. Local imports (components, lib, context, etc.)
5. Type imports (with `type` keyword)

## Comments & Documentation
- **Function Comments**: Document complex business logic
- **Type Comments**: Document complex type definitions
- **TODO Comments**: Use `// TODO:` for future improvements
- **FIXME Comments**: Use `// FIXME:` for known issues

## Git Conventions
- **Commit Messages**: Use conventional commits format
- **Branch Naming**: Use feature/ prefix for features
- **Pull Requests**: Include description of changes and testing
- **Code Review**: Review for adherence to these rules

Remember: This app saves lives through efficient donor matching. Code quality, user experience, and data integrity are paramount. Always consider the human impact of your code changes.
