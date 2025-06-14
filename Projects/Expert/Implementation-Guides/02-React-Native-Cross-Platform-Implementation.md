# React Native Cross-Platform Implementation Guide
*Expert Level Implementation: Professional multi-platform mobile application with advanced features*

## Learning Objectives

By completing this implementation, you will master:

- **Advanced React Native Architecture** - Enterprise-level code organization and patterns
- **Cross-Platform Navigation** - Complex navigation flows with platform-specific adaptations
- **State Management** - Redux Toolkit with RTK Query and offline synchronization
- **Native Module Integration** - Custom native modules and third-party library integration
- **Performance Optimization** - Memory management, bundle optimization, and native performance
- **Advanced UI/UX** - Custom animations, gesture handling, and platform-specific designs
- **Backend Integration** - API integration with error handling and caching strategies
- **Testing Strategy** - Unit, integration, and E2E testing for mobile applications
- **CI/CD Pipeline** - Automated building, testing, and deployment for both platforms
- **Security Implementation** - Biometric authentication, secure storage, and API security

## Quick Start (60 Minutes)

### Prerequisites Verification

```bash
# Verify Node.js and npm
node --version  # Should be >= 16.x
npm --version   # Should be >= 8.x

# Verify React Native CLI
npx react-native --version

# Verify platform-specific requirements
# For iOS (macOS only):
xcode-select --install
pod --version

# For Android:
# Ensure Android Studio is installed with SDK
echo $ANDROID_HOME
```

### Project Initialization

```bash
# Create new React Native project
npx react-native init CrossPlatformApp --template react-native-template-typescript

cd CrossPlatformApp

# Install essential dependencies
npm install @reduxjs/toolkit react-redux redux-persist
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context
npm install react-native-gesture-handler react-native-reanimated
npm install @react-native-async-storage/async-storage
npm install react-native-keychain react-native-biometrics
npm install react-native-vector-icons react-native-svg
npm install @shopify/restyle styled-components
npm install react-native-paper react-native-elements

# Development dependencies
npm install --save-dev @types/react-native
npm install --save-dev detox jest @testing-library/react-native
npm install --save-dev flipper-plugin-redux-debugger
npm install --save-dev babel-plugin-module-resolver
```

### Platform-Specific Setup

```bash
# iOS setup (macOS only)
cd ios && pod install && cd ..

# Android setup - ensure emulator is running
npx react-native run-android

# iOS setup
npx react-native run-ios
```

## Project Architecture

### Directory Structure

```
src/
├── components/           # Reusable UI components
│   ├── common/          # Cross-platform components
│   ├── ios/            # iOS-specific components
│   └── android/        # Android-specific components
├── screens/            # Screen components
├── navigation/         # Navigation configuration
├── store/             # Redux store and slices
├── services/          # API and external services
├── hooks/             # Custom React hooks
├── utils/             # Utility functions
├── types/             # TypeScript type definitions
├── assets/            # Images, fonts, etc.
├── native/            # Native module interfaces
└── __tests__/         # Test files
```

### Core Architecture Implementation

```typescript
// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { combineReducers } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import userSlice from './slices/userSlice';
import appSlice from './slices/appSlice';
import { api } from './services/api';

const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['auth', 'user', 'app'],
};

const rootReducer = combineReducers({
  auth: authSlice,
  user: userSlice,
  app: appSlice,
  [api.reducerPath]: api.reducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }).concat(api.middleware),
});

export const persistor = persistStore(store);
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

```typescript
// src/store/slices/authSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { User } from '../../types/user';

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  biometricEnabled: boolean;
}

const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  biometricEnabled: false,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.isLoading = true;
    },
    loginSuccess: (state, action: PayloadAction<{
      user: User;
      token: string;
      refreshToken: string;
    }>) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.refreshToken = action.payload.refreshToken;
      state.isAuthenticated = true;
      state.isLoading = false;
    },
    loginFailure: (state) => {
      state.isLoading = false;
      state.isAuthenticated = false;
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
    },
    enableBiometric: (state) => {
      state.biometricEnabled = true;
    },
    disableBiometric: (state) => {
      state.biometricEnabled = false;
    },
  },
});

export const {
  loginStart,
  loginSuccess,
  loginFailure,
  logout,
  enableBiometric,
  disableBiometric,
} = authSlice.actions;

export default authSlice.reducer;
```

## Advanced Navigation System

### Navigation Structure Implementation

```typescript
// src/navigation/AppNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import AuthNavigator from './AuthNavigator';
import MainNavigator from './MainNavigator';
import { navigationRef } from './NavigationService';

const Stack = createStackNavigator();

