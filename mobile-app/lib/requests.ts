import { auth, database } from '@/database/firebase';
import { get, push, query, ref, set } from 'firebase/database';
import { createDonationRecord } from './donations';
import { BloodRequest } from './types';

function stripUndefined<T extends Record<string, unknown>>(obj: T): T {
  const cleaned = Object.fromEntries(
    Object.entries(obj).filter(([, v]) => v !== undefined)
  ) as T;
  return cleaned;
}

export async function postRequest(payload: Omit<BloodRequest, 'id' | 'status' | 'createdAt' | 'createdBy'>): Promise<string> {
  const uid = auth.currentUser?.uid;
  if (!uid) throw new Error('Not authenticated');
  const id = push(ref(database, 'requests')).key!;
  const data: BloodRequest = {
    id,
    createdBy: uid,
    status: payload.requestedTo ? 'pending' : 'open',
    createdAt: Date.now(),
    patientName: payload.patientName,
    requiredBloodGroup: payload.requiredBloodGroup,
    city: payload.city,
    gender: payload.gender,
    hospital: payload.hospital,
    locationAddress: (payload as any).locationAddress,
    locationLat: (payload as any).locationLat,
    locationLng: (payload as any).locationLng,
    unitsRequired: payload.unitsRequired,
    neededBy: payload.neededBy,
    notes: payload.notes,
    requestedTo: payload.requestedTo,
    urgent: payload.urgent,
  };
  await set(ref(database, `requests/${id}`), stripUndefined(data));
  return id;
}

export async function listMyRequests(uid?: string): Promise<BloodRequest[]> {
  const userId = uid ?? auth.currentUser?.uid;
  if (!userId) return [];
  const snap = await get(ref(database, 'requests'));
  if (!snap.exists()) return [];
  const all: BloodRequest[] = Object.values(snap.val());
  return all.filter((r) => r.createdBy === userId);
}

export async function getRequestById(id: string): Promise<BloodRequest | null> {
  const snap = await get(ref(database, `requests/${id}`));
  if (!snap.exists()) return null;
  return snap.val() as BloodRequest;
}

export async function getDonorStats(uid: string): Promise<{ totalReceived: number; accepted: number; rejected: number; }>{
  const snap = await get(ref(database, 'requests'));
  if (!snap.exists()) return { totalReceived: 0, accepted: 0, rejected: 0 };
  const all: BloodRequest[] = Object.values(snap.val());
  const mine = all.filter((r) => r.requestedTo === uid);
  const accepted = mine.filter((r) => r.status === 'accepted').length;
  const rejected = mine.filter((r) => r.status === 'rejected').length;
  return { totalReceived: mine.length, accepted, rejected };
}

export async function canAcceptRequest(requestId: string, donorUid?: string): Promise<boolean> {
  const uid = donorUid ?? auth.currentUser?.uid;
  if (!uid) return false;
  
  try {
    // Check if donor is available
    const userSnap = await get(ref(database, `users/${uid}`));
    if (!userSnap.exists()) return false;
    const userProfile = userSnap.val();
    if (!userProfile.available) return false;
    
    // Check request status and permissions
    const requestSnap = await get(ref(database, `requests/${requestId}`));
    if (!requestSnap.exists()) return false;
    const request = requestSnap.val() as BloodRequest;
    
    // Check if request is still available for acceptance
    if (request.status !== 'open' && request.status !== 'pending') return false;
    
    // Check if donor is targeted (for pending requests)
    if (request.status === 'pending' && request.requestedTo !== uid) return false;
    
    return true;
  } catch (error) {
    console.error('Error checking if request can be accepted:', error);
    return false;
  }
}

export async function getAcceptableRequests(donorUid?: string): Promise<BloodRequest[]> {
  const uid = donorUid ?? auth.currentUser?.uid;
  if (!uid) return [];
  
  try {
    // Check if donor is available
    const userSnap = await get(ref(database, `users/${uid}`));
    if (!userSnap.exists()) return [];
    const userProfile = userSnap.val();
    if (!userProfile.available) return [];
    
    // Get all requests
    const snap = await get(ref(database, 'requests'));
    if (!snap.exists()) return [];
    const all: BloodRequest[] = Object.values(snap.val() as Record<string, BloodRequest>);
    
    // Filter acceptable requests
    return all.filter((request) => {
      // Only open requests or pending requests targeted to this donor
      if (request.status === 'open') return true;
      if (request.status === 'pending' && request.requestedTo === uid) return true;
      return false;
    }).sort((a, b) => b.createdAt - a.createdAt);
  } catch (error) {
    console.error('Error getting acceptable requests:', error);
    return [];
  }
}

