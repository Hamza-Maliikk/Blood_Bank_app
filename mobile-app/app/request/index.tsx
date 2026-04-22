import { Colors } from '@/constants/Colors';
import { auth, database } from '@/database/firebase';
import { useColorScheme } from '@/hooks/useColorScheme';
import { acceptRequest, rejectRequest } from '@/lib/requests';
import { BloodRequest } from '@/lib/types';
import { Link } from 'expo-router';
import { get, ref } from 'firebase/database';
import React, { useEffect, useState } from 'react';
import { Alert, FlatList, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function RequestListScreen() {
  const colorScheme = useColorScheme() ?? 'light';
  const isDark = colorScheme === 'dark';
  const [requests, setRequests] = useState<BloodRequest[]>([]);
  const [tab, setTab] = useState<'to_me' | 'all'>('to_me');

  useEffect(() => {
    (async () => {
      const snap = await get(ref(database, 'requests'));
      if (snap.exists()) {
        const list = Object.values(snap.val()) as BloodRequest[];
        setRequests(list.sort((a, b) => b.createdAt - a.createdAt));
      } else {
        setRequests([]);
      }
    })();
  }, []);

  const uid = auth.currentUser?.uid;
  const filtered = requests.filter((r) => {
    if (tab === 'to_me') {
      return r.status !== 'fulfilled' && r.status !== 'cancelled' && (r.requestedTo === uid || (!r.requestedTo && r.status === 'open'));
    }
    return true;
  });

  const onAccept = async (id: string) => {
    try {
      await acceptRequest(id);
      Alert.alert('Accepted', 'You have accepted this request.');
    } catch (e: any) {
      Alert.alert('Failed', e?.message ?? 'Could not accept.');
    }
  };
  const onReject = async (id: string) => {
    try {
      await rejectRequest(id);
      Alert.alert('Rejected', 'You have rejected this request.');
    } catch (e: any) {
      Alert.alert('Failed', e?.message ?? 'Could not reject.');
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: Colors[colorScheme].background }] }>
      <Text style={[styles.title, { color: isDark ? '#fff' : Colors[colorScheme].text }]}>Patient Requests</Text>
      <View style={styles.tabs}>
        {(['to_me','all'] as const).map((k) => (
          <TouchableOpacity key={k} style={[styles.tab, tab===k && styles.tabActive]} onPress={() => setTab(k)}>
            <Text style={[styles.tabText, tab===k && styles.tabTextActive]}>{k === 'to_me' ? 'REQUEST TO ME' : 'ALL REQUESTS'}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <FlatList
        data={filtered}
        keyExtractor={(i) => i.id}
        contentContainerStyle={{ gap: 8, paddingVertical: 8 }}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Link href={`/request/${item.id}`} asChild>
              <TouchableOpacity>
                <Text style={[styles.name, { color: isDark ? '#fff' : '#111827' }]}>{item.patientName} • {item.requiredBloodGroup}</Text>
                <Text style={[styles.meta, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>{item.city} • {item.hospital ?? '—'}</Text>
                <Text style={[styles.meta, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>Status: {item.status}</Text>
              </TouchableOpacity>
            </Link>
            <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
              {item.status === 'open' && (
                <TouchableOpacity style={styles.primaryButton} onPress={() => onAccept(item.id)}>
                  <Text style={styles.primaryText}>Accept</Text>
                </TouchableOpacity>
              )}
              {item.status === 'pending' && item.requestedTo === uid && (
                <>
                  <TouchableOpacity style={styles.primaryButton} onPress={() => onAccept(item.id)}>
                    <Text style={styles.primaryText}>Accept</Text>
                  </TouchableOpacity>
                  <TouchableOpacity style={styles.secondaryButton} onPress={() => onReject(item.id)}>
                    <Text style={styles.secondaryText}>Reject</Text>
                  </TouchableOpacity>
                </>
              )}
              <Link href={`/donations/add`} asChild>
                <TouchableOpacity style={styles.darkButton}>
                  <Text style={styles.darkText}>Donate Amount</Text>
                </TouchableOpacity>
              </Link>
            </View>
          </View>
        )}
        ListEmptyComponent={<Text style={{ textAlign: 'center', marginTop: 24, opacity: 0.6, color: isDark ? '#D1D5DB' : '#6B7280' }}>No requests</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 24, fontWeight: '700' },
  tabs: { flexDirection: 'row', gap: 8, marginTop: 8, marginBottom: 8 },
  tab: { paddingVertical: 8, paddingHorizontal: 10, borderRadius: 10, borderWidth: 1, borderColor: '#e5e7eb' },
  tabActive: { backgroundColor: '#111827' },
  tabText: { color: '#111827', fontWeight: '600' },
  tabTextActive: { color: '#fff' },
  card: { borderWidth: 1, borderColor: '#eee', borderRadius: 12, padding: 12, gap: 4 },
  name: { fontSize: 16, fontWeight: '600' },
  meta: { fontSize: 14, opacity: 0.7 },
  primaryButton: { backgroundColor: '#E11D48', paddingVertical: 10, paddingHorizontal: 12, borderRadius: 10 },
  primaryText: { color: '#fff', fontWeight: '600' },
  secondaryButton: { borderColor: '#E11D48', borderWidth: 1, paddingVertical: 10, paddingHorizontal: 12, borderRadius: 10 },
  secondaryText: { color: '#E11D48', fontWeight: '600' },
  darkButton: { backgroundColor: '#111827', paddingVertical: 10, paddingHorizontal: 12, borderRadius: 10 },
  darkText: { color: '#fff', fontWeight: '600' },
});