const AppNavigator: React.FC = () => {
  const isAuthenticated = useSelector(
    (state: RootState) => state.auth.isAuthenticated
  );

  return (
    <NavigationContainer ref={navigationRef}>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="Main" component={MainNavigator} />
        ) : (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
```

```typescript
// src/navigation/MainNavigator.tsx
import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Platform } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import HomeScreen from '../screens/HomeScreen';
import ProfileScreen from '../screens/ProfileScreen';
import SettingsScreen from '../screens/SettingsScreen';
import NotificationsScreen from '../screens/NotificationsScreen';
import { colors } from '../theme/colors';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

const HomeStack = () => (
  <Stack.Navigator>
    <Stack.Screen name="HomeScreen" component={HomeScreen} />
    <Stack.Screen name="Notifications" component={NotificationsScreen} />
  </Stack.Navigator>
);

const ProfileStack = () => (
  <Stack.Navigator>
    <Stack.Screen name="ProfileScreen" component={ProfileScreen} />
    <Stack.Screen name="Settings" component={SettingsScreen} />
  </Stack.Navigator>
);

const MainNavigator: React.FC = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Home':
              iconName = 'home';
              break;
            case 'Profile':
              iconName = 'person';
              break;
            default:
              iconName = 'help';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.gray,
        tabBarStyle: {
          backgroundColor: colors.background,
          borderTopWidth: Platform.OS === 'ios' ? 0 : 1,
          elevation: Platform.OS === 'android' ? 8 : 0,
          shadowOpacity: Platform.OS === 'ios' ? 0.1 : 0,
          shadowRadius: Platform.OS === 'ios' ? 4 : 0,
          shadowOffset: Platform.OS === 'ios' ? { width: 0, height: -2 } : { width: 0, height: 0 },
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeStack} />
      <Tab.Screen name="Profile" component={ProfileStack} />
    </Tab.Navigator>
  );
};

export default MainNavigator;
```

## Advanced Authentication System

### Biometric Authentication Implementation

```typescript
// src/services/BiometricService.ts
import TouchID from 'react-native-biometrics';
import { Platform } from 'react-native';

export class BiometricService {
  static async checkBiometricSupport(): Promise<{
    available: boolean;
    biometryType: string | null;
  }> {
    try {
      const { available, biometryType } = await TouchID.isSensorAvailable();
      return { available, biometryType };
    } catch (error) {
      return { available: false, biometryType: null };
    }
  }

  static async authenticateWithBiometrics(
    reason: string = 'Authenticate to access your account'
  ): Promise<boolean> {
    try {
      const { success } = await TouchID.simplePrompt({
        promptMessage: reason,
        fallbackPromptMessage: 'Use Passcode',
        cancelButtonText: 'Cancel',
      });
      return success;
    } catch (error) {
      console.error('Biometric authentication failed:', error);
      return false;
    }
  }

  static async createBiometricKey(keyAlias: string): Promise<boolean> {
    try {
      const { success } = await TouchID.createKeys({
        keyAlias,
        promptMessage: 'Set up biometric authentication',
      });
      return success;
    } catch (error) {
      console.error('Failed to create biometric key:', error);
      return false;
    }
  }

  static async signWithBiometrics(
    keyAlias: string,
    payload: string
  ): Promise<{ success: boolean; signature?: string }> {
    try {
      const { success, signature } = await TouchID.createSignature({
        keyAlias,
        promptMessage: 'Sign in with biometrics',
        payload,
      });
      return { success, signature };
    } catch (error) {
      console.error('Biometric signing failed:', error);
      return { success: false };
    }
  }
}
```

```typescript
{% raw %}
{% raw %}
// src/services/AuthService.ts
import { Keychain } from 'react-native-keychain';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { BiometricService } from './BiometricService';

