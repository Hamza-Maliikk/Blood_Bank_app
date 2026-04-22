export const BLOOD_GROUPS = [
  'A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'
];

export const GENDERS = [
  'Male', 'Female', 'Other'
];

export const CITIES_PK = [
  'Karachi','Lahore','Islamabad','Rawalpindi','Faisalabad','Multan','Peshawar','Quetta','Hyderabad',
  'Sialkot','Gujranwala','Bahawalpur','Sukkur','Sargodha','Abbottabad','Mardan','Mingora','Kasur',
  'Okara','Sahiwal','Mirpur Khas','Nawabshah','Sheikhupura','Jhang','Rahim Yar Khan','Dera Ghazi Khan'
];

export function isValidPakistaniPhone(phone: string): boolean {
  return /^\+92\d{10}$/.test(phone.trim());
}


