import { auth, database } from '@/database/firebase';
import { get, push, ref, remove, set } from 'firebase/database';
import { Comment } from './types';

export async function addComment(requestId: string, uid: string, text: string): Promise<string> {
  if (!auth.currentUser?.uid) throw new Error('Not authenticated');
  const id = push(ref(database, `comments/${requestId}`)).key!;
  const comment: Comment = {
    id,
    uid,
    text: text.trim(),
    createdAt: Date.now(),
  };
  await set(ref(database, `comments/${requestId}/${id}`), comment);
  return id;
}

export async function listComments(requestId: string): Promise<Comment[]> {
  const snap = await get(ref(database, `comments/${requestId}`));
  if (!snap.exists()) return [];
  const comments: Comment[] = Object.values(snap.val() as Record<string, Comment>);
  return comments.sort((a, b) => a.createdAt - b.createdAt);
}

export async function deleteComment(requestId: string, commentId: string): Promise<void> {
  const uid = auth.currentUser?.uid;
  if (!uid) throw new Error('Not authenticated');
  
  // Get comment to verify ownership
  const commentSnap = await get(ref(database, `comments/${requestId}/${commentId}`));
  if (!commentSnap.exists()) return;
  
  const comment = commentSnap.val() as Comment;
  
  // Get request to check if user is the request creator
  const requestSnap = await get(ref(database, `requests/${requestId}`));
  const request = requestSnap.exists() ? requestSnap.val() : null;
  
  // Only author or request creator can delete
  if (comment.uid !== uid && request?.createdBy !== uid) {
    throw new Error('Not authorized to delete this comment');
  }
  
  await remove(ref(database, `comments/${requestId}/${commentId}`));
}