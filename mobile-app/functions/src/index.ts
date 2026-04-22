import * as admin from 'firebase-admin';
import * as functions from 'firebase-functions';

// Initialize Firebase Admin
admin.initializeApp();

// Firebase function to handle donation payment processing
export const processDonationPayment = functions.https.onCall(async (data, context) => {
  // Verify authentication
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }

  const { requestId, donorUid, amount, currency = 'PKR' } = data;

  // Validate required fields
  if (!requestId || !donorUid || !amount) {
    throw new functions.https.HttpsError('invalid-argument', 'Missing required fields');
  }

  try {
    // Create donation record
    const donationRef = admin.database().ref(`donations/${donorUid}`).push();
    const donationId = donationRef.key;

    const donationData = {
      id: donationId,
      requestId,
      status: 'pending',
      date: Date.now(),
      amount,
      currency,
    };

    await donationRef.set(donationData);

    // Update request status to accepted
    await admin.database().ref(`requests/${requestId}`).update({
      status: 'accepted',
      requestedTo: donorUid,
      updatedAt: Date.now(),
    });

    return {
      success: true,
      donationId,
      message: 'Donation record created successfully',
    };
  } catch (error) {
    console.error('Error processing donation payment:', error);
    throw new functions.https.HttpsError('internal', 'Failed to process donation payment');
  }
});

// Firebase function to update donation status
export const updateDonationStatus = functions.https.onCall(async (data, context) => {
  // Verify authentication
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }

  const { donationId, status, donorUid } = data;

  // Validate required fields
  if (!donationId || !status || !donorUid) {
    throw new functions.https.HttpsError('invalid-argument', 'Missing required fields');
  }

  // Validate status
  const validStatuses = ['pending', 'completed', 'cancelled'];
  if (!validStatuses.includes(status)) {
    throw new functions.https.HttpsError('invalid-argument', 'Invalid status');
  }

  try {
    // Update donation status
    await admin.database().ref(`donations/${donorUid}/${donationId}`).update({
      status,
      updatedAt: Date.now(),
    });

    // If completed, update request status to fulfilled
    if (status === 'completed') {
      const donationSnap = await admin.database().ref(`donations/${donorUid}/${donationId}`).once('value');
      const donation = donationSnap.val();
      
      if (donation && donation.requestId) {
        await admin.database().ref(`requests/${donation.requestId}`).update({
          status: 'fulfilled',
          updatedAt: Date.now(),
        });
      }
    }

    return {
      success: true,
      message: 'Donation status updated successfully',
    };
  } catch (error) {
    console.error('Error updating donation status:', error);
    throw new functions.https.HttpsError('internal', 'Failed to update donation status');
  }
});

// Firebase function to record money donation
export const recordMoneyDonation = functions.https.onCall(async (data, context) => {
  // Verify authentication
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }

  const { amount, currency = 'PKR', purpose, stripePaymentId, receiptUrl } = data;
  const uid = context.auth.uid;

  // Validate required fields
  if (!amount || !stripePaymentId) {
    throw new functions.https.HttpsError('invalid-argument', 'Missing required fields');
  }

  try {
    // Create money donation record
    const donationRef = admin.database().ref(`money_donations/${uid}`).push();
    const donationId = donationRef.key;

    const donationData = {
      id: donationId,
      uid,
      amount,
      currency,
      purpose,
      createdAt: Date.now(),
      receiptUrl,
      stripePaymentId,
    };

    await donationRef.set(donationData);

    return {
      success: true,
      donationId,
      message: 'Money donation recorded successfully',
    };
  } catch (error) {
    console.error('Error recording money donation:', error);
    throw new functions.https.HttpsError('internal', 'Failed to record money donation');
  }
});

// Firebase function to get donation statistics
export const getDonationStats = functions.https.onCall(async (data, context) => {
  // Verify authentication
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }

  const { uid } = data;
  const userId = uid || context.auth.uid;

  try {
    // Get blood donations
    const bloodDonationsSnap = await admin.database().ref(`donations/${userId}`).once('value');
    const bloodDonations = bloodDonationsSnap.val() || {};

    // Get money donations
    const moneyDonationsSnap = await admin.database().ref(`money_donations/${userId}`).once('value');
    const moneyDonations = moneyDonationsSnap.val() || {};

    // Calculate statistics
    const bloodDonationCount = Object.keys(bloodDonations).length;
    const completedBloodDonations = Object.values(bloodDonations).filter(
      (donation: any) => donation.status === 'completed'
    ).length;

    const moneyDonationCount = Object.keys(moneyDonations).length;
    const totalMoneyDonated = Object.values(moneyDonations).reduce(
      (total: number, donation: any) => total + (donation.amount || 0),
      0
    );

    return {
      success: true,
      stats: {
        bloodDonations: {
          total: bloodDonationCount,
          completed: completedBloodDonations,
          pending: bloodDonationCount - completedBloodDonations,
        },
        moneyDonations: {
          total: moneyDonationCount,
          totalAmount: totalMoneyDonated,
        },
      },
    };
  } catch (error) {
    console.error('Error getting donation stats:', error);
    throw new functions.https.HttpsError('internal', 'Failed to get donation statistics');
  }
});