import { STRIPE_CONFIG, STRIPE_PRODUCTS, getStripeErrorMessage, pkrToCents } from '@/config/stripe';
import { auth, database } from '@/database/firebase';
import { get, push, ref, set } from 'firebase/database';
import { Donation, MoneyDonation } from './types';

export async function createDonationRecord(requestId: string, donorUid: string): Promise<string> {
  const id = push(ref(database, `donations/${donorUid}`)).key!;
  const data: Donation = {
    id,
    requestId,
    status: 'pending',
    date: Date.now(),
  };
  await set(ref(database, `donations/${donorUid}/${id}`), data);
  return id;
}

export async function listMyDonations(uid?: string): Promise<Donation[]> {
  const userId = uid ?? auth.currentUser?.uid;
  if (!userId) return [];
  const snap = await get(ref(database, `donations/${userId}`));
  if (!snap.exists()) return [];
  return Object.values(snap.val());
}

// Create Stripe payment intent for money donation via Node.js backend
export async function createStripePaymentIntent({ 
  amount, 
  currency = 'PKR', 
  purpose 
}: {
  amount: number;
  currency?: string;
  purpose?: string;
}): Promise<string> {
  const user = auth.currentUser;
  if (!user) throw new Error('Authentication required');

  try {
    // Convert PKR to cents for Stripe
    const amountInCents = pkrToCents(amount);
    
    // Validate amount
    const { minimumAmount, maximumAmount } = STRIPE_PRODUCTS.donations;
    if (amountInCents < minimumAmount) {
      throw new Error(`Minimum donation amount is PKR ${minimumAmount / 100}`);
    }
    if (amountInCents > maximumAmount) {
      throw new Error(`Maximum donation amount is PKR ${maximumAmount / 100}`);
    }

    // Create payment intent via Node.js backend
    const response = await fetch(`${STRIPE_CONFIG.backendUrl}/api/create-payment-intent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        amount: amountInCents,
        currency: currency.toLowerCase(),
        purpose,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || error.message || 'Failed to create payment intent');
    }

    const { clientSecret } = await response.json();
    return clientSecret;
  } catch (error: any) {
    console.error('Stripe payment intent creation failed:', error);
    throw new Error(getStripeErrorMessage(error.code, error.type));
  }
}


// Record completed money donation after Stripe confirmation
export async function recordMoneyDonation(data: Omit<MoneyDonation, 'id' | 'createdAt' | 'uid'> & { 
  amount: number; 
  currency?: string;
  stripePaymentId?: string;
  stripeSessionId?: string;
}): Promise<string> {
  const uid = auth.currentUser?.uid;
  if (!uid) throw new Error('Not authenticated');
  const id = push(ref(database, `money_donations/${uid}`)).key!;
  const payload: MoneyDonation = {
    id,
    uid,
    amount: data.amount,
    currency: data.currency ?? 'PKR',
    purpose: data.purpose,
    createdAt: Date.now(),
    ...(data.receiptUrl && { receiptUrl: data.receiptUrl }),
    ...(data.stripePaymentId && { stripePaymentId: data.stripePaymentId }),
    ...(data.stripeSessionId && { stripeSessionId: data.stripeSessionId }),
  };
  await set(ref(database, `money_donations/${uid}/${id}`), payload);
  return id;
}

export async function listMyMoneyDonations(uid?: string): Promise<MoneyDonation[]> {
  const userId = uid ?? auth.currentUser?.uid;
  if (!userId) return [];
  const snap = await get(ref(database, `money_donations/${userId}`));
  if (!snap.exists()) return [];
  return Object.values(snap.val());
}