interface LoginCredentials {
  email: string;
  password: string;
}

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export class AuthService {
  private static readonly TOKENS_KEY = 'auth_tokens';
  private static readonly BIOMETRIC_KEY = 'biometric_auth';

  static async login(credentials: LoginCredentials): Promise<AuthTokens> {
    try {
      const response = await fetch('https://api.example.com/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      await this.storeTokens(data.tokens);
      return data.tokens;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  static async loginWithBiometrics(): Promise<AuthTokens | null> {
    try {
      const biometricSupport = await BiometricService.checkBiometricSupport();
      if (!biometricSupport.available) {
        throw new Error('Biometric authentication not available');
      }

      const authenticated = await BiometricService.authenticateWithBiometrics(
        'Authenticate to sign in'
      );

      if (!authenticated) {
        throw new Error('Biometric authentication failed');
      }

      const storedTokens = await this.getStoredTokens();
      if (storedTokens) {
        return storedTokens;
      }

      throw new Error('No stored credentials found');
    } catch (error) {
      console.error('Biometric login error:', error);
      return null;
    }
  }

  static async storeTokens(tokens: AuthTokens): Promise<void> {
    try {
      await Keychain.setInternetCredentials(
        this.TOKENS_KEY,
        tokens.accessToken,
        tokens.refreshToken
      );
    } catch (error) {
      console.error('Error storing tokens:', error);
      // Fallback to AsyncStorage
      await AsyncStorage.setItem(this.TOKENS_KEY, JSON.stringify(tokens));
    }
  }

  static async getStoredTokens(): Promise<AuthTokens | null> {
    try {
      const credentials = await Keychain.getInternetCredentials(this.TOKENS_KEY);
      if (credentials) {
        return {
          accessToken: credentials.username,
          refreshToken: credentials.password,
        };
      }
    } catch (error) {
      console.error('Error retrieving tokens from Keychain:', error);
      // Fallback to AsyncStorage
      try {
        const storedTokens = await AsyncStorage.getItem(this.TOKENS_KEY);
        return storedTokens ? JSON.parse(storedTokens) : null;
      } catch (asyncError) {
        console.error('Error retrieving tokens from AsyncStorage:', asyncError);
      }
    }
    return null;
  }

  static async refreshToken(refreshToken: string): Promise<AuthTokens> {
    try {
      const response = await fetch('https://api.example.com/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${refreshToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      await this.storeTokens(data.tokens);
      return data.tokens;
    } catch (error) {
      console.error('Token refresh error:', error);
      throw error;
    }
  }

  static async logout(): Promise<void> {
    try {
      await Keychain.resetInternetCredentials(this.TOKENS_KEY);
      await AsyncStorage.removeItem(this.TOKENS_KEY);
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
}
{% endraw %}
{% endraw %}
```

## Advanced UI Components

### Platform-Specific Components

```typescript
{% raw %}
{% raw %}
// src/components/common/PlatformButton.tsx
import React from 'react';
import {
  TouchableOpacity,
  Text,
  Platform,
  ViewStyle,
  TextStyle,
  ActivityIndicator,
} from 'react-native';
import styled from 'styled-components/native';
import { colors } from '../../theme/colors';

interface PlatformButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outlined';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

const StyledButton = styled(TouchableOpacity)<{
  variant: string;
  size: string;
  disabled: boolean;
}>`
  background-color: ${({ variant, disabled }) => {
    if (disabled) return colors.gray200;
    switch (variant) {
      case 'primary': return colors.primary;
      case 'secondary': return colors.secondary;
      case 'outlined': return 'transparent';
      default: return colors.primary;
    }
  }};
  border-width: ${({ variant }) => variant === 'outlined' ? '2px' : '0px'};
  border-color: ${colors.primary};
  border-radius: ${Platform.OS === 'ios' ? '12px' : '8px'};
  padding: ${({ size }) => {
    switch (size) {
      case 'small': return '8px 16px';
      case 'medium': return '12px 24px';
      case 'large': return '16px 32px';
      default: return '12px 24px';
    }
  }};
  align-items: center;
  justify-content: center;
  min-height: ${({ size }) => {
    switch (size) {
      case 'small': return '36px';
      case 'medium': return '48px';
      case 'large': return '56px';
      default: return '48px';
    }
  }};
  elevation: ${Platform.OS === 'android' ? '2' : '0'};
  shadow-color: ${Platform.OS === 'ios' ? colors.primary : 'transparent'};
  shadow-offset: ${Platform.OS === 'ios' ? '0px 2px' : '0px 0px'};
  shadow-opacity: ${Platform.OS === 'ios' ? '0.1' : '0'};
  shadow-radius: ${Platform.OS === 'ios' ? '4px' : '0px'};
`;

const ButtonText = styled(Text)<{
  variant: string;
  size: string;
  disabled: boolean;
}>`
  color: ${({ variant, disabled }) => {
    if (disabled) return colors.gray500;
    switch (variant) {
      case 'primary': return colors.white;
      case 'secondary': return colors.white;
      case 'outlined': return colors.primary;
      default: return colors.white;
    }
  }};
  font-size: ${({ size }) => {
    switch (size) {
      case 'small': return '14px';
      case 'medium': return '16px';
      case 'large': return '18px';
      default: return '16px';
    }
  }};
  font-weight: ${Platform.OS === 'ios' ? '600' : 'bold'};
  text-align: center;
`;

const PlatformButton: React.FC<PlatformButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  style,
  textStyle,
}) => {
  return (
    <StyledButton
      variant={variant}
      size={size}
      disabled={disabled || loading}
      onPress={onPress}
      style={style}
      activeOpacity={0.7}
    >
      {loading ? (
        <ActivityIndicator
          color={variant === 'outlined' ? colors.primary : colors.white}
          size="small"
        />
      ) : (
        <ButtonText
          variant={variant}
          size={size}
          disabled={disabled}
          style={textStyle}
        >
          {title}
        </ButtonText>
      )}
    </StyledButton>
  );
};

export default PlatformButton;
{% endraw %}
{% endraw %}
```

### Advanced Animation Components

```typescript
{% raw %}
{% raw %}
// src/components/common/AnimatedCard.tsx
import React, { useRef, useEffect } from 'react';
import {
  Animated,
  PanGestureHandler,
  PanGestureHandlerGestureEvent,
  State,
} from 'react-native-gesture-handler';
import { Dimensions, ViewStyle } from 'react-native';
import styled from 'styled-components/native';
import { colors } from '../../theme/colors';

const { width: screenWidth } = Dimensions.get('window');

interface AnimatedCardProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  style?: ViewStyle;
  swipeThreshold?: number;
}

const CardContainer = styled(Animated.View)`
  background-color: ${colors.white};
  border-radius: 16px;
  padding: 20px;
  margin: 10px;
  shadow-color: ${colors.gray900};
  shadow-offset: 0px 4px;
  shadow-opacity: 0.1;
  shadow-radius: 8px;
  elevation: 5;
`;

const AnimatedCard: React.FC<AnimatedCardProps> = ({
  children,
  onSwipeLeft,
  onSwipeRight,
  style,
  swipeThreshold = screenWidth * 0.3,
}) => {
  const translateX = useRef(new Animated.Value(0)).current;
  const opacity = useRef(new Animated.Value(1)).current;
  const scale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Entry animation
    Animated.parallel([
      Animated.timing(opacity, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.spring(scale, {
        toValue: 1,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const onGestureEvent = Animated.event(
    [{ nativeEvent: { translationX: translateX } }],
    { useNativeDriver: true }
  );

  const onHandlerStateChange = (event: PanGestureHandlerGestureEvent) => {
    if (event.nativeEvent.state === State.END) {
      const { translationX } = event.nativeEvent;

      if (translationX > swipeThreshold && onSwipeRight) {
        // Swipe right
        Animated.parallel([
          Animated.timing(translateX, {
            toValue: screenWidth,
            duration: 300,
            useNativeDriver: true,
          }),
          Animated.timing(opacity, {
            toValue: 0,
            duration: 300,
            useNativeDriver: true,
          }),
        ]).start(() => onSwipeRight());
      } else if (translationX < -swipeThreshold && onSwipeLeft) {
        // Swipe left
        Animated.parallel([
          Animated.timing(translateX, {
            toValue: -screenWidth,
            duration: 300,
            useNativeDriver: true,
          }),
          Animated.timing(opacity, {
            toValue: 0,
            duration: 300,
            useNativeDriver: true,
          }),
        ]).start(() => onSwipeLeft());
      } else {
        // Return to center
        Animated.spring(translateX, {
          toValue: 0,
          tension: 50,
          friction: 7,
          useNativeDriver: true,
        }).start();
      }
    }
  };

  const cardStyle = {
    transform: [
      { translateX },
      { scale },
      {
        rotate: translateX.interpolate({
          inputRange: [-screenWidth, 0, screenWidth],
          outputRange: ['-15deg', '0deg', '15deg'],
          extrapolate: 'clamp',
        }),
      },
    ],
    opacity,
  };

  return (
    <PanGestureHandler
      onGestureEvent={onGestureEvent}
      onHandlerStateChange={onHandlerStateChange}
    >
      <CardContainer style={[cardStyle, style]}>
        {children}
      </CardContainer>
    </PanGestureHandler>
  );
};

export default AnimatedCard;
{% endraw %}
{% endraw %}
```

## Advanced API Integration

### RTK Query API Service

```typescript
{% raw %}
{% raw %}
// src/store/services/api.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { RootState } from '../index';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

interface Post {
  id: string;
  title: string;
  content: string;
  author: User;
  createdAt: string;
  updatedAt: string;
  likes: number;
  comments: Comment[];
}

interface Comment {
  id: string;
  content: string;
  author: User;
  createdAt: string;
}

interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Cache management
const CACHE_DURATION = 60; // seconds

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: 'https://api.example.com/',
    prepareHeaders: async (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      headers.set('Content-Type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['User', 'Post', 'Comment'],
  endpoints: (builder) => ({
    // User endpoints
    getCurrentUser: builder.query<User, void>({
      query: () => 'users/me',
      providesTags: ['User'],
      keepUnusedDataFor: CACHE_DURATION,
    }),
    updateUser: builder.mutation<User, Partial<User>>({
      query: (userData) => ({
        url: 'users/me',
        method: 'PATCH',
        body: userData,
      }),
      invalidatesTags: ['User'],
    }),
    uploadAvatar: builder.mutation<{ avatarUrl: string }, FormData>({
      query: (formData) => ({
        url: 'users/avatar',
        method: 'POST',
        body: formData,
      }),
      invalidatesTags: ['User'],
    }),

    // Posts endpoints
    getPosts: builder.query<PaginatedResponse<Post>, {
      page?: number;
      limit?: number;
      search?: string;
    }>({
      query: ({ page = 1, limit = 10, search }) => ({
        url: 'posts',
        params: { page, limit, search },
      }),
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Post' as const, id })),
              { type: 'Post', id: 'LIST' },
            ]
          : [{ type: 'Post', id: 'LIST' }],
      serializeQueryArgs: ({ queryArgs }) => {
        const { page, ...otherArgs } = queryArgs;
        return otherArgs;
      },
      merge: (currentCache, newItems, { arg }) => {
        if (arg.page === 1) {
          return newItems;
        }
        return {
          ...newItems,
          data: [...currentCache.data, ...newItems.data],
        };
      },
      forceRefetch: ({ currentArg, previousArg }) => {
        return currentArg?.page !== previousArg?.page;
      },
      keepUnusedDataFor: CACHE_DURATION,
    }),
    getPost: builder.query<Post, string>({
      query: (id) => `posts/${id}`,
      providesTags: (result, error, id) => [{ type: 'Post', id }],
      keepUnusedDataFor: CACHE_DURATION,
    }),
    createPost: builder.mutation<Post, Omit<Post, 'id' | 'author' | 'createdAt' | 'updatedAt' | 'likes' | 'comments'>>({
      query: (postData) => ({
        url: 'posts',
        method: 'POST',
        body: postData,
      }),
      invalidatesTags: [{ type: 'Post', id: 'LIST' }],
    }),
    updatePost: builder.mutation<Post, { id: string; data: Partial<Post> }>({
      query: ({ id, data }) => ({
        url: `posts/${id}`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Post', id },
        { type: 'Post', id: 'LIST' },
      ],
    }),
    deletePost: builder.mutation<void, string>({
      query: (id) => ({
        url: `posts/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, id) => [
        { type: 'Post', id },
        { type: 'Post', id: 'LIST' },
      ],
    }),
    likePost: builder.mutation<{ likes: number }, string>({
      query: (id) => ({
        url: `posts/${id}/like`,
        method: 'POST',
      }),
      async onQueryStarted(id, { dispatch, queryFulfilled }) {
        // Optimistic update
        const patchResult = dispatch(
          api.util.updateQueryData('getPost', id, (draft) => {
            draft.likes += 1;
          })
        );
        try {
          await queryFulfilled;
        } catch {
          patchResult.undo();
        }
      },
    }),

    // Comments endpoints
    getComments: builder.query<Comment[], string>({
      query: (postId) => `posts/${postId}/comments`,
      providesTags: (result, error, postId) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: 'Comment' as const, id })),
              { type: 'Comment', id: `POST_${postId}` },
            ]
          : [{ type: 'Comment', id: `POST_${postId}` }],
      keepUnusedDataFor: CACHE_DURATION,
    }),
    createComment: builder.mutation<Comment, { postId: string; content: string }>({
      query: ({ postId, content }) => ({
        url: `posts/${postId}/comments`,
        method: 'POST',
        body: { content },
      }),
      invalidatesTags: (result, error, { postId }) => [
        { type: 'Comment', id: `POST_${postId}` },
        { type: 'Post', id: postId },
      ],
    }),
  }),
});

export const {
  useGetCurrentUserQuery,
  useUpdateUserMutation,
  useUploadAvatarMutation,
  useGetPostsQuery,
  useGetPostQuery,
  useCreatePostMutation,
  useUpdatePostMutation,
  useDeletePostMutation,
  useLikePostMutation,
  useGetCommentsQuery,
  useCreateCommentMutation,
} = api;

// Offline synchronization
export const offlineSync = {
  async syncPendingRequests() {
    try {
      const pendingRequests = await AsyncStorage.getItem('pendingRequests');
      if (pendingRequests) {
        const requests = JSON.parse(pendingRequests);
        // Process pending requests when online
        for (const request of requests) {
          // Implement retry logic
        }
        await AsyncStorage.removeItem('pendingRequests');
      }
    } catch (error) {
      console.error('Offline sync error:', error);
    }
  },
};
{% endraw %}
{% endraw %}
```

## Performance Optimization

### Memory Management and Performance

```typescript
{% raw %}
{% raw %}
// src/hooks/usePerformanceMonitor.ts
import { useEffect, useRef } from 'react';
import { InteractionManager, Platform } from 'react-native';

interface PerformanceMetrics {
  renderTime: number;
  memoryUsage?: number;
  interactionTime: number;
}

export const usePerformanceMonitor = (componentName: string) => {
  const startTime = useRef<number>(Date.now());
  const interactionStart = useRef<number>(Date.now());

  useEffect(() => {
    const endTime = Date.now();
    const renderTime = endTime - startTime.current;

    // Log performance metrics
    console.log(`[Performance] ${componentName} render time: ${renderTime}ms`);

    // Track interaction ready time
    InteractionManager.runAfterInteractions(() => {
      const interactionTime = Date.now() - interactionStart.current;
      console.log(`[Performance] ${componentName} interaction ready: ${interactionTime}ms`);
    });

    // Memory monitoring (Android specific)
    if (Platform.OS === 'android' && __DEV__) {
      try {
        const memoryInfo = require('react-native').PerformanceObserver;
        // Implementation for memory monitoring
      } catch (error) {
        console.warn('Memory monitoring not available');
      }
    }
  }, [componentName]);

  return {
    markInteractionStart: () => {
      interactionStart.current = Date.now();
    },
    markRenderStart: () => {
      startTime.current = Date.now();
    },
  };
};
{% endraw %}
{% endraw %}
```

```typescript
// src/components/optimized/OptimizedFlatList.tsx
import React, { useMemo, useCallback } from 'react';
import {
  FlatList,
  FlatListProps,
  ViewStyle,
  Platform,
  Dimensions,
} from 'react-native';

const { height: screenHeight } = Dimensions.get('window');

interface OptimizedFlatListProps<T> extends Omit<FlatListProps<T>, 'data'> {
  data: T[];
  itemHeight?: number;
  overscanCount?: number;
}

function OptimizedFlatList<T>({
  data,
  renderItem,
  itemHeight = 100,
  overscanCount = 5,
  ...props
}: OptimizedFlatListProps<T>) {
  const getItemLayout = useCallback(
    (data: any, index: number) => ({
      length: itemHeight,
      offset: itemHeight * index,
      index,
    }),
    [itemHeight]
  );

  const keyExtractor = useCallback(
    (item: any, index: number) => {
      return item.id || item.key || index.toString();
    },
    []
  );

  const optimizedProps = useMemo(() => ({
    // Performance optimizations
    removeClippedSubviews: Platform.OS === 'android',
    maxToRenderPerBatch: 10,
    updateCellsBatchingPeriod: 50,
    initialNumToRender: Math.ceil(screenHeight / itemHeight) + overscanCount,
    windowSize: 10,
    
    // Memory optimizations
    getItemLayout: itemHeight > 0 ? getItemLayout : undefined,
    keyExtractor,
    
    // Scroll optimizations
    disableVirtualization: false,
    legacyImplementation: false,
  }), [itemHeight, overscanCount, getItemLayout, keyExtractor]);

  return (
    <FlatList
      data={data}
      renderItem={renderItem}
      {...optimizedProps}
      {...props}
    />
  );
}

export default OptimizedFlatList;
```

### Image Optimization

```typescript
{% raw %}
{% raw %}
// src/components/common/OptimizedImage.tsx
import React, { useState, useCallback } from 'react';
import {
  Image,
  ImageProps,
  View,
  ActivityIndicator,
  Platform,
} from 'react-native';
import FastImage from 'react-native-fast-image';
import styled from 'styled-components/native';
import { colors } from '../../theme/colors';

interface OptimizedImageProps extends Omit<ImageProps, 'source'> {
  source: { uri: string } | number;
  placeholder?: React.ReactNode;
  fallback?: React.ReactNode;
  cachePolicy?: 'memory' | 'disk' | 'hybrid';
  priority?: 'low' | 'normal' | 'high';
  blur?: boolean;
}

const ImageContainer = styled(View)`
  position: relative;
  overflow: hidden;
`;

const LoadingContainer = styled(View)`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  justify-content: center;
  align-items: center;
  background-color: ${colors.gray100};
`;

const OptimizedImage: React.FC<OptimizedImageProps> = ({
  source,
  style,
  placeholder,
  fallback,
  cachePolicy = 'hybrid',
  priority = 'normal',
  blur = false,
  ...props
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const handleLoadStart = useCallback(() => {
    setLoading(true);
    setError(false);
  }, []);

  const handleLoadEnd = useCallback(() => {
    setLoading(false);
  }, []);

  const handleError = useCallback(() => {
    setLoading(false);
    setError(true);
  }, []);

  if (error && fallback) {
    return <>{fallback}</>;
  }

  const ImageComponent = Platform.OS === 'ios' ? FastImage : Image;

  const imageProps = Platform.OS === 'ios' ? {
    source: typeof source === 'object' ? {
      ...source,
      priority: FastImage.priority[priority],
      cache: FastImage.cacheControl[cachePolicy],
    } : source,
    onLoadStart: handleLoadStart,
    onLoadEnd: handleLoadEnd,
    onError: handleError,
    resizeMode: FastImage.resizeMode.cover,
  } : {
    source,
    onLoadStart: handleLoadStart,
    onLoadEnd: handleLoadEnd,
    onError: handleError,
    resizeMode: 'cover' as const,
  };

  return (
    <ImageContainer style={style}>
      <ImageComponent
        {...imageProps}
        {...props}
        style={[
          style,
          blur && { opacity: 0.8 },
        ]}
      />
      {loading && (
        <LoadingContainer>
          {placeholder || (
            <ActivityIndicator
              size="small"
              color={colors.primary}
            />
          )}
        </LoadingContainer>
      )}
    </ImageContainer>
  );
};

export default OptimizedImage;
{% endraw %}
{% endraw %}
```

## Advanced Testing Strategy

### Component Testing

```typescript
// src/__tests__/components/PlatformButton.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import PlatformButton from '../../components/common/PlatformButton';

describe('PlatformButton', () => {
  it('renders correctly with default props', () => {
    const { getByText } = render(
      <PlatformButton title="Test Button" onPress={() => {}} />
    );
    
    expect(getByText('Test Button')).toBeTruthy();
  });

  it('calls onPress when pressed', () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(
      <PlatformButton title="Test Button" onPress={mockOnPress} />
    );
    
    fireEvent.press(getByText('Test Button'));
    expect(mockOnPress).toHaveBeenCalledTimes(1);
  });

  it('shows loading indicator when loading', () => {
    const { getByTestId, queryByText } = render(
      <PlatformButton
        title="Test Button"
        onPress={() => {}}
        loading={true}
        testID="button"
      />
    );
    
    expect(queryByText('Test Button')).toBeNull();
    expect(getByTestId('button')).toBeTruthy();
  });

  it('is disabled when disabled prop is true', () => {
    const mockOnPress = jest.fn();
    const { getByText } = render(
      <PlatformButton
        title="Test Button"
        onPress={mockOnPress}
        disabled={true}
      />
    );
    
    fireEvent.press(getByText('Test Button'));
    expect(mockOnPress).not.toHaveBeenCalled();
  });

  it('applies correct styles for different variants', () => {
    const { getByText, rerender } = render(
      <PlatformButton
        title="Primary Button"
        onPress={() => {}}
        variant="primary"
      />
    );
    
    const primaryButton = getByText('Primary Button').parent;
    expect(primaryButton).toHaveStyle({ backgroundColor: expect.any(String) });

    rerender(
      <PlatformButton
        title="Outlined Button"
        onPress={() => {}}
        variant="outlined"
      />
    );
    
    const outlinedButton = getByText('Outlined Button').parent;
    expect(outlinedButton).toHaveStyle({ borderWidth: 2 });
  });
});
```

### Integration Testing

```typescript
// src/__tests__/integration/Authentication.test.tsx
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { store } from '../../store';
import LoginScreen from '../../screens/LoginScreen';
import { AuthService } from '../../services/AuthService';

// Mock the AuthService
jest.mock('../../services/AuthService');
const mockAuthService = AuthService as jest.Mocked<typeof AuthService>;

const MockedApp = ({ children }: { children: React.ReactNode }) => (
  <Provider store={store}>
    {children}
  </Provider>
);

describe('Authentication Flow', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('successfully logs in with valid credentials', async () => {
    const mockTokens = {
      accessToken: 'mock-access-token',
      refreshToken: 'mock-refresh-token',
    };

    mockAuthService.login.mockResolvedValue(mockTokens);

    const { getByPlaceholderText, getByText } = render(
      <MockedApp>
        <LoginScreen />
      </MockedApp>
    );

    const emailInput = getByPlaceholderText('Email');
    const passwordInput = getByPlaceholderText('Password');
    const loginButton = getByText('Sign In');

    fireEvent.changeText(emailInput, 'test@example.com');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.press(loginButton);

    await waitFor(() => {
      expect(mockAuthService.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('shows error message for invalid credentials', async () => {
    mockAuthService.login.mockRejectedValue(new Error('Invalid credentials'));

    const { getByPlaceholderText, getByText, findByText } = render(
      <MockedApp>
        <LoginScreen />
      </MockedApp>
    );

    const emailInput = getByPlaceholderText('Email');
    const passwordInput = getByPlaceholderText('Password');
    const loginButton = getByText('Sign In');

    fireEvent.changeText(emailInput, 'invalid@example.com');
    fireEvent.changeText(passwordInput, 'wrongpassword');
    fireEvent.press(loginButton);

    const errorMessage = await findByText(/invalid credentials/i);
    expect(errorMessage).toBeTruthy();
  });

  it('enables biometric login after initial setup', async () => {
    const mockTokens = {
      accessToken: 'mock-access-token',
      refreshToken: 'mock-refresh-token',
    };

    mockAuthService.loginWithBiometrics.mockResolvedValue(mockTokens);

    const { getByText } = render(
      <MockedApp>
        <LoginScreen />
      </MockedApp>
    );

    const biometricButton = getByText('Use Biometrics');
    fireEvent.press(biometricButton);

    await waitFor(() => {
      expect(mockAuthService.loginWithBiometrics).toHaveBeenCalled();
    });
  });
});
```

### E2E Testing with Detox

```typescript
// e2e/Authentication.e2e.ts
describe('Authentication', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  it('should show login screen on first launch', async () => {
    await expect(element(by.id('login-screen'))).toBeVisible();
    await expect(element(by.id('email-input'))).toBeVisible();
    await expect(element(by.id('password-input'))).toBeVisible();
    await expect(element(by.id('login-button'))).toBeVisible();
  });

  it('should login with valid credentials', async () => {
    await element(by.id('email-input')).typeText('test@example.com');
    await element(by.id('password-input')).typeText('password123');
    await element(by.id('login-button')).tap();

    await waitFor(element(by.id('home-screen')))
      .toBeVisible()
      .withTimeout(5000);
  });

  it('should show error for invalid credentials', async () => {
    await element(by.id('email-input')).typeText('invalid@example.com');
    await element(by.id('password-input')).typeText('wrongpassword');
    await element(by.id('login-button')).tap();

    await waitFor(element(by.text('Invalid credentials')))
      .toBeVisible()
      .withTimeout(3000);
  });

  it('should navigate between tabs', async () => {
    // Login first
    await element(by.id('email-input')).typeText('test@example.com');
    await element(by.id('password-input')).typeText('password123');
    await element(by.id('login-button')).tap();

    await waitFor(element(by.id('home-screen')))
      .toBeVisible()
      .withTimeout(5000);

    // Navigate to profile tab
    await element(by.id('profile-tab')).tap();
    await expect(element(by.id('profile-screen'))).toBeVisible();

    // Navigate back to home tab
    await element(by.id('home-tab')).tap();
    await expect(element(by.id('home-screen'))).toBeVisible();
  });
});
```

## CI/CD Pipeline Configuration

### GitHub Actions Workflow

```yaml
{% raw %}
{% raw %}
# .github/workflows/ci-cd.yml
name: React Native CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  NODE_VERSION: '18'
  JAVA_VERSION: '11'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run TypeScript check
        run: npm run type-check

      - name: Run ESLint
        run: npm run lint

      - name: Run unit tests
        run: npm run test:unit

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3

  android-build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Setup Java
        uses: actions/setup-java@v3
        with:
          distribution: 'temurin'
          java-version: ${{ env.JAVA_VERSION }}

      - name: Setup Android SDK
        uses: android-actions/setup-android@v2

      - name: Install dependencies
        run: npm ci

      - name: Build Android APK
        run: |
          cd android
          ./gradlew assembleRelease

      - name: Upload APK artifact
        uses: actions/upload-artifact@v3
        with:
          name: android-apk
          path: android/app/build/outputs/apk/release/

  ios-build:
    runs-on: macos-latest
    needs: test
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Setup Xcode
        uses: maxim-lobanov/setup-xcode@v1
        with:
          xcode-version: latest-stable

      - name: Install dependencies
        run: npm ci

      - name: Install CocoaPods
        run: |
          cd ios
          pod install

      - name: Build iOS
        run: |
          cd ios
          xcodebuild -workspace CrossPlatformApp.xcworkspace \
                     -scheme CrossPlatformApp \
                     -configuration Release \
                     -destination generic/platform=iOS \
                     -archivePath CrossPlatformApp.xcarchive \
                     archive

      - name: Upload iOS artifact
        uses: actions/upload-artifact@v3
        with:
          name: ios-archive
          path: ios/CrossPlatformApp.xcarchive

  e2e-test:
    runs-on: macos-latest
    needs: [android-build, ios-build]
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Detox CLI
        run: npm install -g detox-cli

      - name: Build Detox
        run: detox build --configuration ios.sim.release

      - name: Run Detox tests
        run: detox test --configuration ios.sim.release --headless

  deploy-staging:
    runs-on: ubuntu-latest
    needs: [android-build, ios-build, e2e-test]
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Deploy to staging
        run: echo "Deploying to staging environment"
        # Add your staging deployment steps here

  deploy-production:
    runs-on: ubuntu-latest
    needs: [android-build, ios-build, e2e-test]
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: echo "Deploying to production environment"
        # Add your production deployment steps here
{% endraw %}
{% endraw %}
```

## Advanced Security Implementation

### Security Best Practices

```typescript
{% raw %}
{% raw %}
// src/security/SecurityManager.ts
import CryptoJS from 'crypto-js';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Keychain } from 'react-native-keychain';

export class SecurityManager {
  private static readonly ENCRYPTION_KEY = 'your-encryption-key';
  private static readonly IV_LENGTH = 16;

  // Data encryption/decryption
  static encrypt(data: string): string {
    const iv = CryptoJS.lib.WordArray.random(this.IV_LENGTH);
    const encrypted = CryptoJS.AES.encrypt(data, this.ENCRYPTION_KEY, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7,
    });
    return iv.concat(encrypted.ciphertext).toString(CryptoJS.enc.Base64);
  }

  static decrypt(encryptedData: string): string {
    const ciphertext = CryptoJS.enc.Base64.parse(encryptedData);
    const iv = CryptoJS.lib.WordArray.create(
      ciphertext.words.slice(0, this.IV_LENGTH / 4)
    );
    const encrypted = CryptoJS.lib.WordArray.create(
      ciphertext.words.slice(this.IV_LENGTH / 4)
    );
    const decrypted = CryptoJS.AES.decrypt(
      { ciphertext: encrypted } as any,
      this.ENCRYPTION_KEY,
      { iv: iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 }
    );
    return decrypted.toString(CryptoJS.enc.Utf8);
  }

  // Secure storage
  static async secureStore(key: string, value: string): Promise<void> {
    try {
      if (Platform.OS === 'ios') {
        await Keychain.setInternetCredentials(key, key, value);
      } else {
        const encryptedValue = this.encrypt(value);
        await AsyncStorage.setItem(key, encryptedValue);
      }
    } catch (error) {
      console.error('Secure storage failed:', error);
      throw error;
    }
  }

  static async secureRetrieve(key: string): Promise<string | null> {
    try {
      if (Platform.OS === 'ios') {
        const credentials = await Keychain.getInternetCredentials(key);
        return credentials ? credentials.password : null;
      } else {
        const encryptedValue = await AsyncStorage.getItem(key);
        return encryptedValue ? this.decrypt(encryptedValue) : null;
      }
    } catch (error) {
      console.error('Secure retrieval failed:', error);
      return null;
    }
  }

  // Certificate pinning
  static validateCertificate(certificate: string): boolean {
    const expectedFingerprint = 'your-expected-certificate-fingerprint';
    const receivedFingerprint = CryptoJS.SHA256(certificate).toString();
    return receivedFingerprint === expectedFingerprint;
  }

  // API request signing
  static signRequest(
    method: string,
    url: string,
    body: string,
    timestamp: number,
    secretKey: string
  ): string {
    const message = `${method}\n${url}\n${body}\n${timestamp}`;
    return CryptoJS.HmacSHA256(message, secretKey).toString();
  }

  // Input sanitization
  static sanitizeInput(input: string): string {
    return input
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+\s*=/gi, '');
  }

  // Rate limiting check
  private static requestCounts = new Map<string, { count: number; resetTime: number }>();

  static checkRateLimit(endpoint: string, limit: number = 100, windowMs: number = 60000): boolean {
    const now = Date.now();
    const key = endpoint;
    const current = this.requestCounts.get(key);

    if (!current || now > current.resetTime) {
      this.requestCounts.set(key, { count: 1, resetTime: now + windowMs });
      return true;
    }

    if (current.count >= limit) {
      return false;
    }

    current.count++;
    return true;
  }
}
{% endraw %}
{% endraw %}
```

## Learning Checklist & Next Steps

### Implementation Verification

- [ ] **Project Setup Complete**
  - [ ] React Native environment configured
  - [ ] TypeScript properly integrated
  - [ ] All dependencies installed and working

- [ ] **Architecture Implementation**
  - [ ] Redux store with RTK configured
  - [ ] Navigation system working
  - [ ] Folder structure organized

- [ ] **Authentication System**
  - [ ] Basic login/logout working
  - [ ] Biometric authentication implemented
  - [ ] Secure token storage

- [ ] **UI/UX Implementation**
  - [ ] Platform-specific components created
  - [ ] Animations and gestures working
  - [ ] Responsive design implemented

- [ ] **API Integration**
  - [ ] RTK Query endpoints created
  - [ ] Error handling implemented
  - [ ] Offline synchronization working

- [ ] **Performance Optimization**
  - [ ] List virtualization implemented
  - [ ] Image optimization working
  - [ ] Memory leaks identified and fixed

- [ ] **Testing Strategy**
  - [ ] Unit tests passing
  - [ ] Integration tests implemented
  - [ ] E2E tests configured

- [ ] **Security Implementation**
  - [ ] Data encryption working
  - [ ] Secure storage implemented
  - [ ] API security measures in place

- [ ] **CI/CD Pipeline**
  - [ ] Automated testing working
  - [ ] Build process configured
  - [ ] Deployment pipeline set up

### Next Steps for Mastery

1. **Advanced Performance**
   - Implement code splitting
   - Add performance monitoring
   - Optimize bundle size

2. **Enhanced Security**
   - Add certificate pinning
   - Implement request signing
   - Add security headers

3. **Advanced Features**
   - Push notifications
   - Background sync
   - Offline-first architecture

4. **Platform-Specific Optimization**
   - iOS-specific features
   - Android-specific features
   - Performance tuning per platform

5. **Production Readiness**
   - Crash reporting
   - Analytics integration
   - Performance monitoring

This implementation provides a comprehensive foundation for enterprise-level React Native development with advanced features, security measures, and performance optimizations.