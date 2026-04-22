import { Colors } from '@/constants/Colors';
import { useMode } from '@/context/ModeContext';
import { useThemeCustom } from '@/context/ThemeContext';
import { acceptRequest, listRequests } from '@/lib/requests';
import { Ionicons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import { useRouter } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { Alert, FlatList, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

export default function HomeScreen() {
  const { theme } = useThemeCustom();
  const isDark = theme === 'dark';
  const router = useRouter();
  const { mode } = useMode();
  const [searchCity, setSearchCity] = useState('');
  const [searchGroup, setSearchGroup] = useState('');
  const [urgent, setUrgent] = useState<any[]>([]);
  const [acceptingRequest, setAcceptingRequest] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const reqs = await listRequests({ status: ['open', 'pending'], urgentOnly: true });
      setUrgent(reqs.slice(0, 10));
    })();
  }, []);

  const filteredUrgent = useMemo(() => {
    return urgent.filter((r) =>
      (!searchCity || r.city?.toLowerCase().includes(searchCity.toLowerCase())) &&
      (!searchGroup || r.requiredBloodGroup === searchGroup)
    );
  }, [urgent, searchCity, searchGroup]);

  const handleAcceptRequest = async (requestId: string) => {
    if (mode !== 'donor') {
      Alert.alert('Access Denied', 'Only donors can accept requests. Switch to Donor mode in your profile.');
      return;
    }
    
    try {
      setAcceptingRequest(requestId);
      await acceptRequest(requestId);
      Alert.alert('Success', 'Request accepted! The patient will be notified.');
      // Refresh urgent requests - remove accepted request from list
      const reqs = await listRequests({ status: ['open', 'pending'], urgentOnly: true });
      setUrgent(reqs.slice(0, 10));
    } catch (e: any) {
      Alert.alert('Error', e?.message ?? 'Failed to accept request');
    } finally {
      setAcceptingRequest(null);
    }
  };

  const formatTimeAgo = (timestamp: number) => {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <View style={[styles.container, { paddingTop: 12, backgroundColor: Colors[theme as 'light' | 'dark'].background }]}> 
      <View style={styles.headerBranding}>
        <Image source={require('@/assets/images/logo.jpg')} style={{ width: 40, height: 40, borderRadius: 8 }} />
        <Text style={[styles.title, { color: Colors[theme as 'light' | 'dark'].text }]}>Blood Donation</Text>
      </View>

      <View style={styles.searchBox}>
        <TextInput
          placeholder="City"
          placeholderTextColor={Colors[theme as 'light' | 'dark'].secondaryText}
          style={[styles.input, { 
            color: Colors[theme as 'light' | 'dark'].text, 
            borderColor: Colors[theme as 'light' | 'dark'].border, 
            backgroundColor: Colors[theme as 'light' | 'dark'].inputBackground 
          }]}
          value={searchCity}
          onChangeText={setSearchCity}
        />
        <TextInput
          placeholder="Blood Group"
          placeholderTextColor={Colors[theme as 'light' | 'dark'].secondaryText}
          style={[styles.input, { 
            color: Colors[theme as 'light' | 'dark'].text, 
            borderColor: Colors[theme as 'light' | 'dark'].border, 
            backgroundColor: Colors[theme as 'light' | 'dark'].inputBackground 
          }]}
          value={searchGroup}
          onChangeText={setSearchGroup}
        />
      </View>

      {/* <View style={styles.actionsRow}>
        <TouchableOpacity style={[styles.actionButton, { backgroundColor: '#E11D48' }]} onPress={() => router.replace('/(tabs)/request') }>
          <Text style={styles.actionButtonText}>Request Blood</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.actionButton, { borderColor: '#E11D48', borderWidth: 1 }]} onPress={() => router.replace('/(tabs)/donors') }>
          <Text style={styles.actionButtonText}>Find Donors</Text>
        </TouchableOpacity>
      </View> */}

      {/* Urgent Requests Section - Enhanced */}
      <View style={{ marginTop: 16 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <Text style={[styles.sectionTitle, { color: Colors[theme as 'light' | 'dark'].text }]}>Urgent Requests</Text>
          {filteredUrgent.length > 0 && (
            <Ionicons name="alert-circle" size={20} color="#EF4444" />
          )}
        </View>
        
        {filteredUrgent.length === 0 ? (
          <View style={[styles.emptyCard, { backgroundColor: Colors[theme as 'light' | 'dark'].cardBackground, borderColor: Colors[theme as 'light' | 'dark'].border }]}>
            <Ionicons name="heart" size={32} color={Colors[theme as 'light' | 'dark'].secondaryText} />
            <Text style={{ color: Colors[theme as 'light' | 'dark'].secondaryText, marginTop: 8 }}>No urgent requests at the moment</Text>
          </View>
        ) : (
          <FlatList
            data={filteredUrgent}
            keyExtractor={(item) => item.id}
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={{ gap: 12 }}
            renderItem={({ item }) => (
              <View style={[styles.urgentCard, { backgroundColor: Colors[theme as 'light' | 'dark'].cardBackground, borderColor: Colors[theme as 'light' | 'dark'].border }]}> 
                <View style={styles.urgentHeader}>
                  <Text style={[styles.cardTitle, { color: Colors[theme as 'light' | 'dark'].text }]}>{item.patientName}</Text>
                  <Text style={[styles.timeAgo, { color: Colors[theme as 'light' | 'dark'].secondaryText }]}>{formatTimeAgo(item.createdAt)}</Text>
                </View>
                
                <View style={styles.urgentInfo}>
                  <View style={styles.infoRow}>
                    <Ionicons name="water" size={16} color="#EF4444" />
                    <Text style={[styles.cardLine, { color: Colors[theme as 'light' | 'dark'].text }]}>{item.requiredBloodGroup}</Text>
                  </View>
                  <View style={styles.infoRow}>
                    <Ionicons name="location" size={16} color="#3B82F6" />
                    <Text style={[styles.cardLine, { color: Colors[theme as 'light' | 'dark'].text }]}>{item.city}</Text>
                  </View>
                  {item.hospital && (
                    <View style={styles.infoRow}>
                      <Ionicons name="medical" size={16} color="#10B981" />
                      <Text style={[styles.cardLine, { color: Colors[theme as 'light' | 'dark'].text }]} numberOfLines={1}>{item.hospital}</Text>
                    </View>
                  )}
                </View>

                <View style={styles.urgentActions}>
                  <TouchableOpacity 
                    style={[styles.detailsButton, { borderColor: Colors[theme as 'light' | 'dark'].border }]}
                    onPress={() => router.push(`/request/${item.id}`)}
                  >
                    <Text style={[styles.detailsButtonText, { color: Colors[theme as 'light' | 'dark'].linkText }]}>View Details</Text>
                  </TouchableOpacity>
                  
                  {mode === 'donor' && item.status === 'open' && (
                    <TouchableOpacity 
                      style={[styles.acceptButton, { opacity: acceptingRequest === item.id ? 0.7 : 1 }]}
                      onPress={() => handleAcceptRequest(item.id)}
                      disabled={acceptingRequest === item.id}
                    >
                      <Text style={styles.acceptButtonText}>
                        {acceptingRequest === item.id ? 'Accepting...' : 'Accept'}
                      </Text>
                    </TouchableOpacity>
                  )}
                </View>
              </View>
            )}
          />
        )}
      </View>

    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, gap: 12 },
  headerBranding: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  title: {
    fontSize: 28,
    fontWeight: '700',
  },
  subtitle: {
    fontSize: 16,
    opacity: 0.7,
  },
  searchBox: { flexDirection: 'row', gap: 8, marginTop: 8 },
  input: { borderWidth: 1, borderRadius: 10, padding: 10, flex: 1 },
  actionsRow: { flexDirection: 'row', gap: 12, marginTop: 8 },
  actionButton: {
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    flex: 1,
  },
  actionButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
  sectionTitle: { fontSize: 18, fontWeight: '700', marginTop: 4 },
  
  // Empty state
  emptyCard: { 
    padding: 24, 
    borderWidth: 1, 
    borderRadius: 12, 
    alignItems: 'center', 
    borderStyle: 'dashed' 
  },
  
  // Urgent requests
  urgentCard: { 
    width: 280, 
    padding: 16, 
    borderWidth: 1, 
    borderRadius: 12, 
    gap: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#EF4444'
  },
  urgentHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'flex-start' 
  },
  urgentInfo: { gap: 8 },
  urgentActions: { 
    flexDirection: 'row', 
    gap: 8, 
    marginTop: 4 
  },
  timeAgo: { 
    fontSize: 11, 
    fontWeight: '500' 
  },
  infoRow: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 6 
  },
  detailsButton: { 
    flex: 1, 
    borderWidth: 1, 
    paddingVertical: 8, 
    borderRadius: 6, 
    alignItems: 'center' 
  },
  detailsButtonText: { 
    fontSize: 12, 
    fontWeight: '600' 
  },
  acceptButton: { 
    flex: 1, 
    backgroundColor: '#10B981', 
    paddingVertical: 8, 
    borderRadius: 6, 
    alignItems: 'center' 
  },
  acceptButtonText: { 
    color: '#fff', 
    fontSize: 12, 
    fontWeight: '600' 
  },
  
  // Legacy
  card: { width: 220, padding: 12, borderRadius: 12, borderWidth: 1 },
  cardTitle: { fontSize: 16, fontWeight: '700' },
  cardLine: { marginTop: 4 },
});


