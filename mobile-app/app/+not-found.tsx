import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import { Ionicons } from '@expo/vector-icons';
import { Link, Stack } from 'expo-router';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function NotFoundScreen() {
  const colorScheme = useColorScheme() ?? 'light';
  const isDark = colorScheme === 'dark';

  return (
    <>
      <Stack.Screen options={{ title: 'Page Not Found' }} />
      <View style={[styles.container, { backgroundColor: Colors[colorScheme].background }]}>
        <View style={styles.content}>
          <Ionicons 
            name="alert-circle-outline" 
            size={80} 
            color={isDark ? '#6B7280' : '#9CA3AF'} 
            style={styles.icon}
          />
          
          <Text style={[styles.title, { color: isDark ? '#fff' : '#111827' }]}>
            Page Not Found
          </Text>
          
          <Text style={[styles.subtitle, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>
            Sorry, we couldn't find the page you're looking for.
          </Text>
          
          <Text style={[styles.description, { color: isDark ? '#9CA3AF' : '#9CA3AF' }]}>
            The page may have been moved, deleted, or you may have entered an incorrect URL.
          </Text>

          <View style={styles.actions}>
            <Link href="/" asChild>
              <TouchableOpacity style={[styles.primaryButton, { backgroundColor: '#E11D48' }]}>
                <Ionicons name="home" size={20} color="#fff" />
                <Text style={styles.primaryButtonText}>Go to Home</Text>
              </TouchableOpacity>
            </Link>

            <Link href="/(tabs)/donors" asChild>
              <TouchableOpacity style={[styles.secondaryButton, { borderColor: isDark ? '#374151' : '#E5E7EB' }]}>
                <Ionicons name="people" size={20} color={isDark ? '#D1D5DB' : '#6B7280'} />
                <Text style={[styles.secondaryButtonText, { color: isDark ? '#D1D5DB' : '#6B7280' }]}>Find Donors</Text>
              </TouchableOpacity>
            </Link>
          </View>

          <View style={styles.helpSection}>
            <Text style={[styles.helpTitle, { color: isDark ? '#fff' : '#111827' }]}>Need Help?</Text>
            <View style={styles.helpLinks}>
              <Link href="/(tabs)/request" asChild>
                <TouchableOpacity style={styles.helpLink}>
                  <Text style={[styles.helpLinkText, { color: '#3B82F6' }]}>Request Blood</Text>
                </TouchableOpacity>
              </Link>
              
              <Text style={[styles.helpSeparator, { color: isDark ? '#6B7280' : '#9CA3AF' }]}>•</Text>
              
              <Link href="/(tabs)/donate" asChild>
                <TouchableOpacity style={styles.helpLink}>
                  <Text style={[styles.helpLinkText, { color: '#3B82F6' }]}>Donate Money</Text>
                </TouchableOpacity>
              </Link>
              
              <Text style={[styles.helpSeparator, { color: isDark ? '#6B7280' : '#9CA3AF' }]}>•</Text>
              
              <Link href="/(tabs)/profile" asChild>
                <TouchableOpacity style={styles.helpLink}>
                  <Text style={[styles.helpLinkText, { color: '#3B82F6' }]}>Profile</Text>
                </TouchableOpacity>
              </Link>
            </View>
          </View>
        </View>
      </View>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  content: {
    alignItems: 'center',
    maxWidth: 400,
  },
  icon: {
    marginBottom: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 12,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 8,
    textAlign: 'center',
    lineHeight: 24,
  },
  description: {
    fontSize: 14,
    marginBottom: 32,
    textAlign: 'center',
    lineHeight: 20,
  },
  actions: {
    width: '100%',
    gap: 12,
    marginBottom: 32,
  },
  primaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  secondaryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    borderWidth: 1,
    backgroundColor: 'transparent',
  },
  secondaryButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  helpSection: {
    alignItems: 'center',
  },
  helpTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  helpLinks: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  helpLink: {
    paddingVertical: 4,
  },
  helpLinkText: {
    fontSize: 14,
    fontWeight: '500',
  },
  helpSeparator: {
    fontSize: 14,
  },
});
