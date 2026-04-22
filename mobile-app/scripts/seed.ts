// Client-side seeder using Firebase Web SDK (no service account).
// Requires a Firebase user with write permissions and permissive DB rules for that user.
import { initializeApp } from 'firebase/app';
import {
    createUserWithEmailAndPassword,
    getAuth,
    inMemoryPersistence,
    setPersistence,
    signInWithEmailAndPassword,
} from 'firebase/auth';
import { getDatabase, push, ref, remove, set, update } from 'firebase/database';

// Configure from env if provided, otherwise fall back to project defaults.
const firebaseConfig = {
  apiKey: process.env.FIREBASE_API_KEY || 'AIzaSyDBKr5eE4TV-uget7xQsUko5UxzXJ1M66Y',
  authDomain: process.env.FIREBASE_AUTH_DOMAIN || 'bloodbank-50357.firebaseapp.com',
  projectId: process.env.FIREBASE_PROJECT_ID || 'bloodbank-50357',
  databaseURL:
    process.env.FIREBASE_DATABASE_URL || 'https://bloodbank-50357-default-rtdb.firebaseio.com',
  storageBucket:
    process.env.FIREBASE_STORAGE_BUCKET || 'bloodbank-50357.firebasestorage.app',
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID || '573555262048',
  appId: process.env.FIREBASE_APP_ID || '1:573555262048:web:a8c4b8231c3c52c17e7905',
};

const SEED_EMAIL = process.env.SEED_EMAIL || 'donar@gmail.com';
const SEED_PASSWORD = process.env.SEED_PASSWORD || '123456';

