import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import { listMyRequests } from '@/lib/requests';
import { getUserProfile } from '@/lib/users';
import React, { useEffect, useState } from 'react';
import { FlatList, Image, StyleSheet, Text, View } from 'react-native';

type MyRequest = {
  id: string;
  patientName: string;
  requiredBloodGroup: string;
  city: string;
  status: string;
};

export default function PatientProfileScreen() {
  const colorScheme = useColorScheme() ?? 'light';
  const isDark = colorScheme === 'dark';
  const [name, setName] = useState('');
  const [group, setGroup] = useState<string | undefined>('');
  const [city, setCity] = useState<string | undefined>('');
  const [requests, setRequests] = useState<MyRequest[]>([]);

  useEffect(() => {
    (async () => {
      const p = await getUserProfile();
      if (p) {
        setName(p.name ?? '');
        setGroup(p.bloodGroup);
        setCity(p.city);
      }
      const list = await listMyRequests();
      setRequests(list.map(r => ({ id: r.id, patientName: r.patientName, requiredBloodGroup: r.requiredBloodGroup, city: r.city, status: r.status })));
    })();
  }, []);

  return (
    <View style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}>
      <View style={{ alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <Image source={require('@/assets/images/profile.png')} style={{ width: 72, height: 72, borderRadius: 36 }} />
        <Text style={[styles.title, { color: isDark ? '#fff' : Colors[colorScheme].text }]}>{name || 'Patient'}</Text>
        <Text style={{ color: isDark ? '#D1D5DB' : '#6B7280' }}>{group ?? '—'} • {city ?? '—'}</Text>
      </View>

      <Text style={[styles.sectionTitle, { color: isDark ? '#fff' : Colors[colorScheme].text }]}>My Requests</Text>
      <FlatList
        data={requests}
        keyExtractor={(i) => i.id}
        contentContainerStyle={{ gap: 8, paddingVertical: 8 }}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={[styles.name, { color: isDark ? '#fff' : '#111827' }]}>{item.patientName} • {item.requiredBloodGroup}</Text>
            <Text style={[styles.meta, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>{item.city} • {item.status}</Text>
          </View>
        )}
        ListEmptyComponent={<Text style={{ textAlign: 'center', marginTop: 24, opacity: 0.6, color: isDark ? '#D1D5DB' : '#6B7280' }}>No requests yet.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 24, fontWeight: '700' },
  sectionTitle: { marginTop: 4, fontSize: 18, fontWeight: '700' },
  card: { borderWidth: 1, borderColor: '#eee', borderRadius: 12, padding: 12, gap: 4 },
  name: { fontSize: 16, fontWeight: '600' },
  meta: { fontSize: 14, opacity: 0.7 },
});




