import { STRIPE_PRODUCTS, formatCurrency } from '@/config/stripe';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import { createStripePaymentIntent } from '@/lib/donations';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import { Alert, Linking, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

export default function AddMoneyDonationScreen() {
  const colorScheme = useColorScheme() ?? 'light';
  const isDark = colorScheme === 'dark';
  const router = useRouter();
  const [amount, setAmount] = useState('');
  const [purpose, setPurpose] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async () => {
    const amountNum = parseFloat(amount);
    if (!amount || isNaN(amountNum) || amountNum <= 0) {
      Alert.alert('Invalid Amount', 'Please enter a valid donation amount.');
      return;
    }

    // Validate minimum amount
    const { minimumAmount } = STRIPE_PRODUCTS.donations;
    if (amountNum < minimumAmount / 100) {
      Alert.alert(
        'Minimum Amount Required', 
        `The minimum donation amount is ${formatCurrency(minimumAmount)}.`
      );
      return;
    }

    try {
      setLoading(true);
      
      // Create Stripe checkout session
      const sessionUrl = await createStripePaymentIntent({
        amount: amountNum,
        currency: 'PKR',
        purpose: purpose.trim() || undefined,
      });
      
      // Open Stripe checkout in browser
      const supported = await Linking.canOpenURL(sessionUrl);
      if (supported) {
        await Linking.openURL(sessionUrl);
        
        // Show success message and navigate
        Alert.alert(
          'Payment Started',
          'You will be redirected to complete your donation payment. Thank you for your generosity!',
          [
            {
              text: 'View History',
              onPress: () => router.push('/donations'),
            },
            {
              text: 'OK',
              style: 'default',
              onPress: () => router.back(),
            },
          ]
        );
        
        // Reset form
        setAmount('');
        setPurpose('');
      } else {
        throw new Error('Unable to open payment page');
      }
    } catch (e: any) {
      Alert.alert('Payment Error', e?.message ?? 'Failed to start payment process. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const quickAmounts = [100, 250, 500, 1000, 2500, 5000];

  return (
    <View style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}>
      <View style={[styles.header, { backgroundColor: isDark ? '#111827' : '#fff', borderColor: isDark ? '#374151' : '#e5e7eb' }]}>
        <Ionicons name="heart" size={32} color="#E11D48" />
        <Text style={[styles.title, { color: isDark ? '#fff' : Colors[colorScheme].text }]}>Make a Donation</Text>
        <Text style={[styles.subtitle, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>
          Your contribution helps save lives and supports our blood donation community
        </Text>
      </View>

      <View style={[styles.form, { backgroundColor: isDark ? '#111827' : '#fff', borderColor: isDark ? '#374151' : '#e5e7eb' }]}>
        <Text style={[styles.label, { color: isDark ? '#fff' : '#111827' }]}>Donation Amount (PKR) *</Text>
        
        {/* Quick Amount Buttons */}
        <View style={styles.quickAmounts}>
          {quickAmounts.map((quickAmount) => (
            <TouchableOpacity
              key={quickAmount}
              style={[
                styles.quickAmountButton,
                { 
                  backgroundColor: amount === quickAmount.toString() ? '#E11D48' : (isDark ? '#374151' : '#F3F4F6'),
                  borderColor: isDark ? '#4B5563' : '#E5E7EB',
                }
              ]}
              onPress={() => setAmount(quickAmount.toString())}
            >
              <Text style={[
                styles.quickAmountText,
                { color: amount === quickAmount.toString() ? '#fff' : (isDark ? '#D1D5DB' : '#374151') }
              ]}>
                {quickAmount}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <TextInput
          placeholder="Enter custom amount"
          placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'}
          style={[
            styles.input,
            {
              color: isDark ? '#fff' : '#111827',
              borderColor: isDark ? '#374151' : '#e5e7eb',
              backgroundColor: isDark ? '#1F2937' : '#fff',
            }
          ]}
          value={amount}
          onChangeText={setAmount}
          keyboardType="numeric"
        />

        <Text style={[styles.label, { color: isDark ? '#fff' : '#111827', marginTop: 20 }]}>Purpose (Optional)</Text>
        <TextInput
          placeholder="e.g., Support patient transport, Hospital supplies, General donation"
          placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'}
          style={[
            styles.input,
            styles.textArea,
            {
              color: isDark ? '#fff' : '#111827',
              borderColor: isDark ? '#374151' : '#e5e7eb',
              backgroundColor: isDark ? '#1F2937' : '#fff',
            }
          ]}
          value={purpose}
          onChangeText={setPurpose}
          multiline
          numberOfLines={3}
        />

        <View style={[styles.infoBox, { backgroundColor: isDark ? '#1E3A8A' : '#EFF6FF', borderColor: '#3B82F6' }]}>
          <Ionicons name="information-circle" size={20} color="#3B82F6" />
          <Text style={[styles.infoText, { color: isDark ? '#93C5FD' : '#1E40AF' }]}>
            Your donation will be used to support blood donation activities and help patients in need.
          </Text>
        </View>

        <TouchableOpacity
          style={[
            styles.submitButton,
            {
              backgroundColor: loading || !amount ? '#9CA3AF' : '#E11D48',
            }
          ]}
          onPress={onSubmit}
          disabled={loading || !amount}
        >
          <Ionicons name={loading ? 'hourglass' : 'card'} size={20} color="#fff" />
          <Text style={styles.submitButtonText}>
            {loading ? 'Processing...' : `Pay PKR ${amount || '0'} via Stripe`}
          </Text>
        </TouchableOpacity>
        
        <View style={[styles.securityInfo, { backgroundColor: isDark ? '#1F2937' : '#F9FAFB' }]}>
          <Ionicons name="shield-checkmark" size={16} color="#10B981" />
          <Text style={[styles.securityText, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>
            Secure payment powered by Stripe. Your card information is encrypted and safe.
          </Text>
        </View>
      </View>

      <View style={[styles.footer, { backgroundColor: isDark ? '#111827' : '#fff', borderColor: isDark ? '#374151' : '#e5e7eb' }]}>
        <Text style={[styles.footerTitle, { color: isDark ? '#fff' : '#111827' }]}>Why Donate?</Text>
        <View style={styles.benefitsList}>
          <View style={styles.benefitItem}>
            <Ionicons name="medical" size={16} color="#10B981" />
            <Text style={[styles.benefitText, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>
              Support medical equipment and supplies
            </Text>
          </View>
          <View style={styles.benefitItem}>
            <Ionicons name="car" size={16} color="#10B981" />
            <Text style={[styles.benefitText, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>
              Help with patient transportation costs
            </Text>
          </View>
          <View style={styles.benefitItem}>
            <Ionicons name="people" size={16} color="#10B981" />
            <Text style={[styles.benefitText, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>
              Maintain our blood donation community
            </Text>
          </View>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  header: { borderWidth: 1, borderRadius: 16, padding: 20, marginBottom: 16, alignItems: 'center' },
  title: { fontSize: 24, fontWeight: '700', marginTop: 12, marginBottom: 8 },
  subtitle: { fontSize: 14, textAlign: 'center', lineHeight: 20 },
  form: { borderWidth: 1, borderRadius: 16, padding: 20, marginBottom: 16 },
  label: { fontSize: 16, fontWeight: '600', marginBottom: 8 },
  quickAmounts: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 16 },
  quickAmountButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    borderWidth: 1,
  },
  quickAmountText: { fontSize: 14, fontWeight: '600' },
  input: {
    borderWidth: 1,
    borderRadius: 12,
    padding: 12,
    fontSize: 16,
  },
  textArea: { height: 80, textAlignVertical: 'top' },
  infoBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    marginTop: 16,
    marginBottom: 20,
  },
  infoText: { fontSize: 12, lineHeight: 16, flex: 1 },
  submitButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 16,
    borderRadius: 12,
  },
  submitButtonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  footer: { borderWidth: 1, borderRadius: 16, padding: 20 },
  footerTitle: { fontSize: 18, fontWeight: '700', marginBottom: 12 },
  benefitsList: { gap: 8 },
  benefitItem: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  benefitText: { fontSize: 14, flex: 1 },
  securityInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 12,
    borderRadius: 8,
    marginTop: 12,
  },
  securityText: { fontSize: 12, flex: 1 },
});