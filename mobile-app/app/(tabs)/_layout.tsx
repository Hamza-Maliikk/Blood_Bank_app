import { Colors } from '@/constants/Colors';
import { useMode } from '@/context/ModeContext';
import { useThemeCustom } from '@/context/ThemeContext';
import { auth } from '@/database/firebase';
import { setAvailability } from '@/lib/users';
import { Ionicons } from '@expo/vector-icons';
import type { BottomTabBarProps } from '@react-navigation/bottom-tabs';
import { BottomTabBar } from '@react-navigation/bottom-tabs';
import { Redirect, Tabs } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { Dimensions, Image, Platform, Switch, Text, TouchableOpacity, View } from 'react-native';

// CustomTabBar component for mode-based filtering
type CustomTabBarProps = BottomTabBarProps & {
	mode: "donor" | "patient" | string;
};

function CustomTabBar({ state, descriptors, navigation, mode, ...rest }: CustomTabBarProps) {
	// which route names should be visible for each mode
	const visibleNames = useMemo(() => {
		if (mode === "donor") {
			return new Set(["home", "inbox", "donate", "history", "profile"]);
		}
		// patient (or default)
		return new Set(["home", "donors", "request", "donate", "history", "profile"]);
	}, [mode]);

	// filter routes + descriptors
	const filteredRoutes = state.routes.filter((r) => visibleNames.has(r.name));
	const filteredDescriptors = filteredRoutes.reduce<Record<string, any>>((acc, r) => {
		acc[r.key] = descriptors[r.key];
		return acc;
	}, {});

	// find index of currently active route inside filteredRoutes
	const currentRouteKey = state.routes[state.index]?.key;
	const filteredIndex = filteredRoutes.findIndex((r) => r.key === currentRouteKey);

	// if current active route is hidden, navigate to the first visible route
	useEffect(() => {
		if (filteredIndex === -1 && filteredRoutes.length > 0) {
			// navigate to first allowed route name
			navigation.navigate(filteredRoutes[0].name);
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [filteredIndex, filteredRoutes.length]);

	// create a safe filtered state for BottomTabBar to render
	const safeState = {
		...state,
		routes: filteredRoutes,
		index: Math.max(0, filteredIndex === -1 ? 0 : filteredIndex),
	};

	return <BottomTabBar {...rest} state={safeState} descriptors={filteredDescriptors} navigation={navigation} />;
}

export default function TabLayout() {
	const { theme } = useThemeCustom();
	const isLoggedIn = !!auth.currentUser;
	const { mode, toggleMode } = useMode();
	const [available, setAvailableLocal] = useState<boolean>(true);
	useEffect(() => {
		setAvailableLocal(true);
	}, []);
	const onToggleAvailability = async () => {
		const next = !available;
		setAvailableLocal(next);
		try {
			await setAvailability(next);
		} catch {
			setAvailableLocal(!next);
		}
	};

	// Get screen dimensions for responsive design
	const { width: screenWidth } = Dimensions.get('window');
	const isSmallScreen = screenWidth < 375; // iPhone SE and similar

	// Header left component with logo and branding
	const HeaderLeft = () => (
		<View style={{ flexDirection: 'row', alignItems: 'center', paddingLeft: 16 }}>
			<Image 
				source={require('@/assets/images/logo.jpg')} 
				style={{ width: 32, height: 32, borderRadius: 6, marginRight: 8 }} 
			/>
			{!isSmallScreen && (
				<Text style={{ color: '#fff', fontSize: 14, fontWeight: '600' }}>
					Blood Bank
				</Text>
			)}
		</View>
	);

	// Header right component with proper spacing and responsive design
	const HeaderRight = () => (
		<View style={{ 
			flexDirection: 'row', 
			alignItems: 'center', 
			paddingRight: 16,
			minHeight: 44, // Ensure adequate touch target
		}}>
			{/* Mode Switch - hide on small screens, accessible via Profile */}
			{!isSmallScreen && (
				<TouchableOpacity 
					onPress={toggleMode} 
					style={{ 
						paddingVertical: 6, 
						paddingHorizontal: 10, 
						backgroundColor: mode === 'donor' ? '#DC2626' : '#2563EB', 
						borderRadius: 16,
						marginRight: 8, // 8px spacing between elements
						minWidth: 60,
						alignItems: 'center',
					}}
				>
					<Text style={{ color: '#fff', fontSize: 12, fontWeight: '600' }}>
						{mode === 'donor' ? 'Donor' : 'Patient'}
					</Text>
				</TouchableOpacity>
			)}
			
			{/* Availability Toggle - always visible for donors */}
			{mode === 'donor' && (
				<View style={{ 
					flexDirection: 'row', 
					alignItems: 'center',
					backgroundColor: 'rgba(255, 255, 255, 0.1)',
					paddingHorizontal: 8,
					paddingVertical: 4,
					borderRadius: 12,
				}}>
					<Text style={{ 
						color: '#fff', 
						fontSize: 12, 
						fontWeight: '600', 
						marginRight: 6 
					}}>
						Available
					</Text>
					<Switch 
						value={available} 
						onValueChange={onToggleAvailability}
						trackColor={{ false: 'rgba(255, 255, 255, 0.3)', true: '#10B981' }}
						thumbColor="#fff"
						ios_backgroundColor="rgba(255, 255, 255, 0.3)"
						style={{ 
							transform: [{ scaleX: 0.8 }, { scaleY: 0.8 }] // Slightly smaller for compact design
						}}
					/>
				</View>
			)}
		</View>
	);
	if (!isLoggedIn) {
		return <Redirect href="/auth/login" />;
	}
	
	return (
		<Tabs
			key={`tabs-${mode}`} // Force re-render when mode changes
			screenOptions={{
				tabBarActiveTintColor: Colors[theme as 'light' | 'dark'].tint,
				headerShown: true,
				headerTitleAlign: 'center',
				headerStyle: { 
					backgroundColor: '#E11D48',
					minHeight: 60, // Minimum 60px as specified
					height: Platform.OS === 'ios' ? 100 : 70, // Adequate height for toggles
				},
				headerTintColor: '#fff',
				headerTitleStyle: {
					fontWeight: '700',
					fontSize: isSmallScreen ? 16 : 18, // Responsive font size
					maxWidth: screenWidth - 200, // Prevent overlap with action buttons
				},
				headerLeft: () => <HeaderLeft />,
				headerRight: () => <HeaderRight />,
				headerTitleContainerStyle: {
					// Ensure title can be truncated if needed
					flex: 1,
					alignItems: 'center',
				},
				tabBarStyle: Platform.select({
					ios: { position: 'absolute' },
					default: {},
				}),
			}}
			// pass mode to custom tab bar
			tabBar={(props) => <CustomTabBar {...props} mode={mode} />}
		>
			{/* declare ALL screens (keep them all so router sees them) */}
			<Tabs.Screen
				name="home"
				options={{
					title: 'Blood Bank Dashboard',
					tabBarIcon: ({ color, size }) => <Ionicons name="home" size={size ?? 24} color={color} />,
					tabBarLabel: 'Home',
				}}
			/>
			<Tabs.Screen
				name="inbox"
				options={{
					title: 'Donor Inbox',
					tabBarIcon: ({ color, size }) => (
						<Ionicons name="mail" size={size ?? 24} color={color} />
					),
					tabBarLabel: 'Inbox',
				}}
			/>
			<Tabs.Screen
				name="donors"
				options={{
					title: 'Find Donors',
					tabBarIcon: ({ color, size }) => (
						<Ionicons name="people" size={size ?? 24} color={color} />
					),
					tabBarLabel: 'Donors',
				}}
			/>
			<Tabs.Screen
				name="request"
				options={{
					title: 'Request Blood',
					tabBarIcon: ({ color, size }) => (
						<Ionicons name="add-circle" size={size ?? 24} color={color} />
					),
					tabBarLabel: 'Request',
				}}
			/>
			<Tabs.Screen
				name="donate"
				options={{
					title: 'Donate Money',
					tabBarIcon: ({ color, size }) => (
						<Ionicons name="heart" size={size ?? 24} color={color} />
					),
					tabBarLabel: 'Donate',
				}}
			/>
			<Tabs.Screen
				name="history"
				options={{
					title: 'History',
					tabBarIcon: ({ color, size }) => (
						<Ionicons name="time" size={size ?? 24} color={color} />
					),
					tabBarLabel: 'History',
				}}
			/>
			<Tabs.Screen
				name="profile"
				options={{
					title: 'My Account',
					tabBarIcon: ({ color, size }) => (
						<Ionicons name="person" size={size ?? 24} color={color} />
					),
					tabBarLabel: 'Profile',
				}}
			/>
		</Tabs>
	);
}
