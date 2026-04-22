import SelectModal from '@/components/SelectModal';
import { Colors } from '@/constants/Colors';
import { BLOOD_GROUPS, CITIES_PK, GENDERS } from '@/data/pk';
import { auth } from '@/database/firebase';
import { useColorScheme } from '@/hooks/useColorScheme';
import { saveUserProfile } from '@/lib/users';
import { Image } from 'expo-image';
import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Switch, Text, TextInput, TouchableOpacity, View } from 'react-native';

export default function OnboardingScreen() {
  const router = useRouter();
  const colorScheme = useColorScheme() ?? 'light';
  const isDark = colorScheme === 'dark';
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('+92');
  const [gender, setGender] = useState('');
  const [bloodGroup, setBloodGroup] = useState('');
  const [city, setCity] = useState('');
  const [mode, setMode] = useState<'donor' | 'patient'>('patient');
  const [available, setAvailable] = useState(true);
  const [openPicker, setOpenPicker] = useState<null | 'gender' | 'city' | 'blood'>(null);

  const normalizePhone = (value: string) => {
    if (!value.startsWith('+92')) return '+92';
    const digits = value.replace(/[^\d+]/g, '');
    return digits.slice(0, 13);
  };

  const onSave = async () => {
    if (!name || !bloodGroup || !city) {
      Alert.alert('Missing fields', 'Please fill name, blood group and city.');
      return;
    }
    try {
      await saveUserProfile({ name, email, phone, gender, bloodGroup, city, mode, available: mode === 'donor' ? available : undefined });
      Alert.alert('Saved', 'Welcome!');
      router.replace('/(tabs)/home');
    } catch (e: any) {
      const message = e?.message ?? 'Could not save profile. Are you logged in?';
      Alert.alert('Save failed', message);
    }
  };

  useEffect(() => {
    const currentEmail = auth.currentUser?.email ?? '';
    if (currentEmail) setEmail(currentEmail);
  }, []);

  return (
    <ScrollView 
      style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}
      contentContainerStyle={styles.scrollContent}
      showsVerticalScrollIndicator={false}
    >
      <Image source={require('@/assets/images/logo.jpg')} style={{ width: 96, height: 96, borderRadius: 16, alignSelf: 'center', marginBottom: 12 }} />
      <Text style={{ textAlign: 'center', fontSize: 20, fontWeight: '700', marginBottom: 12, color: Colors[colorScheme].text }}>Blood Donation App</Text>
      <View style={[styles.card, { backgroundColor: Colors[colorScheme].cardBackground, borderColor: Colors[colorScheme].border }]}>
        <Text style={[styles.title, { color: Colors[colorScheme].text }]}>Complete Profile</Text>
        
        <TextInput 
          placeholder="Full Name" 
          placeholderTextColor={Colors[colorScheme].secondaryText}
          style={[styles.input, { color: Colors[colorScheme].text, backgroundColor: Colors[colorScheme].inputBackground, borderColor: Colors[colorScheme].border }]} 
          value={name} 
          onChangeText={setName} 
        />
        
        <TextInput 
          placeholder="Email" 
          placeholderTextColor={Colors[colorScheme].disabledText}
          style={[styles.input, styles.inputDisabled, { color: Colors[colorScheme].disabledText, backgroundColor: Colors[colorScheme].inputBackground, borderColor: Colors[colorScheme].border }]} 
          value={email} 
          onChangeText={setEmail} 
          editable={false} 
        />
        
        <TextInput 
          placeholder="Phone (+92...)" 
          placeholderTextColor={Colors[colorScheme].secondaryText}
          style={[styles.input, { color: Colors[colorScheme].text, backgroundColor: Colors[colorScheme].inputBackground, borderColor: Colors[colorScheme].border }]} 
          value={phone} 
          onChangeText={(v)=>setPhone(normalizePhone(v))} 
          keyboardType="phone-pad" 
        />
        
        <TouchableOpacity style={[styles.input, { backgroundColor: Colors[colorScheme].inputBackground, borderColor: Colors[colorScheme].border }]} onPress={() => setOpenPicker('gender')}>
          <Text style={{ color: gender ? Colors[colorScheme].text : Colors[colorScheme].secondaryText }}>{gender || 'Gender'}</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.input, { backgroundColor: Colors[colorScheme].inputBackground, borderColor: Colors[colorScheme].border }]} onPress={() => setOpenPicker('blood')}>
          <Text style={{ color: bloodGroup ? Colors[colorScheme].text : Colors[colorScheme].secondaryText }}>{bloodGroup || 'Blood Group'}</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.input, { backgroundColor: Colors[colorScheme].inputBackground, borderColor: Colors[colorScheme].border }]} onPress={() => setOpenPicker('city')}>
          <Text style={{ color: city ? Colors[colorScheme].text : Colors[colorScheme].secondaryText }}>{city || 'City'}</Text>
        </TouchableOpacity>

        {/* Mode Selection */}
        <View style={{ marginVertical: 16 }}>
          <Text style={{ fontWeight: '600', marginBottom: 8, color: Colors[colorScheme].text }}>Select Mode</Text>
          <Text style={{ fontSize: 12, color: Colors[colorScheme].secondaryText, marginBottom: 12 }}>
            Choose your primary role in the app. You can change this later in your profile.
          </Text>
          <View style={{ flexDirection: 'row', gap: 12 }}>
            <TouchableOpacity 
              style={[
                styles.modeOption, 
                { 
                  backgroundColor: mode === 'patient' ? Colors[colorScheme].linkText : Colors[colorScheme].inputBackground,
                  borderColor: mode === 'patient' ? Colors[colorScheme].linkText : Colors[colorScheme].border
                }
              ]} 
              onPress={() => setMode('patient')}
            >
              <Text style={{ color: mode === 'patient' ? '#fff' : Colors[colorScheme].text, fontWeight: '600' }}>Patient</Text>
              <Text style={{ fontSize: 11, color: mode === 'patient' ? 'rgba(255,255,255,0.8)' : Colors[colorScheme].secondaryText, textAlign: 'center', marginTop: 4 }}>
                Request blood, find donors
              </Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[
                styles.modeOption, 
                { 
                  backgroundColor: mode === 'donor' ? '#10B981' : Colors[colorScheme].inputBackground,
                  borderColor: mode === 'donor' ? '#10B981' : Colors[colorScheme].border
                }
              ]} 
              onPress={() => setMode('donor')}
            >
              <Text style={{ color: mode === 'donor' ? '#fff' : Colors[colorScheme].text, fontWeight: '600' }}>Donor</Text>
              <Text style={{ fontSize: 11, color: mode === 'donor' ? 'rgba(255,255,255,0.8)' : Colors[colorScheme].secondaryText, textAlign: 'center', marginTop: 4 }}>
                Donate blood, help patients
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Availability Toggle - Only for Donors */}
        {mode === 'donor' && (
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
            <View>
              <Text style={{ fontWeight: '600', color: Colors[colorScheme].text }}>Available as Donor</Text>
              <Text style={{ fontSize: 12, color: Colors[colorScheme].secondaryText }}>Others can find and contact you</Text>
            </View>
            <Switch value={available} onValueChange={setAvailable} />
          </View>
        )}
        
        <TouchableOpacity style={styles.primaryButton} onPress={onSave}>
          <Text style={styles.primaryText}>Save & Continue</Text>
        </TouchableOpacity>
      </View>

      <SelectModal visible={openPicker==='gender'} title="Select Gender" options={GENDERS} onClose={()=>setOpenPicker(null)} onSelect={(v)=>{setGender(v); setOpenPicker(null);}} />
      <SelectModal visible={openPicker==='blood'} title="Select Blood Group" options={BLOOD_GROUPS} onClose={()=>setOpenPicker(null)} onSelect={(v)=>{setBloodGroup(v); setOpenPicker(null);}} />
      <SelectModal visible={openPicker==='city'} title="Select City" options={CITIES_PK} onClose={()=>setOpenPicker(null)} onSelect={(v)=>{setCity(v); setOpenPicker(null);}} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, gap: 10 },
  scrollContent: { paddingBottom: 20, flexGrow: 1, justifyContent: 'center' },
  title: { fontSize: 20, fontWeight: '700', marginBottom: 4, textAlign: 'center' },
  input: {
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 10,
    padding: 12,
  },
  inputDisabled: {
    backgroundColor: '#f3f4f6',
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
  modeOption: {
    flex: 1,
    borderWidth: 2,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    minHeight: 70,
    justifyContent: 'center',
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