export async function acceptRequest(requestId: string, donorUid?: string): Promise<void> {
  const uid = donorUid ?? auth.currentUser?.uid;
  if (!uid) throw new Error('Not authenticated');
  
  // Validate that donor can accept this request
  const canAccept = await canAcceptRequest(requestId, uid);
  if (!canAccept) {
    throw new Error('You must be available to accept blood requests');
  }
  
  const snap = await get(ref(database, `requests/${requestId}`));
  if (!snap.exists()) throw new Error('Request not found');
  const current = snap.val() as BloodRequest;
  
  const isOpen = current.status === 'open';
  const isPendingTargetedToMe = current.status === 'pending' && current.requestedTo === uid;
  if (!isOpen && !isPendingTargetedToMe) {
    throw new Error('Not allowed to accept this request');
  }
  
  const now = Date.now();
  const updated: BloodRequest = {
    ...current,
    status: 'accepted',
    requestedTo: current.requestedTo ?? uid,
    acceptedAt: now,
    acceptedBy: uid,
  };
  
  await set(ref(database, `requests/${requestId}`), stripUndefined(updated as unknown as Record<string, unknown>) as unknown as BloodRequest);
  
  // Automatically create donation record when accepting request
  await createDonationRecord(requestId, uid);
}

export async function updateRequestStatus(requestId: string, status: BloodRequest['status'], donorUid?: string): Promise<void> {
  const uid = donorUid ?? auth.currentUser?.uid;
  if (!uid) throw new Error('Not authenticated');
  
  const snap = await get(ref(database, `requests/${requestId}`));
  if (!snap.exists()) throw new Error('Request not found');
  const current = snap.val() as BloodRequest;
  
  // Validate permissions based on status change
  if (status === 'accepted') {
    const canAccept = await canAcceptRequest(requestId, uid);
    if (!canAccept) {
      throw new Error('You must be available to accept blood requests');
    }
  }
  
  const now = Date.now();
  const updated: BloodRequest = {
    ...current,
    status,
    ...(status === 'accepted' && {
      requestedTo: current.requestedTo ?? uid,
      acceptedAt: now,
      acceptedBy: uid,
    }),
  };
  
  await set(ref(database, `requests/${requestId}`), stripUndefined(updated as unknown as Record<string, unknown>) as unknown as BloodRequest);
  
  // Create donation record if accepting
  if (status === 'accepted') {
    await createDonationRecord(requestId, uid);
  }
}

export async function rejectRequest(id: string): Promise<void> {
  const uid = auth.currentUser?.uid;
  if (!uid) throw new Error('Not authenticated');
  const snap = await get(ref(database, `requests/${id}`));
  if (!snap.exists()) throw new Error('Request not found');
  const current = snap.val() as BloodRequest;
  // Only targeted donor may reject targeted (pending) requests
  const isTargetedToMe = current.status === 'pending' && current.requestedTo === uid;
  if (!isTargetedToMe) {
    throw new Error('Only the targeted donor can reject this request');
  }
  const updated: BloodRequest = {
    ...current,
    status: 'rejected',
    requestedTo: current.requestedTo,
  };
  await set(ref(database, `requests/${id}`), stripUndefined(updated as unknown as Record<string, unknown>) as unknown as BloodRequest);
}

export async function cancelRequest(id: string): Promise<void> {
  const uid = auth.currentUser?.uid;
  if (!uid) throw new Error('Not authenticated');
  const snap = await get(ref(database, `requests/${id}`));
  if (!snap.exists()) throw new Error('Request not found');
  const current = snap.val() as BloodRequest;
  if (current.createdBy !== uid) {
    throw new Error('Only the creator can cancel this request');
  }
  if (current.status === 'accepted') {
    throw new Error('Cannot cancel request that has been accepted');
  }
  const updated: BloodRequest = { ...current, status: 'cancelled' };
  await set(ref(database, `requests/${id}`), stripUndefined(updated as unknown as Record<string, unknown>) as unknown as BloodRequest);
}

