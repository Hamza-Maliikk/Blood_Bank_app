import { Colors } from '@/constants/Colors';
import { useThemeCustom } from '@/context/ThemeContext';
import { BLOOD_GROUPS, CITIES_PK } from '@/data/pk';
import { listAllUsers } from '@/lib/users';
import { Ionicons } from '@expo/vector-icons';
import { Link } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { FlatList, Image, Linking, StyleSheet, Switch, Text, TextInput, TouchableOpacity, View } from 'react-native';

type Donor = {
  id: string;
  name: string;
  bloodGroup: string;
  city: string;
  gender?: string;
  available?: boolean;
  phone?: string;
};

export default function DonorsScreen() {
  const { theme } = useThemeCustom();
  const isDark = theme === 'dark';
  const [donors, setDonors] = useState<Donor[]>([]);
  const [selectedBloodGroups, setSelectedBloodGroups] = useState<string[]>([]);
  const [cityFilter, setCityFilter] = useState<string | 'all'>('all');
  const [onlyActive, setOnlyActive] = useState<boolean>(true);
  const [query, setQuery] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const profiles = await listAllUsers();
        const mappedDonors = profiles.map((p) => ({
          id: p.uid,
          name: p.name || '(No Name)',
          bloodGroup: p.bloodGroup ?? '-',
          city: p.city ?? '-',
          gender: p.gender,
          available: Boolean(p.available === true || String(p.available) === 'true'), // Normalize to boolean
          phone: p.phone,
        }));
        
        setDonors(mappedDonors);
      } catch (e) {
        console.error('Failed to load donors:', e);
        setDonors([]);
      }
    })();
  }, []);

  const filtered = useMemo(() => {
    return donors.filter((d) => {
      // Only show donors with available: true
      if (onlyActive && d.available !== true) return false;
      if (cityFilter !== 'all' && d.city !== cityFilter) return false;
      if (selectedBloodGroups.length > 0 && !selectedBloodGroups.includes(d.bloodGroup)) return false;
      if (query && !`${d.name} ${d.city} ${d.bloodGroup}`.toLowerCase().includes(query.toLowerCase())) return false;
      return true;
    });
  }, [donors, onlyActive, cityFilter, selectedBloodGroups, query]);

  const toggleBloodGroup = (group: string) => {
    setSelectedBloodGroups((prev) => {
      if (prev.includes(group)) return prev.filter((g) => g !== group);
      return [...prev, group];
    });
  };

  const clearBloodGroups = () => setSelectedBloodGroups([]);

  const isValidPkPhone = (phone?: string) => {
    if (!phone) return false;
    if (!phone.startsWith('+92')) return false;
    const digits = phone.replace(/\D/g, '');
    return digits.length >= 12; // +92 followed by at least 10 digits
  };

  const openDial = (phone?: string) => {
    if (!isValidPkPhone(phone)) return;
    Linking.openURL(`tel:${phone}`);
  };
  const openSms = (phone?: string) => {
    if (!isValidPkPhone(phone)) return;
    Linking.openURL(`sms:${phone}`);
  };
  const openWhatsApp = (phone?: string) => {
    if (!isValidPkPhone(phone)) return;
    const digits = (phone ?? '').replace(/\D/g, '');
    const wa = `https://wa.me/${digits}`;
    Linking.openURL(wa);
  };

  return (
    <View style={[styles.container, { backgroundColor: Colors[theme].background }]}>
      <Text style={[styles.title, { color: isDark ? '#fff' : Colors[theme].text }]}>Donors</Text>
      <View style={styles.filters}>
        <TextInput placeholder="Search name/city/group" placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'} style={[styles.search, { color: isDark ? '#fff' : '#111827', borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} value={query} onChangeText={setQuery} />
        <FlatList
          data={[{label:'All',value:'all'}, ...BLOOD_GROUPS.map((g) => ({ label: g, value: g }))]}
          keyExtractor={(i) => `${i.value}`}
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={{ gap: 8 }}
          renderItem={({ item }) => (
            item.value === 'all' ? (
              <TouchableOpacity onPress={clearBloodGroups} style={[styles.chip, { borderColor: isDark ? '#374151' : '#e5e7eb' }]}>
                <Text style={[styles.chipText, { color: isDark ? '#D1D5DB' : '#111827' }]}>All</Text>
              </TouchableOpacity>
            ) : (
              <TouchableOpacity onPress={() => toggleBloodGroup(item.value)} style={[styles.chip, { borderColor: isDark ? '#374151' : '#e5e7eb' }, selectedBloodGroups.includes(item.value) && styles.chipActive ]}>
                <Text style={[styles.chipText, { color: isDark ? '#D1D5DB' : '#111827' }, selectedBloodGroups.includes(item.value) && styles.chipTextActive]}>{item.label}</Text>
              </TouchableOpacity>
            )
          )}
        />
        <FlatList
          data={[{label:'All',value:'all'}, ...CITIES_PK.map((c) => ({ label: c, value: c }))]}
          keyExtractor={(i) => `${i.value}`}
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={{ gap: 8, marginTop: 8 }}
          renderItem={({ item }) => (
            <TouchableOpacity onPress={() => setCityFilter(item.value as any)} style={[styles.chip, { borderColor: isDark ? '#374151' : '#e5e7eb' }, cityFilter===item.value && styles.chipActive]}>
              <Text style={[styles.chipText, { color: isDark ? '#D1D5DB' : '#111827' }, cityFilter===item.value && styles.chipTextActive]}>{item.label}</Text>
            </TouchableOpacity>
          )}
        />
        <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginTop: 8 }}>
          <View style={{ flex: 1 }}>
            <Text style={{ fontWeight: '600', color: isDark ? '#fff' : '#111827', fontSize: 16 }}>Active only</Text>
            <Text style={{ fontSize: 12, color: isDark ? '#9CA3AF' : '#6B7280', marginTop: 2 }}>
              {onlyActive ? `Showing ${filtered.length} available donors` : `Showing ${filtered.length} donors`}
            </Text>
            <Text style={{ fontSize: 10, color: isDark ? '#6B7280' : '#9CA3AF', marginTop: 1 }}>
              Filter: {onlyActive ? 'ON' : 'OFF'} | Total: {donors.length}
            </Text>
          </View>
          <Switch 
            value={onlyActive} 
            onValueChange={setOnlyActive}
            trackColor={{ false: '#767577', true: '#E11D48' }}
            thumbColor={onlyActive ? '#fff' : '#f4f3f4'}
          />
        </View>
      </View>
      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ gap: 8, paddingVertical: 8 }}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
              <Image source={require('@/assets/images/profile.png')} style={{ width: 36, height: 36, borderRadius: 18 }} />
              <View style={{ flex: 1 }}>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                  <Text style={[styles.name, { color: isDark ? '#fff' : '#111827' }]}>{item.name}</Text>
                  {item.available && (
                    <View style={styles.availableIndicator}>
                      <Text style={styles.availableText}>Available</Text>
                    </View>
                  )}
                </View>
                <Text style={[styles.meta, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>{item.bloodGroup} • {item.city}</Text>
              </View>
            </View>
            <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
              <Link href={{ pathname: '/profile/[uid]', params: { uid: item.id } }} asChild>
                <TouchableOpacity style={[styles.outlineButton, { flex: 1 }]}> 
                  <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                    <Ionicons name="person" size={16} color="#E11D48" />
                    <Text style={styles.outlineText}>View Profile</Text>
                  </View>
                </TouchableOpacity>
              </Link>
              <Link href={{ pathname: '/(tabs)/request', params: { requestedTo: item.id } }} asChild>
                <TouchableOpacity style={[styles.requestButton, { flex: 1 }]}> 
                  <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                    <Ionicons name="medkit" size={16} color="#fff" />
                    <Text style={styles.requestText}>Request</Text>
                  </View>
                </TouchableOpacity>
              </Link>
            </View>
            <View style={{ flexDirection: 'row', gap: 8, marginTop: 8 }}>
              <TouchableOpacity style={[styles.contactButton, { flex: 1 }]} onPress={() => openDial(item.phone)}>
                <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                  <Ionicons name="call" size={16} color="#fff" />
                  <Text style={styles.contactText}>Call</Text>
                </View>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.contactButton, { flex: 1 }]} onPress={() => openSms(item.phone)}>
                <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                  <Ionicons name="chatbubbles" size={16} color="#fff" />
                  <Text style={styles.contactText}>SMS</Text>
                </View>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.contactButton, { flex: 1 }]} onPress={() => openWhatsApp(item.phone)}>
                <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                  <Ionicons name="logo-whatsapp" size={16} color="#fff" />
                  <Text style={styles.contactText}>WhatsApp</Text>
                </View>
              </TouchableOpacity>
            </View>
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>No donors found. Try seeding or updating your profile to Available.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 24, fontWeight: '700' },
  filters: { marginTop: 8, marginBottom: 8 },
  search: { borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 10, padding: 10, marginBottom: 8 },
  chip: { paddingVertical: 6, paddingHorizontal: 10, borderRadius: 999, borderWidth: 1, borderColor: '#e5e7eb' },
  chipActive: { backgroundColor: '#111827' },
  chipText: { color: '#111827', fontWeight: '600' },
  chipTextActive: { color: '#fff' },
  card: {
    borderWidth: 1,
    borderColor: '#eee',
    borderRadius: 12,
    padding: 12,
    gap: 4,
  },
  name: { fontSize: 16, fontWeight: '600' },
  meta: { fontSize: 14, opacity: 0.7 },
  contactButton: {
    backgroundColor: '#E11D48',
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
  },
  contactText: { color: '#fff', fontWeight: '600' },
  requestButton: {
    marginTop: 8,
    backgroundColor: '#111827',
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
  },
  requestText: { color: '#fff', fontWeight: '600' },
  outlineButton: { borderColor: '#E11D48', borderWidth: 1, paddingVertical: 10, borderRadius: 10, alignItems: 'center' },
  outlineText: { color: '#E11D48', fontWeight: '600' },
  availableIndicator: { 
    backgroundColor: '#10B981', 
    paddingHorizontal: 6, 
    paddingVertical: 2, 
    borderRadius: 8 
  },
  availableText: { 
    color: '#fff', 
    fontSize: 10, 
    fontWeight: '600' 
  },
  empty: { textAlign: 'center', marginTop: 24, opacity: 0.6 },
});


