import { Colors } from '@/constants/Colors';
import { useMode } from '@/context/ModeContext';
import { useThemeCustom } from '@/context/ThemeContext';
import { listMyDonations } from '@/lib/donations';
import { listMyRequests, listRequests } from '@/lib/requests';
import { useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { FlatList, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

type HistoryItem = {
  id: string;
  date: number;
  patient?: string;
  hospital?: string;
  status: 'Donated' | 'Pending' | 'Accepted' | 'Rejected' | 'Cancelled' | 'Open';
};

export default function HistoryScreen() {
  const { theme } = useThemeCustom();
  const isDark = theme === 'dark';
  const { mode } = useMode();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'all' | 'pending' | 'rejected' | 'accepted' | 'fulfilled' | 'cancelled'>('all');
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    (async () => {
      if (mode === 'patient') {
        // Patient view: requests I posted by status
        const myRequests = await listMyRequests();
        const items: HistoryItem[] = myRequests.map((r) => ({
          id: `r_${r.id}`,
          date: r.createdAt,
          patient: r.patientName,
          hospital: r.hospital,
          status: ((r.status === 'open' && 'Open') || (r.status === 'cancelled' && 'Cancelled') || (r.status === 'fulfilled' && 'Donated') || 'Pending') as HistoryItem['status'],
        })).sort((a, b) => b.date - a.date);
        setHistory(items);
      } else {
        // Donor view: blood donations I recorded and accepted requests where I am requestedTo
        const [donations, acceptedRequests] = await Promise.all([
          listMyDonations(),
          listRequests({ toMeOnly: true, status: ['accepted', 'fulfilled'] }),
        ]);
        const items: HistoryItem[] = [
          ...donations.map((d) => ({
            id: `d_${d.id}`,
            date: d.date,
            status: (d.status === 'donated' ? 'Donated' : 'Pending') as HistoryItem['status'],
          })),
          ...acceptedRequests.map((r) => ({
            id: `r_${r.id}`,
            date: r.createdAt,
            patient: r.patientName,
            hospital: r.hospital,
            status: ((r.status === 'fulfilled' && 'Donated') || 'Accepted') as HistoryItem['status'],
          })),
        ].sort((a, b) => b.date - a.date);
        setHistory(items);
      }
    })();
  }, [mode]);

  const filteredHistory = activeTab === 'all' ? history : history.filter((item) => {
    const statusMap: Record<string, string[]> = {
      pending: ['Pending'],
      rejected: ['Rejected'],
      accepted: ['Accepted'],
      fulfilled: ['Donated'],
      cancelled: ['Cancelled'],
    };
    return statusMap[activeTab]?.includes(item.status) ?? false;
  });

  const handleItemPress = (item: HistoryItem) => {
    // Extract request ID from the item ID (remove prefix like 'r_' or 'd_')
    const requestId = item.id.startsWith('r_') ? item.id.substring(2) : item.id;
    router.push(`/request/${requestId}`);
  };

  return (
    <View style={[styles.container, { backgroundColor: Colors[theme].background }]}>
      <Text style={[styles.title, { color: isDark ? '#fff' : Colors[theme].text }]}>
        Request History
      </Text>
      
      <View style={styles.tabs}>
        {(['all', 'pending', 'accepted', 'fulfilled', 'cancelled'] as const).map((tab) => (
          <TouchableOpacity
            key={tab}
            style={[styles.tab, activeTab === tab && styles.tabActive]}
            onPress={() => setActiveTab(tab)}
          >
            <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <FlatList
        data={filteredHistory}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ gap: 8, paddingVertical: 8 }}
        renderItem={({ item }) => (
          <TouchableOpacity 
            style={[styles.card, { borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]}
            onPress={() => handleItemPress(item)}
            activeOpacity={0.7}
          >
            <Text style={[styles.meta, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>{new Date(item.date).toLocaleDateString()}</Text>
            <Text style={[styles.name, { color: isDark ? '#fff' : '#111827' }]}>{item.patient ?? 'N/A'}</Text>
            <Text style={[styles.meta, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>{item.hospital ?? '—'} • {item.status}</Text>
            <Text style={[styles.clickHint, { color: isDark ? '#9CA3AF' : '#9CA3AF' }]}>Tap to view details</Text>
          </TouchableOpacity>
        )}
        ListEmptyComponent={<Text style={[styles.empty, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>No history yet.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 16 },
  tabs: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 16 },
  tab: { paddingVertical: 8, paddingHorizontal: 12, borderRadius: 20, backgroundColor: '#F3F4F6' },
  tabActive: { backgroundColor: '#E11D48' },
  tabText: { fontWeight: '600', color: '#6B7280', fontSize: 12 },
  tabTextActive: { color: '#fff' },
  card: {
    borderWidth: 1,
    borderColor: '#eee',
    borderRadius: 12,
    padding: 12,
    gap: 4,
  },
  name: { fontSize: 16, fontWeight: '600' },
  meta: { fontSize: 14, opacity: 0.7 },
  clickHint: { fontSize: 12, opacity: 0.6, fontStyle: 'italic', marginTop: 4 },
  empty: { textAlign: 'center', marginTop: 24, opacity: 0.6 },
});


