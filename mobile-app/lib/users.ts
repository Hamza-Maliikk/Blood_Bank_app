import { auth, database } from '@/database/firebase';
import { child, get, ref, update } from 'firebase/database';
import { UserProfile } from './types';

function pathSafeKey(key: string): string {
  return key.replace(/[.#$/\[\]]/g, '_');
}

function stripUndefined<T extends Record<string, unknown>>(obj: T): T {
  return Object.fromEntries(
    Object.entries(obj).filter(([, v]) => v !== undefined)
  ) as T;
}

export async function saveUserProfile(partial: Partial<UserProfile>): Promise<void> {
  const uid = auth.currentUser?.uid;
  if (!uid) throw new Error('Not authenticated');
  const now = Date.now();
  const key = pathSafeKey(uid);
  const existingSnap = await get(child(ref(database, 'users'), key));
  const current: Partial<UserProfile> = existingSnap.exists() ? (existingSnap.val() as UserProfile) : {};
  const profile: UserProfile = {
    uid,
    name: partial.name ?? current.name ?? '',
    email: partial.email ?? current.email,
    gender: partial.gender ?? current.gender,
    bloodGroup: partial.bloodGroup ?? current.bloodGroup,
    city: partial.city ?? current.city,
    cnic: partial.cnic ?? current.cnic,
    phone: partial.phone ?? current.phone,
    available: partial.available ?? (current.available ?? true),
    mode: partial.mode ?? current.mode ?? 'patient',
    themePreference: partial.themePreference ?? current.themePreference,
    createdAt: (current.createdAt as number) ?? now,
    updatedAt: now,
  };
  // Remove undefined values; update() rejects objects containing undefined
  const cleaned = stripUndefined(profile) as unknown as Record<string, unknown>;
  await update(ref(database), { [`users/${key}`]: cleaned });
}

export async function getUserProfile(uid?: string): Promise<UserProfile | null> {
  const id = uid ?? auth.currentUser?.uid;
  if (!id) return null;
  const key = pathSafeKey(id);
  const snap = await get(child(ref(database, 'users'), key));
  if (!snap.exists()) return null;
  return snap.val() as UserProfile;
}

export async function listAvailableDonors(): Promise<UserProfile[]> {
  // Prefer a simple fetch + filter to be resilient to legacy data types (e.g., 'true' strings)
  const snap = await get(ref(database, 'users'));
  if (!snap.exists()) return [];
  const all = Object.values(snap.val() as Record<string, UserProfile | undefined>)
    .filter(Boolean) as UserProfile[];
  return all.filter((u) => (u as any)?.available === true || (u as any)?.available === 'true');
}


export async function listAllUsers(): Promise<UserProfile[]> {
  const snap = await get(ref(database, 'users'));
  if (!snap.exists()) return [];
  const all = Object.values(snap.val() as Record<string, UserProfile | undefined>)
    .filter(Boolean) as UserProfile[];
  return all;
}

export async function setAvailability(available: boolean): Promise<void> {
  const uid = auth.currentUser?.uid;
  if (!uid) throw new Error('Not authenticated');
  const key = pathSafeKey(uid);
  const now = Date.now();
  await update(ref(database), {
    [`users/${key}/available`]: available,
    [`users/${key}/updatedAt`]: now,
  });
}


