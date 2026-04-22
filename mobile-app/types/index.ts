import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';

// Define the type for the stack navigator params
export type RootStackParamList = {
  SplashScreen: undefined;
  Signup: undefined;
  Login: undefined;
  Setting: undefined;
  FindBloodDonor: undefined;
  SmsSend: undefined;
  Feedback: undefined;
  UserProfile: undefined;
  ForgotPassword: undefined;
  Dashboard: undefined;
  Whatsapp: undefined;
};

// Define types for navigation props
export type ScreenNavigationProp<T extends keyof RootStackParamList> = 
  StackNavigationProp<RootStackParamList, T>;

export type ScreenRouteProp<T extends keyof RootStackParamList> = 
  RouteProp<RootStackParamList, T>;

export type ScreenProps<T extends keyof RootStackParamList> = {
  navigation: ScreenNavigationProp<T>;
  route: ScreenRouteProp<T>;
};