export async function canCancelRequest(requestId: string): Promise<boolean> {
  const uid = auth.currentUser?.uid;
  if (!uid) return false;
  const snap = await get(ref(database, `requests/${requestId}`));
  if (!snap.exists()) return false;
  const current = snap.val() as BloodRequest;
  
  // Check if user is the creator
  if (current.createdBy !== uid) return false;
  
  // Check if request is already accepted
  if (current.status === 'accepted') return false;
  
  // Check if within 10 minutes (600000 milliseconds)
  const now = Date.now();
  const tenMinutesAgo = now - (10 * 60 * 1000);
  if (current.createdAt < tenMinutesAgo) return false;
  
  return true;
}

export async function markFulfilled(id: string): Promise<void> {
  const uid = auth.currentUser?.uid;
  if (!uid) throw new Error('Not authenticated');
  const snap = await get(ref(database, `requests/${id}`));
  if (!snap.exists()) throw new Error('Request not found');
  const current = snap.val() as BloodRequest;
  if (current.createdBy !== uid) {
    throw new Error('Only the creator can mark this request as fulfilled');
  }
  const updated: BloodRequest = { ...current, status: 'fulfilled' };
  await set(ref(database, `requests/${id}`), stripUndefined(updated as unknown as Record<string, unknown>) as unknown as BloodRequest);
}

export type ListRequestsFilters = {
  status?: BloodRequest['status'] | BloodRequest['status'][];
  city?: string;
  requiredBloodGroup?: string;
  createdBy?: string;
  requestedTo?: string;
  mineOnly?: boolean; // requests I created
  toMeOnly?: boolean; // targeted to me
  openOnly?: boolean; // status === 'open'
  urgentOnly?: boolean; // urgent === true
};

export async function listRequests(filters: ListRequestsFilters = {}): Promise<BloodRequest[]> {
  // For now, fetch all and filter client-side as per Project.md guidance
  const uid = auth.currentUser?.uid ?? undefined;
  const snap = await get(query(ref(database, 'requests')));
  if (!snap.exists()) return [];
  let items: BloodRequest[] = Object.values(snap.val() as Record<string, BloodRequest>);

  if (filters.status) {
    const statuses = Array.isArray(filters.status) ? filters.status : [filters.status];
    items = items.filter((r) => statuses.includes(r.status));
  }
  if (filters.city) items = items.filter((r) => r.city === filters.city);
  if (filters.requiredBloodGroup)
    items = items.filter((r) => r.requiredBloodGroup === filters.requiredBloodGroup);
  if (filters.createdBy) items = items.filter((r) => r.createdBy === filters.createdBy);
  if (filters.requestedTo) items = items.filter((r) => r.requestedTo === filters.requestedTo);
  if (filters.mineOnly && uid) items = items.filter((r) => r.createdBy === uid);
  if (filters.toMeOnly && uid) items = items.filter((r) => r.requestedTo === uid);
  if (filters.openOnly) items = items.filter((r) => r.status === 'open');
  if (filters.urgentOnly) items = items.filter((r) => r.urgent === true);

  // Sort newest first
  items.sort((a, b) => b.createdAt - a.createdAt);
  return items;
}

export async function listDonorInbox(): Promise<{ targeted: BloodRequest[]; discoverable: BloodRequest[] }> {
  const uid = auth.currentUser?.uid;
  if (!uid) return { targeted: [], discoverable: [] };
  
  const snap = await get(query(ref(database, 'requests')));
  if (!snap.exists()) return { targeted: [], discoverable: [] };
  const all: BloodRequest[] = Object.values(snap.val() as Record<string, BloodRequest>);
  
  const targeted = all
    .filter((r) => r.requestedTo === uid && r.status === 'pending')
    .sort((a, b) => b.createdAt - a.createdAt);
  
  const discoverable = all
    .filter((r) => r.status === 'open')
    .sort((a, b) => b.createdAt - a.createdAt);
  
  return { targeted, discoverable };
}



