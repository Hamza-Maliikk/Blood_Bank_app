import SelectModal from '@/components/SelectModal';
import { Colors } from '@/constants/Colors';
import { useThemeCustom } from '@/context/ThemeContext';
import { BLOOD_GROUPS, CITIES_PK, GENDERS } from '@/data/pk';
import { postRequest } from '@/lib/requests';
import { getUserProfile } from '@/lib/users';
import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Switch, Text, TextInput, TouchableOpacity, View } from 'react-native';

export default function RequestBloodScreen() {
	const { theme } = useThemeCustom();
	const isDark = theme === 'dark';
	const params = useLocalSearchParams<{ requestedTo?: string }>();
	const [patientName, setPatientName] = useState('');
	const [bloodGroup, setBloodGroup] = useState('');
	const [city, setCity] = useState('');
	const [gender, setGender] = useState('');
	const [hospital, setHospital] = useState('');
	const [units, setUnits] = useState('');
	const [notes, setNotes] = useState('');
	const [urgent, setUrgent] = useState(false);
	const [openPicker, setOpenPicker] = useState<null | 'gender' | 'city' | 'blood'>(null);
	const requestedTo = typeof params.requestedTo === 'string' ? params.requestedTo : undefined;

	useEffect(() => {
		(async () => {
			const profile = await getUserProfile();
			if (profile) {
				if (!patientName) setPatientName(profile.name ?? '');
				if (!bloodGroup && profile.bloodGroup) setBloodGroup(profile.bloodGroup);
				if (!city && profile.city) setCity(profile.city);
				if (!gender && profile.gender) setGender(profile.gender);
			}
		})();
	}, []);


	const onSubmit = async () => {
		if (!patientName || !bloodGroup || !city) {
			Alert.alert('Missing fields', 'Please fill patient name, blood group and city.');
			return;
		}
		try {
			await postRequest({
				patientName,
				requiredBloodGroup: bloodGroup,
				city,
				gender,
				hospital,
				unitsRequired: units ? Number(units) : undefined,
				notes,
				requestedTo,
				urgent,
			});
			Alert.alert('Posted', 'Your request has been posted.');
			setPatientName('');
			setBloodGroup('');
			setCity('');
			setGender('');
			setHospital('');
			setUnits('');
			setNotes('');
			setUrgent(false);
		} catch (e: any) {
			Alert.alert('Post failed', e?.message ?? 'Could not post request. Are you logged in?');
		}
	};

	return (
		<ScrollView 
			style={[styles.scrollContainer, { backgroundColor: Colors[theme].background }]}
			contentContainerStyle={styles.scrollContent}
			showsVerticalScrollIndicator={false}
			keyboardShouldPersistTaps="handled"
		>
			<Text style={[styles.title, { color: isDark ? '#fff' : Colors[theme].text }]}>Request Blood</Text>
			<TextInput placeholder="Patient Name" placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'} style={[styles.input, { color: isDark ? '#fff' : '#111827', borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} value={patientName} onChangeText={setPatientName} />
			<TouchableOpacity style={[styles.input, { borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} onPress={() => setOpenPicker('blood')}>
				<Text style={{ color: isDark ? (bloodGroup ? '#fff' : '#9CA3AF') : '#111827' }}>{bloodGroup || 'Blood Group'}</Text>
			</TouchableOpacity>
			<TouchableOpacity style={[styles.input, { borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} onPress={() => setOpenPicker('city')}>
				<Text style={{ color: isDark ? (city ? '#fff' : '#9CA3AF') : '#111827' }}>{city || 'City'}</Text>
			</TouchableOpacity>
			<TouchableOpacity style={[styles.input, { borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} onPress={() => setOpenPicker('gender')}>
				<Text style={{ color: isDark ? (gender ? '#fff' : '#9CA3AF') : '#111827' }}>{gender || 'Gender'}</Text>
			</TouchableOpacity>
			<TextInput placeholder="Hospital/Location" placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'} style={[styles.input, { color: isDark ? '#fff' : '#111827', borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} value={hospital} onChangeText={setHospital} />
			<TextInput placeholder="Quantity (units)" placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'} keyboardType="number-pad" style={[styles.input, { color: isDark ? '#fff' : '#111827', borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} value={units} onChangeText={setUnits} />
			<TextInput placeholder="Additional Notes" placeholderTextColor={isDark ? '#9CA3AF' : '#6B7280'} style={[styles.input, styles.textarea, { color: isDark ? '#fff' : '#111827', borderColor: isDark ? '#374151' : '#e5e7eb', backgroundColor: isDark ? '#111827' : '#fff' }]} value={notes} onChangeText={setNotes} multiline />
			
			{/* Urgent Request Toggle */}
			<View style={[styles.urgentToggle, { backgroundColor: isDark ? '#111827' : '#fff', borderColor: isDark ? '#374151' : '#e5e7eb' }]}>
				<View style={styles.urgentToggleContent}>
					<View style={styles.urgentToggleText}>
						<Text style={[styles.urgentLabel, { color: isDark ? '#fff' : '#111827' }]}>Urgent Request</Text>
						<Text style={[styles.urgentDescription, { color: isDark ? '#9CA3AF' : '#6B7280' }]}>Mark as high priority for faster donor matching</Text>
					</View>
					<Switch
						value={urgent}
						onValueChange={setUrgent}
						trackColor={{ false: '#767577', true: '#E11D48' }}
						thumbColor={urgent ? '#fff' : '#f4f3f4'}
					/>
				</View>
			</View>
			
			{requestedTo ? (
				<View style={{ marginTop: 4 }}>
					<Text style={{ color: isDark ? '#D1D5DB' : '#6B7280' }}>Requesting a specific donor</Text>
				</View>
			) : null}
			<TouchableOpacity style={styles.primaryButton} onPress={onSubmit}>
				<Text style={styles.primaryText}>Post Request</Text>
			</TouchableOpacity>

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
		</ScrollView>
	);
}

const styles = StyleSheet.create({
	scrollContainer: { flex: 1 },
	scrollContent: { 
		padding: 16, 
		paddingBottom: 40, 
		gap: 10,
		flexGrow: 1 
	},
	title: { fontSize: 24, fontWeight: '700', marginBottom: 4 },
	input: {
		borderWidth: 1,
		borderColor: '#e5e7eb',
		borderRadius: 10,
		padding: 12,
	},
	textarea: { minHeight: 100, textAlignVertical: 'top' },
	urgentToggle: {
		borderWidth: 1,
		borderRadius: 10,
		padding: 12,
		marginTop: 8,
	},
	urgentToggleContent: {
		flexDirection: 'row',
		alignItems: 'center',
		justifyContent: 'space-between',
	},
	urgentToggleText: {
		flex: 1,
		marginRight: 12,
	},
	urgentLabel: {
		fontSize: 16,
		fontWeight: '600',
		marginBottom: 2,
	},
	urgentDescription: {
		fontSize: 12,
		opacity: 0.7,
	},
	primaryButton: {
		marginTop: 16,
		marginBottom: 8,
		backgroundColor: '#E11D48',
		paddingVertical: 14,
		borderRadius: 12,
		alignItems: 'center',
	},
	primaryText: { color: '#fff', fontWeight: '600' },
});


