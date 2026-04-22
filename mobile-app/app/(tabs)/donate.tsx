import { Colors } from '@/constants/Colors';
import { useThemeCustom } from '@/context/ThemeContext';
import { createStripePaymentIntent, recordMoneyDonation } from '@/lib/donations';
import { Ionicons } from '@expo/vector-icons';
import { useStripe } from '@stripe/stripe-react-native';
import { Link } from 'expo-router';
import { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

const PREDEFINED_AMOUNTS = [500, 1000, 2500, 5000];
const PURPOSE_OPTIONS = [
  { id: 'platform', label: 'Platform Support', description: 'General platform maintenance and development' },
  { id: 'emergency', label: 'Emergency Fund', description: 'Support urgent blood donation needs' },
  { id: 'equipment', label: 'Equipment', description: 'Medical equipment and supplies' },
  { id: 'general', label: 'General', description: 'General blood bank operations' },
];

export default function DonateScreen() {
  const { theme } = useThemeCustom();
  const isDark = theme === 'dark';
  const { initPaymentSheet, presentPaymentSheet } = useStripe();
  const [selectedAmount, setSelectedAmount] = useState<number | null>(null);
  const [customAmount, setCustomAmount] = useState('');
  const [selectedPurpose, setSelectedPurpose] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAmountSelect = (amount: number) => {
    setSelectedAmount(amount);
    setCustomAmount('');
  };

  const handleCustomAmountChange = (text: string) => {
    setCustomAmount(text);
    setSelectedAmount(null);
  };

  const getFinalAmount = () => {
    if (selectedAmount) return selectedAmount;
    const custom = parseFloat(customAmount);
    return isNaN(custom) ? 0 : custom;
  };

  const handleDonate = async () => {
    const amount = getFinalAmount();
    const purpose = selectedPurpose ? PURPOSE_OPTIONS.find(p => p.id === selectedPurpose)?.label : undefined;

    if (amount < 100) {
      Alert.alert('Invalid Amount', 'Minimum donation amount is PKR 100');
      return;
    }

    try {
      setLoading(true);
      
      // Create payment intent via Node.js backend
      const clientSecret = await createStripePaymentIntent({
        amount,
        currency: 'PKR',
        purpose,
      });
      
      // Initialize payment sheet with Stripe SDK
      const { error: initError } = await initPaymentSheet({
        paymentIntentClientSecret: clientSecret,
        merchantDisplayName: 'Blood Bank',
        allowsDelayedPaymentMethods: true,
      });

      if (initError) {
        throw new Error(initError.message);
      }

      // Present payment sheet
      const { error: presentError } = await presentPaymentSheet();

      if (presentError) {
        if (presentError.code === 'Canceled') {
          // User canceled - no error needed
          return;
        }
        throw new Error(presentError.message);
      }

      // Payment succeeded - record the donation
      try {
        await recordMoneyDonation({
          amount,
          currency: 'PKR',
          purpose,
          stripePaymentId: 'stripe_payment_' + Date.now(), // Placeholder since we don't have the actual payment ID
        });
        
        Alert.alert('Success', 'Thank you for your donation! A receipt has been sent to your email.');
        
        // Reset form
        setSelectedAmount(null);
        setCustomAmount('');
        setSelectedPurpose(null);
      } catch (recordError) {
        console.error('Failed to record donation:', recordError);
        Alert.alert('Success', 'Thank you for your donation! A receipt has been sent to your email.');
        
        // Reset form even if recording failed
        setSelectedAmount(null);
        setCustomAmount('');
        setSelectedPurpose(null);
      }
      
    } catch (error: any) {
      Alert.alert('Payment Error', error?.message || 'Failed to process donation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: Colors[theme].background }]}>
      <View style={styles.header}>
        <Ionicons name="heart" size={48} color="#E11D48" />
        <Text style={[styles.title, { color: Colors[theme].text }]}>Support Our Mission</Text>
        <Text style={[styles.subtitle, { color: Colors[theme].secondaryText }]}>
          Your monetary donations help us maintain the platform and support blood donation operations
        </Text>
      </View>

      {/* Amount Selection */}
      <View style={[styles.section, { backgroundColor: isDark ? '#1F2937' : '#F9FAFB' }]}>
        <Text style={[styles.sectionTitle, { color: Colors[theme].text }]}>Select Amount (PKR)</Text>
        
        <View style={styles.amountGrid}>
          {PREDEFINED_AMOUNTS.map((amount) => (
            <TouchableOpacity
              key={amount}
              style={[
                styles.amountButton,
                selectedAmount === amount && styles.amountButtonSelected,
                { borderColor: isDark ? '#374151' : '#D1D5DB' }
              ]}
              onPress={() => handleAmountSelect(amount)}
            >
              <Text style={[
                styles.amountText,
                selectedAmount === amount && styles.amountTextSelected,
                { color: selectedAmount === amount ? '#fff' : Colors[theme].text }
              ]}>
                {amount.toLocaleString()}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={[styles.orText, { color: Colors[theme].secondaryText }]}>or</Text>
        
        <View style={[styles.customAmountContainer, { borderColor: isDark ? '#374151' : '#D1D5DB' }]}>
          <Text style={[styles.currencySymbol, { color: Colors[theme].text }]}>PKR</Text>
          <TextInput
            style={[
              styles.customAmountInput, 
              { 
                color: Colors[theme].text,
                opacity: selectedAmount ? 0.5 : 1
              }
            ]}
            placeholder="Enter custom amount"
            placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'}
            value={customAmount}
            onChangeText={handleCustomAmountChange}
            keyboardType="numeric"
            editable={!selectedAmount}
          />
        </View>
      </View>

      {/* Purpose Selection */}
      <View style={[styles.section, { backgroundColor: isDark ? '#1F2937' : '#F9FAFB' }]}>
        <Text style={[styles.sectionTitle, { color: Colors[theme].text }]}>Purpose (Optional)</Text>
        
        {PURPOSE_OPTIONS.map((purpose) => (
          <TouchableOpacity
            key={purpose.id}
            style={[
              styles.purposeButton,
              selectedPurpose === purpose.id && styles.purposeButtonSelected,
              { borderColor: isDark ? '#374151' : '#D1D5DB' }
            ]}
            onPress={() => setSelectedPurpose(selectedPurpose === purpose.id ? null : purpose.id)}
          >
            <View style={styles.purposeContent}>
              <Text style={[
                styles.purposeLabel,
                { color: selectedPurpose === purpose.id ? '#fff' : Colors[theme].text }
              ]}>
                {purpose.label}
              </Text>
              <Text style={[
                styles.purposeDescription,
                { color: selectedPurpose === purpose.id ? '#E5E7EB' : Colors[theme].secondaryText }
              ]}>
                {purpose.description}
              </Text>
            </View>
            {selectedPurpose === purpose.id && (
              <Ionicons name="checkmark-circle" size={20} color="#10B981" />
            )}
          </TouchableOpacity>
        ))}
      </View>

      {/* Donation Summary */}
      <View style={[styles.summary, { backgroundColor: isDark ? '#1E3A8A' : '#EFF6FF', borderColor: '#3B82F6' }]}>
        <Text style={[styles.summaryLabel, { color: isDark ? '#93C5FD' : '#1E40AF' }]}>Donation Amount</Text>
        <Text style={[styles.summaryAmount, { color: isDark ? '#DBEAFE' : '#1E3A8A' }]}>
          PKR {getFinalAmount().toLocaleString()}
        </Text>
      </View>

      {/* Action Buttons */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={[
            styles.donateButton,
            { backgroundColor: getFinalAmount() >= 100 ? '#E11D48' : '#9CA3AF' }
          ]}
          onPress={handleDonate}
          disabled={getFinalAmount() < 100 || loading}
        >
          <Ionicons name="card" size={20} color="#fff" />
          <Text style={styles.donateButtonText}>
            {loading ? 'Processing...' : 'Donate Now'}
          </Text>
        </TouchableOpacity>

        <Link href="/donations" asChild>
          <TouchableOpacity style={[styles.historyButton, { borderColor: isDark ? '#374151' : '#D1D5DB' }]}>
            <Ionicons name="time" size={20} color={Colors[theme].text} />
            <Text style={[styles.historyButtonText, { color: Colors[theme].text }]}>
              View Donation History
            </Text>
          </TouchableOpacity>
        </Link>
      </View>

      {/* Information */}
      <View style={[styles.info, { backgroundColor: isDark ? '#1F2937' : '#F3F4F6' }]}>
        <Ionicons name="information-circle" size={20} color="#3B82F6" />
        <Text style={[styles.infoText, { color: Colors[theme].secondaryText }]}>
          All donations are processed securely through Stripe. You'll receive a receipt via email.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
    paddingVertical: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    marginTop: 12,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 22,
  },
  section: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 16,
  },
  amountGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 16,
  },
  amountButton: {
    flex: 1,
    minWidth: 80,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    alignItems: 'center',
  },
  amountButtonSelected: {
    backgroundColor: '#E11D48',
    borderColor: '#E11D48',
  },
  amountText: {
    fontSize: 16,
    fontWeight: '600',
  },
  amountTextSelected: {
    color: '#fff',
  },
  orText: {
    textAlign: 'center',
    fontSize: 14,
    marginVertical: 8,
  },
  customAmountContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 12,
  },
  currencySymbol: {
    fontSize: 16,
    fontWeight: '600',
    marginRight: 8,
  },
  customAmountInput: {
    flex: 1,
    fontSize: 16,
    paddingVertical: 12,
  },
  purposeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    marginBottom: 8,
  },
  purposeButtonSelected: {
    backgroundColor: '#E11D48',
    borderColor: '#E11D48',
  },
  purposeContent: {
    flex: 1,
  },
  purposeLabel: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  purposeDescription: {
    fontSize: 14,
    lineHeight: 18,
  },
  summary: {
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
    marginBottom: 24,
  },
  summaryLabel: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 8,
  },
  summaryAmount: {
    fontSize: 28,
    fontWeight: '700',
  },
  actions: {
    gap: 12,
    marginBottom: 24,
  },
  donateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    gap: 8,
  },
  donateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  historyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    borderWidth: 1,
    gap: 8,
  },
  historyButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  info: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 16,
    borderRadius: 8,
    gap: 12,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
  },
});
