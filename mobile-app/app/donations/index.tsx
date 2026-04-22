import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import { listMyMoneyDonations } from '@/lib/donations';
import { MoneyDonation } from '@/lib/types';
import { Ionicons } from '@expo/vector-icons';
import { Link } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { Alert, FlatList, Linking, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

export default function DonationsScreen() {
  const colorScheme = useColorScheme() ?? 'light';
  const isDark = colorScheme === 'dark';
  const [donations, setDonations] = useState<MoneyDonation[]>([]);
  const [filteredDonations, setFilteredDonations] = useState<MoneyDonation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'amount'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    loadDonations();
  }, []);

  useEffect(() => {
    filterAndSortDonations();
  }, [donations, searchQuery, sortBy, sortOrder]);

  const loadDonations = async () => {
    try {
      setLoading(true);
      const moneyDonations = await listMyMoneyDonations();
      setDonations(moneyDonations);
    } catch (e) {
      console.error('Failed to load donations', e);
      Alert.alert('Error', 'Failed to load donation history');
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortDonations = () => {
    let filtered = [...donations];

    // Filter by search query (amount or purpose)
    if (searchQuery) {
      filtered = filtered.filter(donation => 
        donation.amount.toString().includes(searchQuery) ||
        (donation.purpose && donation.purpose.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Sort donations
    filtered.sort((a, b) => {
      if (sortBy === 'date') {
        return sortOrder === 'asc' ? a.createdAt - b.createdAt : b.createdAt - a.createdAt;
      } else {
        return sortOrder === 'asc' ? a.amount - b.amount : b.amount - a.amount;
      }
    });

    setFilteredDonations(filtered);
  };

  const openReceipt = (receiptUrl: string) => {
    Linking.openURL(receiptUrl);
  };

  const totalDonated = donations.reduce((sum, donation) => sum + donation.amount, 0);
  const totalDonations = donations.length;
  const averageDonation = totalDonations > 0 ? totalDonated / totalDonations : 0;

  return (
    <ScrollView style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}>
      <View style={[styles.header, { backgroundColor: isDark ? '#111827' : '#fff', borderColor: isDark ? '#374151' : '#e5e7eb' }]}>
        <Ionicons name="heart" size={32} color="#E11D48" />
        <Text style={[styles.title, { color: isDark ? '#fff' : Colors[colorScheme].text }]}>Donation History</Text>
        <Text style={[styles.subtitle, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>
          Track your monetary contributions to the blood bank platform
        </Text>
        
        {donations.length > 0 && (
          <View style={styles.statsContainer}>
            <View style={[styles.statCard, { backgroundColor: isDark ? '#1E3A8A' : '#EFF6FF', borderColor: '#3B82F6' }]}>
              <Text style={[styles.statLabel, { color: isDark ? '#93C5FD' : '#1E40AF' }]}>Total Donated</Text>
              <Text style={[styles.statValue, { color: isDark ? '#DBEAFE' : '#1E3A8A' }]}>
                PKR {totalDonated.toLocaleString()}
              </Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: isDark ? '#059669' : '#ECFDF5', borderColor: '#10B981' }]}>
              <Text style={[styles.statLabel, { color: isDark ? '#6EE7B7' : '#047857' }]}>Total Donations</Text>
              <Text style={[styles.statValue, { color: isDark ? '#D1FAE5' : '#065F46' }]}>
                {totalDonations}
              </Text>
            </View>
            <View style={[styles.statCard, { backgroundColor: isDark ? '#7C3AED' : '#F3E8FF', borderColor: '#8B5CF6' }]}>
              <Text style={[styles.statLabel, { color: isDark ? '#C4B5FD' : '#7C2D12' }]}>Average</Text>
              <Text style={[styles.statValue, { color: isDark ? '#E9D5FF' : '#581C87' }]}>
                PKR {Math.round(averageDonation).toLocaleString()}
              </Text>
            </View>
          </View>
        )}
      </View>

      {/* Search and Filter Controls */}
      {donations.length > 0 && (
        <View style={[styles.controls, { backgroundColor: isDark ? '#1F2937' : '#F9FAFB' }]}>
          <View style={[styles.searchContainer, { borderColor: isDark ? '#374151' : '#D1D5DB' }]}>
            <Ionicons name="search" size={20} color={isDark ? '#9CA3AF' : '#6B7280'} />
            <TextInput
              style={[styles.searchInput, { color: Colors[colorScheme].text }]}
              placeholder="Search by amount or purpose..."
              placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'}
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </View>
          
          <View style={styles.sortControls}>
            <TouchableOpacity
              style={[styles.sortButton, { backgroundColor: isDark ? '#374151' : '#E5E7EB' }]}
              onPress={() => setSortBy(sortBy === 'date' ? 'amount' : 'date')}
            >
              <Text style={[styles.sortButtonText, { color: Colors[colorScheme].text }]}>
                Sort by: {sortBy === 'date' ? 'Date' : 'Amount'}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={[styles.sortButton, { backgroundColor: isDark ? '#374151' : '#E5E7EB' }]}
              onPress={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            >
              <Ionicons 
                name={sortOrder === 'asc' ? 'arrow-up' : 'arrow-down'} 
                size={16} 
                color={Colors[colorScheme].text} 
              />
            </TouchableOpacity>
          </View>
        </View>
      )}

      {donations.length > 0 && (
        <View style={styles.actionBar}>
          <Link href="/(tabs)/donate" asChild>
            <TouchableOpacity style={styles.addButton}>
              <Ionicons name="add" size={20} color="#fff" />
              <Text style={styles.addButtonText}>Make New Donation</Text>
            </TouchableOpacity>
          </Link>
        </View>
      )}

      {loading ? (
        <View style={styles.centered}>
          <Text style={[styles.loadingText, { color: isDark ? '#fff' : Colors[colorScheme].text }]}>Loading donations...</Text>
        </View>
      ) : donations.length === 0 ? (
        <View style={styles.centered}>
          <Ionicons name="heart-outline" size={64} color={isDark ? '#6B7280' : '#9CA3AF'} />
          <Text style={[styles.emptyTitle, { color: isDark ? '#fff' : Colors[colorScheme].text }]}>No Donations Yet</Text>
          <Text style={[styles.emptySubtitle, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>
            Start contributing to the blood bank platform
          </Text>
          <Link href="/(tabs)/donate" asChild>
            <TouchableOpacity style={styles.emptyButton}>
              <Ionicons name="add" size={20} color="#fff" />
              <Text style={styles.emptyButtonText}>Make First Donation</Text>
            </TouchableOpacity>
          </Link>
        </View>
      ) : (
        <FlatList
          data={filteredDonations}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ gap: 12, paddingBottom: 20 }}
          renderItem={({ item }) => (
            <View style={[styles.donationCard, { backgroundColor: isDark ? '#111827' : '#fff', borderColor: isDark ? '#374151' : '#e5e7eb' }]}>
              <View style={styles.donationHeader}>
                <View style={styles.donationInfo}>
                  <Text style={[styles.donationAmount, { color: '#10B981' }]}>
                    PKR {item.amount.toLocaleString()}
                  </Text>
                  <Text style={[styles.donationDate, { color: isDark ? '#9CA3AF' : '#6B7280' }]}>
                    {new Date(item.createdAt).toLocaleDateString()}
                  </Text>
                </View>
                <Ionicons name="heart" size={24} color="#E11D48" />
              </View>
              
              {item.purpose && (
                <Text style={[styles.donationPurpose, { color: isDark ? '#D1D5DB' : '#374151' }]}>
                  Purpose: {item.purpose}
                </Text>
              )}
              
              <View style={styles.donationFooter}>
                <Text style={[styles.donationId, { color: isDark ? '#9CA3AF' : '#9CA3AF' }]}>
                  ID: {item.id.slice(-8)}
                </Text>
                
                {item.receiptUrl && (
                  <TouchableOpacity
                    style={styles.receiptButton}
                    onPress={() => openReceipt(item.receiptUrl!)}
                  >
                    <Ionicons name="document-text" size={16} color="#3B82F6" />
                    <Text style={styles.receiptButtonText}>View Receipt</Text>
                  </TouchableOpacity>
                )}
              </View>
            </View>
          )}
          ListEmptyComponent={
            <View style={styles.centered}>
              <Ionicons name="search" size={48} color={isDark ? '#6B7280' : '#9CA3AF'} />
              <Text style={[styles.emptyTitle, { color: isDark ? '#fff' : Colors[colorScheme].text }]}>No Results Found</Text>
              <Text style={[styles.emptySubtitle, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>
                Try adjusting your search criteria
              </Text>
            </View>
          }
        />
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  header: { borderWidth: 1, borderRadius: 16, padding: 20, marginBottom: 16, alignItems: 'center' as const },
  title: { fontSize: 24, fontWeight: '700' as const, marginTop: 12, marginBottom: 8 },
  subtitle: { fontSize: 14, textAlign: 'center' as const, lineHeight: 20, marginBottom: 16 },
  totalCard: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center' as const,
  },
  totalLabel: { fontSize: 12, fontWeight: '600' as const, marginBottom: 4 },
  totalAmount: { fontSize: 20, fontWeight: '700' as const },
  actionBar: { marginBottom: 16 },
  addButton: {
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    gap: 8,
    backgroundColor: '#E11D48',
    paddingVertical: 12,
    borderRadius: 12,
  },
  addButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' as const },
  centered: { flex: 1, justifyContent: 'center' as const, alignItems: 'center' as const },
  loadingText: { fontSize: 16 },
  donationCard: { borderWidth: 1, borderRadius: 12, padding: 16 },
  donationHeader: { flexDirection: 'row' as const, justifyContent: 'space-between' as const, alignItems: 'flex-start' as const, marginBottom: 8 },
  donationInfo: { flex: 1 },
  donationAmount: { fontSize: 18, fontWeight: '700' as const, marginBottom: 4 },
  donationDate: { fontSize: 12 },
  donationPurpose: { fontSize: 14, marginBottom: 12, fontStyle: 'italic' as const },
  donationFooter: { flexDirection: 'row' as const, justifyContent: 'space-between' as const, alignItems: 'center' as const },
  donationId: { fontSize: 10, fontFamily: 'monospace' },
  receiptButton: { flexDirection: 'row' as const, alignItems: 'center' as const, gap: 4 },
  receiptButtonText: { color: '#3B82F6', fontSize: 12, fontWeight: '600' as const },
  emptyState: { alignItems: 'center' as const, paddingVertical: 40 },
  emptyTitle: { fontSize: 18, fontWeight: '700' as const, marginTop: 16, marginBottom: 8 },
  emptySubtitle: { fontSize: 14, textAlign: 'center' as const, lineHeight: 20, marginBottom: 24 },
  emptyActionButton: {
    backgroundColor: '#E11D48',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 12,
  },
  emptyActionButtonText: { color: '#fff', fontSize: 14, fontWeight: '600' as const },
  statsContainer: {
    flexDirection: 'row' as const,
    gap: 12,
    marginTop: 16,
  },
  statCard: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center' as const,
  },
  statLabel: {
    fontSize: 12,
    fontWeight: '500' as const,
    marginBottom: 4,
  },
  statValue: {
    fontSize: 16,
    fontWeight: '700' as const,
  },
  controls: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  searchContainer: {
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 12,
    marginBottom: 12,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    paddingVertical: 12,
    marginLeft: 8,
  },
  sortControls: {
    flexDirection: 'row' as const,
    gap: 8,
  },
  sortButton: {
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    gap: 4,
  },
  sortButtonText: {
    fontSize: 14,
    fontWeight: '500' as const,
  },
  emptyButton: {
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    backgroundColor: '#E11D48',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 12,
    gap: 8,
  },
  emptyButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600' as const,
  },
});


