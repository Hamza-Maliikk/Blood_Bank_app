import { Colors } from '@/constants/Colors';
import { auth } from '@/database/firebase';
import { useColorScheme } from '@/hooks/useColorScheme';
import { Image } from 'expo-image';
import { sendPasswordResetEmail } from 'firebase/auth';
import { useState } from 'react';
import { Alert, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

export default function ResetScreen() {
  const [email, setEmail] = useState('');
  const colorScheme = useColorScheme() ?? 'light';

  const reset = async () => {
    try {
      await sendPasswordResetEmail(auth, email.trim());
      Alert.alert('Reset email sent', 'Check your inbox for reset instructions.');
    } catch (e: any) {
      Alert.alert('Reset failed', e?.message ?? 'Try again');
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}>
      <Image source={require('@/assets/images/logo.jpg')} style={{ width: 96, height: 96, borderRadius: 16, alignSelf: 'center', marginBottom: 12 }} />
      <Text style={{ textAlign: 'center', fontSize: 20, fontWeight: '700', marginBottom: 12, color: Colors[colorScheme].text }}>Blood Donation App</Text>
      <View style={[styles.card, { backgroundColor: Colors[colorScheme].cardBackground, borderColor: Colors[colorScheme].border }]}>
        <Text style={[styles.title, { color: Colors[colorScheme].text }]}>Reset Password</Text>
        <TextInput 
          placeholder="Email" 
          placeholderTextColor={Colors[colorScheme].secondaryText}
          value={email} 
          onChangeText={setEmail} 
          style={[styles.input, { 
            color: Colors[colorScheme].text, 
            backgroundColor: Colors[colorScheme].inputBackground, 
            borderColor: Colors[colorScheme].border 
          }]} 
          autoCapitalize="none" 
        />
        <TouchableOpacity style={styles.primaryButton} onPress={reset}>
          <Text style={styles.primaryText}>Send Reset Email</Text>
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
});