async function main() {
  if (!SEED_EMAIL || !SEED_PASSWORD) {
    throw new Error('Missing SEED_EMAIL/SEED_PASSWORD env vars for client seeding.');
  }

  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  const database = getDatabase(app);
  await setPersistence(auth, inMemoryPersistence);
  try {
    await signInWithEmailAndPassword(auth, SEED_EMAIL, SEED_PASSWORD);
  } catch (e: any) {
    // If user doesn't exist yet, create it; if wrong password, create a throwaway temp account
    const code = e?.code ?? '';
    if (code === 'auth/user-not-found') {
      await createUserWithEmailAndPassword(auth, SEED_EMAIL, SEED_PASSWORD);
    } else if (code === 'auth/invalid-credential' || code === 'auth/wrong-password') {
      const tmpEmail = `seed_${Date.now()}@example.com`;
      await createUserWithEmailAndPassword(auth, tmpEmail, SEED_PASSWORD);
      console.log(`Created temporary seed user: ${tmpEmail}`);
    } else if (code === 'auth/operation-not-allowed') {
      throw new Error('Enable Email/Password provider in Firebase Authentication settings.');
    } else {
      throw e;
    }
  }

  // Destructive refresh of all app roots used by the client per Project.md
  console.log('Clearing existing data...');
  await Promise.all([
    remove(ref(database, 'users')),
    remove(ref(database, 'requests')),
    remove(ref(database, 'donations')),
    remove(ref(database, 'money_donations')),
    remove(ref(database, 'comments')),
    remove(ref(database, 'organizations')),
    remove(ref(database, 'drives')),
    remove(ref(database, 'user_requests')),
    remove(ref(database, 'donor_requests')),
    remove(ref(database, 'open_requests')),
  ]);
  console.log('Existing data cleared. Seeding dataset...');

  const now = Date.now();
  const oneDay = 24 * 60 * 60 * 1000;
  const threeDays = 3 * oneDay;
  const sevenDays = 7 * oneDay;

  // Users: 1 Patient (Karachi) + 6 Donors across cities, varied blood groups and genders
  const uPatient = {
    uid: 'u_patient',
    name: 'Ayesha Khan',
    email: 'ayesha.khan@example.com',
    gender: 'Female',
    bloodGroup: 'A+',
    city: 'Karachi',
    phone: '+923001112223',
    cnic: '35202-1234567-1',
    available: false,
  };
  const donors = [
    { uid: 'u_d1', name: 'Ali Raza', email: 'ali.raza@example.com', gender: 'Male', bloodGroup: 'O+', city: 'Lahore', phone: '+923101112223', available: true },
    { uid: 'u_d2', name: 'Sara Ahmed', email: 'sara.ahmed@example.com', gender: 'Female', bloodGroup: 'A-', city: 'Karachi', phone: '+923121112223', available: true },
    { uid: 'u_d3', name: 'Bilal Hussain', email: 'bilal.hussain@example.com', gender: 'Male', bloodGroup: 'B+', city: 'Islamabad', phone: '+923131112223', available: false },
    { uid: 'u_d4', name: 'Noor Fatima', email: 'noor.fatima@example.com', gender: 'Female', bloodGroup: 'AB-', city: 'Karachi', phone: '+923141112223', available: true },
    { uid: 'u_d5', name: 'Hamza Ali', email: 'hamza.ali@example.com', gender: 'Male', bloodGroup: 'O-', city: 'Lahore', phone: '+923151112223', available: true },
    { uid: 'u_d6', name: 'Hina Iqbal', email: 'hina.iqbal@example.com', gender: 'Female', bloodGroup: 'A+', city: 'Islamabad', phone: '+923161112223', available: false },
  ];

  const allUsers = [uPatient, ...donors];
  for (const u of allUsers) {
    await set(ref(database, `users/${u.uid}`), {
      ...u,
      createdAt: now,
      updatedAt: now,
    });
  }



  // Requests: 1 open general (city matches patient), 1 targeted pending, 1 accepted
  const requestsRef = ref(database, 'requests');
  const createRequest = async (data: any) => {
    const rRef = push(requestsRef);
    const id = rRef.key!;
    await set(rRef, { id, createdAt: now, ...data });
    return id;
  };

  const reqOpenId = await createRequest({
    createdBy: uPatient.uid,
    patientName: 'Ayesha Khan',
    requiredBloodGroup: 'A+',
    city: 'Karachi',
    gender: 'Female',
    hospital: 'Karachi General Hospital',
    locationAddress: 'Karachi, Pakistan',
    unitsRequired: 2,
    notes: 'Urgent requirement',
    status: 'open',
  });
  const reqPendingId = await createRequest({
    createdBy: uPatient.uid,
    patientName: 'Ayesha Khan',
    requiredBloodGroup: 'A+',
    city: 'Karachi',
    gender: 'Female',
    hospital: 'Karachi General Hospital',
    unitsRequired: 1,
    requestedTo: 'u_d2',
    status: 'pending',
  });
  const reqAcceptedId = await createRequest({
    createdBy: uPatient.uid,
    patientName: 'Ayesha Khan',
    requiredBloodGroup: 'A+',
    city: 'Karachi',
    gender: 'Female',
    hospital: 'Karachi General Hospital',
    unitsRequired: 1,
    requestedTo: 'u_d4',
    status: 'accepted',
  });

  // Index helpers (optional): user_requests, donor_requests, open_requests
  await update(ref(database), {
    [`user_requests/${uPatient.uid}/${reqOpenId}`]: true,
    [`user_requests/${uPatient.uid}/${reqPendingId}`]: true,
    [`user_requests/${uPatient.uid}/${reqAcceptedId}`]: true,
    [`donor_requests/u_d2/${reqPendingId}`]: true,
    [`donor_requests/u_d4/${reqAcceptedId}`]: true,
    [`open_requests/${reqOpenId}`]: true,
  });

  // Comments: add a few comments on pending and accepted requests
  const addComment = async (requestId: string, uid: string, text: string, createdAt: number) => {
    const cRef = push(ref(database, `comments/${requestId}`));
    const id = cRef.key!;
    await set(cRef, { id, uid, text, createdAt });
  };
  await addComment(reqPendingId, 'u_d2', 'I can donate today after 5 PM.', now - oneDay);
  await addComment(reqPendingId, uPatient.uid, 'Thank you! Please come to AKUH.', now - oneDay + 60000);
  await addComment(reqAcceptedId, 'u_d4', 'Accepted. I am on the way.', now - threeDays);

  // Donations: for accepted donor create a pending or fulfilled intent; also add a few money donations
  const addBloodDonation = async (
    donorUid: string,
    requestId: string,
    status: 'pending' | 'fulfilled',
    date: number
  ) => {
    const dRef = push(ref(database, `donations/${donorUid}`));
    const id = dRef.key!;
    await set(dRef, { id, requestId, status, date });
    return id;
  };
  await addBloodDonation('u_d4', reqAcceptedId, 'pending', now - oneDay);
  // Add a past fulfilled record for history
  const pastReqId = await createRequest({
    createdBy: uPatient.uid,
    patientName: 'Hassan Ali',
    requiredBloodGroup: 'O+',
    city: 'Lahore',
    gender: 'Male',
    hospital: 'Lahore General Hospital',
    unitsRequired: 2,
    requestedTo: 'u_d5',
    status: 'fulfilled',
    createdAt: now - sevenDays,
  });
  await update(ref(database), {
    [`user_requests/${uPatient.uid}/${pastReqId}`]: true,
    [`donor_requests/u_d5/${pastReqId}`]: true,
  });
  await addBloodDonation('u_d5', pastReqId, 'fulfilled', now - sevenDays);

  // Money donations across 2 users
  const addMoneyDonation = async (
    uid: string,
    amount: number,
    currency: string,
    purpose: string | undefined,
    createdAt: number,
    receiptUrl?: string
  ) => {
    const mRef = push(ref(database, `money_donations/${uid}`));
    const id = mRef.key!;
    const record: any = { id, uid, amount, currency, createdAt };
    if (purpose !== undefined) {
      record.purpose = purpose;
    }
    if (receiptUrl !== undefined) {
      record.receiptUrl = receiptUrl;
    }
    await set(mRef, record);
  };
  await addMoneyDonation('u_d2', 500, 'PKR', 'Support patient transport', now - threeDays);
  await addMoneyDonation('u_d2', 1000, 'PKR', undefined, now - oneDay, 'https://example.com/receipt/1000');
  await addMoneyDonation('u_d4', 2500, 'PKR', 'Hospital supplies', now - oneDay);
  await addMoneyDonation('u_d4', 800, 'PKR', undefined, now);

  console.log('Seeding complete');
}

// eslint-disable-next-line @typescript-eslint/no-floating-promises
main().catch((e) => {
  console.error('Seeding failed:', e?.message ?? e);
  process.exit(1);
});


