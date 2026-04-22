/**
 * Colors used in the app according to the documentation specifications.
 * Light theme: pure white backgrounds with black text
 * Dark theme: pure black backgrounds with white text
 */

const tintColorLight = '#007BFF';
const tintColorDark = '#4A9EFF';

export const Colors = {
  light: {
    // Primary colors
    text: '#000000', // Pure black
    background: '#FFFFFF', // Pure white
    secondaryBackground: '#F8F9FA', // Light gray
    cardBackground: '#FFFFFF', // White with subtle shadows
    inputBackground: '#F1F3F4',
    
    // Text hierarchy
    secondaryText: '#6C757D', // Medium gray
    disabledText: '#ADB5BD', // Light gray
    linkText: '#007BFF', // Blue
    
    // UI elements
    border: '#E9ECEF', // Light gray
    shadow: 'rgba(0,0,0,0.1)',
    
    // Legacy/compatibility
    tint: tintColorLight,
    icon: '#687076',
    tabIconDefault: '#687076',
    tabIconSelected: tintColorLight,
  },
  dark: {
    // Primary colors
    text: '#FFFFFF', // Pure white
    background: '#000000', // Pure black
    secondaryBackground: '#1A1A1A', // Dark gray
    cardBackground: '#2D2D2D', // Dark gray with subtle highlights
    inputBackground: '#3A3A3A',
    
    // Text hierarchy
    secondaryText: '#B0B0B0', // Light gray
    disabledText: '#666666', // Medium gray
    linkText: '#4A9EFF', // Lighter blue
    
    // UI elements
    border: '#404040', // Medium gray
    shadow: 'rgba(255,255,255,0.1)',
    
    // Legacy/compatibility
    tint: tintColorDark,
    icon: '#9BA1A6',
    tabIconDefault: '#9BA1A6',
    tabIconSelected: tintColorDark,
  },
};
