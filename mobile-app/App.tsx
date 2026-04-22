import * as React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { PaperProvider, DefaultTheme } from 'react-native-paper';
import Login from './components/Login';
import UserProfile from './components/UserProfile';
import Signup from './components/Signup';
import Dashboard from './components/Dashboard';
import SplashScreen from './components/SplashScreen';
import ForgotPassword from './components/ForgotPassword';
import Feedback from './components/Feedback';
import SmsSend from './components/SmsSend';
import FindBloodDonor from './components/FindBloodDonor';
import Setting from './components/Setting';
import Whatsapp from './components/Whatsapp';
import { RootStackParamList } from 'types';


const Stack = createStackNavigator<RootStackParamList>();
// 🔴 Custom Red Theme
const redTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#b22222', 
    accent: '#ff4d4d',  
    background: '#fff', 
    text: '#000',       
    placeholder: '#888',
    surface: '#fff',    
    onSurface: '#000',  
    disabled: '#ccc',
    error: '#f44336',
  },
};


function AppStack() {
  return (
    <Stack.Navigator
      initialRouteName="SplashScreen"
      screenOptions={{
        headerTitleAlign: 'center',
        headerStyle: {
          backgroundColor: redTheme.colors.primary,
          height: 70
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}>
      <Stack.Screen 
        name="SplashScreen" 
        component={SplashScreen} 
        options={{headerShown: false}}  
      />       
      
      <Stack.Screen 
        name="Signup" 
        component={Signup} 
        options={{
          title: 'Signup',
          headerLeft: () => null,
          headerShown: false
        }}
      />       
      <Stack.Screen 
        name="Login" 
        component={Login} 
        options={{
          title: 'Login',
          headerLeft: () => null,
          headerShown: false
        }}
      />
      <Stack.Screen 
        name="Setting" 
        component={Setting} 
        options={{ title: 'Setting' }}
      />

      <Stack.Screen 
        name="FindBloodDonor" 
        component={FindBloodDonor} 
        options={{ title: 'Find Blood Donor' }}
      />

      <Stack.Screen 
        name="SmsSend" 
        component={SmsSend} 
        options={{ title: 'Sms Send' }}
      />

      <Stack.Screen 
        name="Whatsapp" 
        component={Whatsapp} 
        options={{ title: 'Whatsapp' }}
      /> 

      <Stack.Screen 
        name="Feedback" 
        component={Feedback} 
        options={{ title: 'Feed Back' }}
      />

      <Stack.Screen 
        name="UserProfile" 
        component={UserProfile} 
        options={{ title: 'User Profile' }}
      />
      <Stack.Screen 
        name="ForgotPassword" 
        component={ForgotPassword} 
        options={{ title: 'Change Password' }}
      />       

      <Stack.Screen 
        name="Dashboard" 
        component={Dashboard} 
        options={{
          title: 'Dashboard',
          headerLeft: () => null,
          headerShown: true
        }}
      />
    </Stack.Navigator>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <PaperProvider theme={redTheme}>
        <AppStack />
      </PaperProvider>
    </NavigationContainer>
  );
}