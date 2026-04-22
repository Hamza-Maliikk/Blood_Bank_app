import { Colors } from '@/constants/Colors';
import { useThemeCustom } from '@/context/ThemeContext';
import { getDonorStats } from '@/lib/requests';
import { getUserProfile } from '@/lib/users';
import { Ionicons } from '@expo/vector-icons';
import { useLocalSearchParams } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { Image, Linking, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function DonorProfileScreen() {
  const { theme } = useThemeCustom();
  const isDark = theme === 'dark';
  const { uid } = useLocalSearchParams<{ uid: string }>();
  const [profile, setProfile] = useState<any>(null);
  const [stats, setStats] = useState<{ totalReceived: number; accepted: number; rejected: number }>({
    totalReceived: 0,
    accepted: 0,
    rejected: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      if (!uid) return;
      try {
        setLoading(true);
        const [userProfile, donorStats] = await Promise.all([
          getUserProfile(uid),
          getDonorStats(uid),
        ]);
        setProfile(userProfile);
        setStats(donorStats);
      } catch (e) {
        console.error('Failed to load donor profile', e);
      } finally {
        setLoading(false);
      }
    })();
  }, [uid]);

  const callDonor = () => {
    if (!profile?.phone) return;
    Linking.openURL(`tel:${profile.phone}`);
  };

  const sendSMS = () => {
    if (!profile?.phone) return;
    Linking.openURL(`sms:${profile.phone}`);
  };

  const openWhatsApp = () => {
    if (!profile?.phone) return;
    const digits = (profile.phone ?? '').replace(/\D/g, '');
    const wa = `https://wa.me/${digits}`;
    Linking.openURL(wa);
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.centered, { backgroundColor: Colors[theme].background }]}>
        <Text style={[styles.loadingText, { color: isDark ? '#fff' : Colors[theme].text }]}>Loading...</Text>
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={[styles.container, styles.centered, { backgroundColor: Colors[theme].background }]}>
        <Text style={[styles.errorText, { color: isDark ? '#fff' : Colors[theme].text }]}>Profile not found</Text>
      </View>
    );
  }

  const isValidPhone = profile.phone && profile.phone.startsWith('+92') && profile.phone.length >= 12;

  return (
    <ScrollView style={[styles.container, { backgroundColor: Colors[theme].background }]} showsVerticalScrollIndicator={false}>
      {/* Profile Header */}
      <View style={[styles.header, { backgroundColor: isDark ? '#111827' : '#fff', borderColor: isDark ? '#374151' : '#e5e7eb' }]}>
        <View style={styles.profileImageContainer}>
          <Image source={require('@/assets/images/profile.png')} style={styles.profileImage} />
          <View style={[styles.availabilityBadge, { backgroundColor: profile.available ? '#10B981' : '#6B7280' }]}>
            <View style={styles.availabilityDot} />
          </View>
        </View>
        
        <View style={styles.profileInfo}>
          <Text style={[styles.name, { color: isDark ? '#fff' : '#111827' }]}>{profile.name}</Text>
          <Text style={[styles.bloodGroup, { color: '#E11D48' }]}>{profile.bloodGroup}</Text>
          <Text style={[styles.location, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>
            <Ionicons name="location" size={14} color={isDark ? '#D1D5DB' : '#6B7280'} /> {profile.city}
          </Text>
          {profile.gender && (
            <Text style={[styles.gender, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>
              <Ionicons name="person" size={14} color={isDark ? '#D1D5DB' : '#6B7280'} /> {profile.gender}
            </Text>
          )}
        </View>

        <View style={[styles.availabilityIndicator, { backgroundColor: profile.available ? '#10B981' : '#6B7280' }]}>
          <Text style={styles.availabilityText}>
            {profile.available ? 'Available' : 'Unavailable'}
          </Text>
        </View>
      </View>

      {/* Donation Stats */}
      <View style={[styles.statsSection, { backgroundColor: isDark ? '#111827' : '#fff', borderColor: isDark ? '#374151' : '#e5e7eb' }]}>
        <Text style={[styles.sectionTitle, { color: isDark ? '#fff' : '#111827' }]}>Donation Statistics</Text>
        
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={[styles.statNumber, { color: '#3B82F6' }]}>{stats.totalReceived}</Text>
            <Text style={[styles.statLabel, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>Total Requests</Text>
          </View>
          
          <View style={styles.statCard}>
            <Text style={[styles.statNumber, { color: '#10B981' }]}>{stats.accepted}</Text>
            <Text style={[styles.statLabel, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>Accepted</Text>
          </View>
          
          <View style={styles.statCard}>
            <Text style={[styles.statNumber, { color: '#EF4444' }]}>{stats.rejected}</Text>
            <Text style={[styles.statLabel, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>Rejected</Text>
          </View>
        </View>

        {stats.totalReceived > 0 && (
          <View style={styles.successRate}>
            <Text style={[styles.successRateLabel, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>Success Rate</Text>
            <Text style={[styles.successRateValue, { color: '#10B981' }]}>
              {Math.round((stats.accepted / stats.totalReceived) * 100)}%
            </Text>
          </View>
        )}
      </View>

      {/* Contact Actions */}
      {isValidPhone && (
        <View style={[styles.contactSection, { backgroundColor: isDark ? '#111827' : '#fff', borderColor: isDark ? '#374151' : '#e5e7eb' }]}>
          <Text style={[styles.sectionTitle, { color: isDark ? '#fff' : '#111827' }]}>Contact Donor</Text>
          
          <View style={styles.contactActions}>
            <TouchableOpacity style={[styles.contactButton, { backgroundColor: '#10B981' }]} onPress={callDonor}>
              <Ionicons name="call" size={20} color="#fff" />
              <Text style={styles.contactButtonText}>Call</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={[styles.contactButton, { backgroundColor: '#3B82F6' }]} onPress={sendSMS}>
              <Ionicons name="chatbubbles" size={20} color="#fff" />
              <Text style={styles.contactButtonText}>SMS</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={[styles.contactButton, { backgroundColor: '#25D366' }]} onPress={openWhatsApp}>
              <Ionicons name="logo-whatsapp" size={20} color="#fff" />
              <Text style={styles.contactButtonText}>WhatsApp</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* Additional Info */}
      <View style={[styles.infoSection, { backgroundColor: isDark ? '#111827' : '#fff', borderColor: isDark ? '#374151' : '#e5e7eb' }]}>
        <Text style={[styles.sectionTitle, { color: isDark ? '#fff' : '#111827' }]}>Profile Information</Text>
        
        <View style={styles.infoRow}>
          <Text style={[styles.infoLabel, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>Member Since</Text>
          <Text style={[styles.infoValue, { color: isDark ? '#fff' : '#111827' }]}>
            {new Date(profile.createdAt).toLocaleDateString()}
          </Text>
        </View>
        
        <View style={styles.infoRow}>
          <Text style={[styles.infoLabel, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>Last Active</Text>
          <Text style={[styles.infoValue, { color: isDark ? '#fff' : '#111827' }]}>
            {new Date(profile.updatedAt).toLocaleDateString()}
          </Text>
        </View>
        
        {profile.available && (
          <View style={[styles.availabilityNote, { backgroundColor: isDark ? '#065F46' : '#ECFDF5', borderColor: '#10B981' }]}>
            <Ionicons name="checkmark-circle" size={16} color="#10B981" />
            <Text style={[styles.availabilityNoteText, { color: isDark ? '#A7F3D0' : '#047857' }]}>
              This donor is currently available for blood donation
            </Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  centered: { justifyContent: 'center', alignItems: 'center' },
  loadingText: { fontSize: 16 },
  errorText: { fontSize: 16, textAlign: 'center' },
  header: { borderWidth: 1, borderRadius: 16, padding: 20, marginBottom: 16, alignItems: 'center' },
  profileImageContainer: { position: 'relative', marginBottom: 16 },
  profileImage: { width: 80, height: 80, borderRadius: 40 },
  availabilityBadge: {
    position: 'absolute',
    bottom: 4,
    right: 4,
    width: 20,
    height: 20,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  availabilityDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#fff' },
  profileInfo: { alignItems: 'center', marginBottom: 16 },
  name: { fontSize: 24, fontWeight: '700', marginBottom: 4 },
  bloodGroup: { fontSize: 20, fontWeight: '600', marginBottom: 8 },
  location: { fontSize: 14, marginBottom: 4 },
  gender: { fontSize: 14 },
  availabilityIndicator: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  availabilityText: { color: '#fff', fontWeight: '600', fontSize: 12 },
  statsSection: { borderWidth: 1, borderRadius: 16, padding: 20, marginBottom: 16 },
  sectionTitle: { fontSize: 18, fontWeight: '700', marginBottom: 16 },
  statsGrid: { flexDirection: 'row', justifyContent: 'space-around', marginBottom: 16 },
  statCard: { alignItems: 'center' },
  statNumber: { fontSize: 24, fontWeight: '700', marginBottom: 4 },
  statLabel: { fontSize: 12, textAlign: 'center' },
  successRate: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingTop: 16, borderTopWidth: 1, borderTopColor: '#e5e7eb' },
  successRateLabel: { fontSize: 16, fontWeight: '600' },
  successRateValue: { fontSize: 18, fontWeight: '700' },
  contactSection: { borderWidth: 1, borderRadius: 16, padding: 20, marginBottom: 16 },
  contactActions: { flexDirection: 'row', gap: 12 },
  contactButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 12,
    borderRadius: 12,
  },
  contactButtonText: { color: '#fff', fontWeight: '600' },
  infoSection: { borderWidth: 1, borderRadius: 16, padding: 20, marginBottom: 16 },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  infoLabel: { fontSize: 14 },
  infoValue: { fontSize: 14, fontWeight: '600' },
  availabilityNote: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    marginTop: 8,
  },
  availabilityNoteText: { fontSize: 12, fontWeight: '600' },
});