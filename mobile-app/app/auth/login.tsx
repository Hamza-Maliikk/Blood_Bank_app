import { Colors } from '@/constants/Colors';
import { useThemeCustom } from '@/context/ThemeContext';
import { auth } from '@/database/firebase';
import { getUserProfile } from '@/lib/users';
import { Image } from 'expo-image';
import { useRouter } from 'expo-router';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { useState } from 'react';
import { ActivityIndicator, Alert, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

export default function LoginScreen() {
	const router = useRouter();
	const { theme } = useThemeCustom();
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [isLoading, setIsLoading] = useState(false);

	const getAuthErrorMessage = (code?: string) => {
		switch (code) {
			case 'auth/invalid-email':
				return 'Please enter a valid email address.';
			case 'auth/missing-password':
				return 'Please enter your password.';
			case 'auth/invalid-credential':
			case 'auth/wrong-password':
				return 'Email or password is incorrect.';
			case 'auth/user-not-found':
				return 'No account found for this email.';
			case 'auth/user-disabled':
				return 'This account has been disabled.';
			case 'auth/too-many-requests':
				return 'Too many attempts. Please try again later.';
			case 'auth/network-request-failed':
				return 'Network error. Check your connection and try again.';
			default:
				return 'Sign in failed. Please try again.';
		}
	};

	const emailSignIn = async () => {
		if (!email.trim()) {
			Alert.alert('Missing email', 'Please enter your email.');
			return;
		}
		if (!password) {
			Alert.alert('Missing password', 'Please enter your password.');
			return;
		}
		
		setIsLoading(true);
		try {
			await signInWithEmailAndPassword(auth, email.trim(), password);
			const profile = await getUserProfile();
			const needsOnboarding = !profile || !profile.name || !profile.bloodGroup || !profile.city;
			router.replace(needsOnboarding ? '/auth/onboarding' : '/(tabs)/home');
		} catch (e: any) {
			const code: string | undefined = e?.code;
			Alert.alert('Login failed', getAuthErrorMessage(code));
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<View style={[styles.container, { backgroundColor: Colors[theme].background }]}>
			<Image source={require('@/assets/images/logo.jpg')} style={{ width: 96, height: 96, borderRadius: 16, alignSelf: 'center', marginBottom: 12 }} />
			<Text style={{ textAlign: 'center', fontSize: 20, fontWeight: '700', marginBottom: 12, color: Colors[theme].text }}>Blood Donation App</Text>
			<View style={[styles.card, { backgroundColor: Colors[theme].cardBackground, borderColor: Colors[theme].border }]}>
			<Text style={[styles.title, { color: Colors[theme].text }]}>Sign in with Email</Text>
			<TextInput
				placeholder="Email"
				placeholderTextColor={Colors[theme].secondaryText}
				keyboardType="email-address"
				style={[styles.input, { 
					color: Colors[theme].text, 
					backgroundColor: Colors[theme].inputBackground, 
					borderColor: Colors[theme].border 
				}]}
				value={email}
				onChangeText={setEmail}
				autoCapitalize="none"
			/>
			<TextInput
				placeholder="Password"
				placeholderTextColor={Colors[theme].secondaryText}
				secureTextEntry
				style={[styles.input, { 
					color: Colors[theme].text, 
					backgroundColor: Colors[theme].inputBackground, 
					borderColor: Colors[theme].border 
				}]}
				value={password}
				onChangeText={setPassword}
			/>
			<TouchableOpacity 
				style={[styles.primaryButton, isLoading && styles.disabledButton]} 
				onPress={emailSignIn}
				disabled={isLoading}
			>
				{isLoading ? (
					<View style={styles.loadingContainer}>
						<ActivityIndicator color="#fff" size="small" />
						<Text style={[styles.primaryText, { marginLeft: 8 }]}>Signing in...</Text>
					</View>
				) : (
					<Text style={styles.primaryText}>Sign in</Text>
				)}
			</TouchableOpacity>

			<View style={{ marginTop: 16, alignItems: 'center', gap: 8 }}>
				<TouchableOpacity onPress={() => router.push('/auth/signup')}>
					<Text style={{ color: Colors[theme].linkText }}>Create an account</Text>
				</TouchableOpacity>
				<TouchableOpacity onPress={() => router.push('/auth/reset')}>
					<Text style={{ color: Colors[theme].linkText }}>Forgot password?</Text>
				</TouchableOpacity>
			</View>
			</View>
		</View>
	);
}

const styles = StyleSheet.create({
	container: { flex: 1, padding: 16, gap: 10, justifyContent: 'center' },
	title: { fontSize: 20, fontWeight: '700', marginBottom: 4, textAlign: 'center' },
	input: {
		borderWidth: 1,
		borderColor: '#e5e7eb',
		borderRadius: 10,
		padding: 12,
	},
	card: {
		backgroundColor: '#fff',
		borderRadius: 14,
		padding: 16,
		gap: 10,
		elevation: 2,
		shadowColor: '#000',
		shadowOpacity: 0.06,
		shadowRadius: 8,
		shadowOffset: { width: 0, height: 2 },
	},
	primaryButton: {
		marginTop: 8,
		backgroundColor: '#E11D48',
		paddingVertical: 14,
		borderRadius: 12,
		alignItems: 'center',
	},
	primaryText: { color: '#fff', fontWeight: '600' },
	disabledButton: {
		opacity: 0.7,
	},
	loadingContainer: {
		flexDirection: 'row',
		alignItems: 'center',
		justifyContent: 'center',
	},
});


