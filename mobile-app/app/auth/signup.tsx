import { Colors } from '@/constants/Colors';
import { useThemeCustom } from '@/context/ThemeContext';
import { auth } from '@/database/firebase';
import { Image } from 'expo-image';
import { useRouter } from 'expo-router';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { useState } from 'react';
import { Alert, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

export default function SignupScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();
  const { theme } = useThemeCustom();

  const [isLoading, setIsLoading] = useState(false);

  const getAuthErrorMessage = (code?: string) => {
    switch (code) {
      case 'auth/invalid-email':
        return 'Please enter a valid email address.';
      case 'auth/email-already-in-use':
        return 'This email is already registered. Please log in.';
      case 'auth/weak-password':
        return 'Password should be at least 6 characters.';
      case 'auth/network-request-failed':
        return 'Network error. Check your connection.';
      default:
        return 'Sign up failed. Please try again.';
    }
  };

  const signup = async () => {
    if (!email.trim()) {
      Alert.alert('Missing email', 'Please enter your email.');
      return;
    }
    if (!password || password.length < 6) {
      Alert.alert('Weak password', 'Password must be at least 6 characters.');
      return;
    }

    setIsLoading(true);
    try {
      await createUserWithEmailAndPassword(auth, email.trim(), password);
      // Removed alert, directly navigate to onboarding for better UX
      router.replace('/auth/onboarding');
    } catch (e: any) {
      const code: string | undefined = e?.code;
      Alert.alert('Sign up failed', getAuthErrorMessage(code));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: Colors[theme].background }]}>
      <Image source={require('@/assets/images/logo.jpg')} style={{ width: 96, height: 96, borderRadius: 16, alignSelf: 'center', marginBottom: 12 }} />
      <Text style={{ textAlign: 'center', fontSize: 20, fontWeight: '700', marginBottom: 12, color: Colors[theme].text }}>Blood Donation App</Text>
      <View style={[styles.card, { backgroundColor: Colors[theme].cardBackground, borderColor: Colors[theme].border }]}>
        <Text style={[styles.title, { color: Colors[theme].text }]}>Create account</Text>
        <TextInput 
          placeholder="Email" 
          placeholderTextColor={Colors[theme].secondaryText}
          value={email} 
          onChangeText={setEmail} 
          style={[styles.input, { 
            color: Colors[theme].text, 
            backgroundColor: Colors[theme].inputBackground, 
            borderColor: Colors[theme].border 
          }]} 
          autoCapitalize="none" 
        />
        <TextInput 
          placeholder="Password" 
          placeholderTextColor={Colors[theme].secondaryText}
          value={password} 
          onChangeText={setPassword} 
          secureTextEntry 
          style={[styles.input, { 
            color: Colors[theme].text, 
            backgroundColor: Colors[theme].inputBackground, 
            borderColor: Colors[theme].border 
          }]} 
        />
        <TouchableOpacity 
          style={[styles.primaryButton, isLoading && styles.disabledButton]} 
          onPress={signup}
          disabled={isLoading}
        >
          <Text style={styles.primaryText}>{isLoading ? 'Creating account...' : 'Sign Up'}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={{ marginTop: 8, alignItems: 'center' }} onPress={() => router.push('/auth/login')}>
          <Text style={{ color: Colors[theme].linkText }}>Back to login</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, gap: 10, justifyContent: 'center' },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 4, textAlign: 'center' },
  input: {
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 10,
    padding: 12,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 16,
    gap: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
  },
  primaryButton: {
    marginTop: 8,
    backgroundColor: '#E11D48',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  primaryText: { color: '#fff', fontWeight: '600' },
  disabledButton: { opacity: 0.7 },
});


