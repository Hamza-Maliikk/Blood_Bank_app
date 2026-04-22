import { getUserProfile, saveUserProfile } from '@/lib/users';
import AsyncStorage from '@react-native-async-storage/async-storage';
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

export type AppMode = 'donor' | 'patient';

type ModeContextType = {
  mode: AppMode;
  setMode: (mode: AppMode) => void;
  toggleMode: () => void;
  isLoading: boolean;
};

const ModeContext = createContext<ModeContextType | undefined>(undefined);

export function ModeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setModeState] = useState<AppMode>('patient');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load mode from user profile and local storage
    (async () => {
      try {
        // First try to get from user profile
        const profile = await getUserProfile();
        if (profile?.mode) {
          setModeState(profile.mode);
        } else {
          // Fallback to local storage
          const savedMode = await AsyncStorage.getItem('app-mode');
          if (savedMode && ['donor', 'patient'].includes(savedMode)) {
            setModeState(savedMode as AppMode);
          }
        }
      } catch (e) {
        console.warn('Failed to load mode from profile/storage');
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  const setMode = async (newMode: AppMode) => {
    setModeState(newMode);
    try {
      // Save to local storage immediately
      await AsyncStorage.setItem('app-mode', newMode);
      // Save to user profile
      await saveUserProfile({ mode: newMode });
    } catch (e) {
      console.warn('Failed to save mode to profile/storage');
    }
  };

  const toggleMode = () => setMode(mode === 'patient' ? 'donor' : 'patient');

  const value = useMemo(
    () => ({ mode, setMode, toggleMode, isLoading }),
    [mode, isLoading]
  );
  return <ModeContext.Provider value={value}>{children}</ModeContext.Provider>;
}

export function useMode() {
  const ctx = useContext(ModeContext);
  if (!ctx) throw new Error('useMode must be used within ModeProvider');
  return ctx;
}


