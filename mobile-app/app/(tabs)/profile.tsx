import SelectModal from '@/components/SelectModal';
import { Colors } from '@/constants/Colors';
import { useMode } from '@/context/ModeContext';
import { useThemeCustom } from '@/context/ThemeContext';
import { BLOOD_GROUPS, CITIES_PK, GENDERS } from '@/data/pk';
import { auth } from '@/database/firebase';
import { getDonorStats } from '@/lib/requests';
import { getUserProfile, saveUserProfile, setAvailability } from '@/lib/users';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { signOut } from 'firebase/auth';
import { useEffect, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Switch, Text, TextInput, TouchableOpacity, View } from 'react-native';

export default function ProfileScreen() {
	const router = useRouter();
	const { theme, mode: themeMode, setMode: setThemeMode } = useThemeCustom();
	const isDark = theme === 'dark';
	const { mode, toggleMode } = useMode();
	const [name, setName] = useState('');
	const [email, setEmail] = useState('');
	const [gender, setGender] = useState('');
	const [bloodGroup, setBloodGroup] = useState('');
	const [city, setCity] = useState('');
	const [phone, setPhone] = useState('+92');
	const [cnic, setCnic] = useState('');
	const [available, setAvailable] = useState(true);
	const [openPicker, setOpenPicker] = useState<null | 'gender' | 'city' | 'blood' | 'theme'>(null);
	const [donationsAccepted, setDonationsAccepted] = useState<number>(0);

	const normalizePhone = (value: string) => {
		if (!value.startsWith('+92')) return '+92';
		const digits = value.replace(/[^\d+]/g, '');
		return digits.slice(0, 13);
	};

	useEffect(() => {
		(async () => {
			const profile = await getUserProfile();
			if (profile) {
				setName(profile.name ?? '');
				setEmail(profile.email ?? '');
				setGender(profile.gender ?? '');
				setBloodGroup(profile.bloodGroup ?? '');
				setCity(profile.city ?? '');
				setPhone(profile.phone ?? '+92');
				setCnic(profile.cnic ?? '');
				setAvailable(profile.available ?? true);
				const stats = await getDonorStats(profile.uid);
				setDonationsAccepted(stats.accepted);
			}
		})();
	}, []);

	const onSave = async () => {
		await saveUserProfile({ name, email, gender, bloodGroup, city, phone, cnic, available });
		Alert.alert('Saved', 'Profile updated');
	};

	const onToggleAvailability = async (val: boolean) => {
		setAvailable(val);
		try {
			await setAvailability(val);
		} catch (e) {
			setAvailable(!val);
		}
	};

	const onLogout = async () => {
		Alert.alert('Logout', 'Are you sure you want to logout?', [
			{ text: 'Cancel', style: 'cancel' },
			{
				text: 'Logout',
				style: 'destructive',
				onPress: async () => {
					try {
						await signOut(auth);
						router.replace('/auth/login');
					} catch (e: any) {
						Alert.alert('Logout failed', e?.message ?? 'Try again');
					}
				},
			},
		]);
	};

	const getThemeDisplayName = (mode: string) => {
		switch (mode) {
			case 'light': return 'Light';
			case 'dark': return 'Dark';
			default: return 'System';
		}
	};

	return (
		<ScrollView style={[styles.container, { backgroundColor: Colors[theme].background }]} showsVerticalScrollIndicator={false}>
			{/* My Profile Section */}
			<View style={styles.section}>
				<Text style={[styles.sectionTitle, { color: isDark ? '#fff' : Colors[theme].text }]}>My Profile</Text>
				
				<TextInput placeholder="Full Name" placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'} style={[styles.input, { color: isDark ? '#fff' : '#111827', borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} value={name} onChangeText={setName} />
				<TextInput placeholder="Email" placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'} style={[styles.input, styles.inputDisabled, { color: isDark ? '#fff' : '#111827', borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#f3f4f6' }]} value={email} onChangeText={setEmail} editable={false} />
				
				<TouchableOpacity style={[styles.input, { borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} onPress={() => setOpenPicker('gender')}>
					<Text style={{ color: isDark ? (gender ? '#fff' : '#9CA3AF') : '#111827' }}>{gender || 'Gender'}</Text>
				</TouchableOpacity>
				
				<TouchableOpacity style={[styles.input, { borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} onPress={() => setOpenPicker('blood')}>
					<Text style={{ color: isDark ? (bloodGroup ? '#fff' : '#9CA3AF') : '#111827' }}>{bloodGroup || 'Blood Group'}</Text>
				</TouchableOpacity>
				
				<TouchableOpacity style={[styles.input, { borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} onPress={() => setOpenPicker('city')}>
					<Text style={{ color: isDark ? (city ? '#fff' : '#9CA3AF') : '#111827' }}>{city || 'City'}</Text>
				</TouchableOpacity>
				
				<TextInput placeholder="Phone (+92...)" placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'} style={[styles.input, { color: isDark ? '#fff' : '#111827', borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} value={phone} onChangeText={(v)=>setPhone(normalizePhone(v))} keyboardType="phone-pad" />
				<TextInput placeholder="CNIC (optional)" placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'} style={[styles.input, { color: isDark ? '#fff' : '#111827', borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} value={cnic} onChangeText={setCnic} />
				
				<View style={styles.statsRow}>
					<View style={styles.statItem}>
						<Text style={[styles.statLabel, { color: isDark ? '#9CA3AF' : '#6B7280' }]}>Times Donated</Text>
						<Text style={[styles.statValue, { color: isDark ? '#fff' : '#111827' }]}>{donationsAccepted}</Text>
					</View>
				</View>

				<TouchableOpacity style={styles.primaryButton} onPress={onSave}>
					<Ionicons name="save" size={20} color="#fff" />
					<Text style={styles.primaryText}>Save Profile</Text>
				</TouchableOpacity>
			</View>

			{/* Settings Section */}
			<View style={styles.section}>
				<Text style={[styles.sectionTitle, { color: Colors[theme].text }]}>Settings</Text>
				
				{/* Availability Toggle - Only for Donors */}
				{mode === 'donor' && (
					<View style={[styles.settingRow, { borderBottomColor: isDark ? '#374151' : '#e5e7eb' }]}>
						<View style={styles.settingInfo}>
							<Ionicons name="radio-button-on" size={20} color={available ? '#10B981' : '#6B7280'} />
							<View>
							<Text style={[styles.settingLabel, { color: Colors[theme].text }]}>Availability</Text>
							<Text style={[styles.settingSubtext, { color: Colors[theme].secondaryText }]}>Others can find and contact you</Text>
							</View>
						</View>
						<Switch value={available} onValueChange={onToggleAvailability} />
					</View>
				)}

				<View style={[styles.settingRow, { borderBottomColor: isDark ? '#374151' : '#e5e7eb' }]}>
					<View style={styles.settingInfo}>
						<Ionicons name="person-circle" size={20} color="#E11D48" />
						<View>
						<Text style={[styles.settingLabel, { color: Colors[theme].text }]}>Mode</Text>
						<Text style={[styles.settingSubtext, { color: Colors[theme].secondaryText }]}>Switch between Donor and Patient</Text>
						</View>
					</View>
					<TouchableOpacity onPress={toggleMode} style={[styles.modeButton, { backgroundColor: mode === 'donor' ? '#10B981' : '#3B82F6' }]}>
						<Text style={styles.modeButtonText}>{mode === 'donor' ? 'Donor' : 'Patient'}</Text>
					</TouchableOpacity>
				</View>

				<TouchableOpacity style={[styles.settingRow, { borderBottomColor: isDark ? '#374151' : '#e5e7eb' }]} onPress={() => setOpenPicker('theme')}>
					<View style={styles.settingInfo}>
						<Ionicons name="contrast" size={20} color="#8B5CF6" />
						<View>
						<Text style={[styles.settingLabel, { color: Colors[theme].text }]}>Theme</Text>
						<Text style={[styles.settingSubtext, { color: Colors[theme].secondaryText }]}>{getThemeDisplayName(themeMode)}</Text>
						</View>
					</View>
					<Ionicons name="chevron-forward" size={20} color={isDark ? '#9CA3AF' : '#6B7280'} />
				</TouchableOpacity>

				<TouchableOpacity style={[styles.settingRow, { borderBottomWidth: 0 }]} onPress={onLogout}>
					<View style={styles.settingInfo}>
						<Ionicons name="log-out" size={20} color="#EF4444" />
						<Text style={[styles.settingLabel, { color: '#EF4444' }]}>Logout</Text>
					</View>
					<Ionicons name="chevron-forward" size={20} color="#EF4444" />
				</TouchableOpacity>
			</View>

			<SelectModal
				visible={openPicker === 'gender'}
				title="Select Gender"
				options={GENDERS}
				onClose={() => setOpenPicker(null)}
				onSelect={(v) => { setGender(v); setOpenPicker(null); }}
			/>
			<SelectModal
				visible={openPicker === 'city'}
				title="Select City"
				options={CITIES_PK}
				onClose={() => setOpenPicker(null)}
				onSelect={(v) => { setCity(v); setOpenPicker(null); }}
			/>
			<SelectModal
				visible={openPicker === 'blood'}
				title="Select Blood Group"
				options={BLOOD_GROUPS}
				onClose={() => setOpenPicker(null)}
				onSelect={(v) => { setBloodGroup(v); setOpenPicker(null); }}
			/>
			<SelectModal
				visible={openPicker === 'theme'}
				title="Select Theme"
				options={['System', 'Light', 'Dark']}
				onClose={() => setOpenPicker(null)}
				onSelect={(v) => { 
					const mode = v.toLowerCase() as 'system' | 'light' | 'dark';
					setThemeMode(mode); 
					setOpenPicker(null); 
				}}
			/>
		</ScrollView>
	);
}

const styles = StyleSheet.create({
	container: { flex: 1, padding: 16 },
	section: { marginBottom: 32 },
	sectionTitle: { fontSize: 24, fontWeight: '700' as const, marginBottom: 16 },
	input: {
		borderWidth: 1,
		borderColor: '#e5e7eb',
		borderRadius: 10,
		padding: 12,
		marginBottom: 12,
	},
	inputDisabled: { backgroundColor: '#f3f4f6' },
	statsRow: { marginVertical: 16 },
	statItem: { alignItems: 'center' as const },
	statLabel: { fontSize: 14, fontWeight: '600' as const, marginBottom: 4 },
	statValue: { fontSize: 24, fontWeight: '700' as const },
	primaryButton: {
		flexDirection: 'row' as const,
		alignItems: 'center' as const,
		justifyContent: 'center' as const,
		gap: 8,
		backgroundColor: '#E11D48',
		paddingVertical: 14,
		borderRadius: 12,
		marginTop: 16,
	},
	primaryText: { color: '#fff', fontWeight: '600' as const, fontSize: 16 },
	settingRow: {
		flexDirection: 'row' as const,
		alignItems: 'center' as const,
		justifyContent: 'space-between' as const,
		paddingVertical: 16,
		borderBottomWidth: 1,
	},
	settingInfo: { flexDirection: 'row' as const, alignItems: 'center' as const, gap: 12, flex: 1 },
	settingLabel: { fontSize: 16, fontWeight: '600' as const },
	settingSubtext: { fontSize: 14, marginTop: 2 },
	modeButton: {
		paddingVertical: 6,
		paddingHorizontal: 12,
		borderRadius: 16,
	},
	modeButtonText: { color: '#fff', fontWeight: '600' as const, fontSize: 14 },
});


