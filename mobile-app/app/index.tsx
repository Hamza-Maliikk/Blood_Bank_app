import { auth } from '@/database/firebase';
import { Redirect } from 'expo-router';

export default function Index() {
	const isLoggedIn = !!auth.currentUser;
	return <Redirect href={isLoggedIn ? '/(tabs)/home' : '/auth/login'} />;
}
