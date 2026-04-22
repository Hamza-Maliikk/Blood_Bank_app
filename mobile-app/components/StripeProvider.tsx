import { StripeProvider as NativeStripeProvider } from '@stripe/stripe-react-native';
import { STRIPE_CONFIG } from '@/config/stripe';

export default function StripeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NativeStripeProvider publishableKey={STRIPE_CONFIG.publishableKey}>
      {children}
    </NativeStripeProvider>
  );
}
