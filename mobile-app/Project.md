### Blood Donation App – Full Plan (React Native Expo & Firebase)

This document is the canonical reference for product behavior, data flow, and implementation details.

#### Core Objectives
- Save lives via fast donor matching (city, blood group, availability).
- Trust & Safety via verified donors, hospitals, NGOs.
- Sustainability via optional paid features (priority requests, hospital/NGO subscriptions).

#### User Roles
- Donor: register, mark availability, donate blood/money.
- Receiver (Patient/Family): create requests, contact donors.
- Hospital/NGO: manage drives, verify requests.
- Admin: monitor, prevent fraud.

#### Navigation (expo-router)
- Auth stack: `/auth/login`, `/auth/signup`, `/auth/reset`, `/auth/onboarding`.
- Tabs: `/(tabs)/home`, `/(tabs)/donors` (Patient only), `/(tabs)/request` (Patient only), `/(tabs)/donate`, `/(tabs)/history`, `/(tabs)/profile`, `/(tabs)/inbox` (Donor only).
    -In expo {tabs} navigation showing by detail with file name. we can overcome this with _layout.tsx file but there could be an issue when we showing menu conditionally it will with default routing.
- Details: `/request`, `/request/[id]`, `/profile/[uid]`, `/donations`, `/donations/add`, `/+not-found`.
- Auth Guard: tabs require authentication; logged-out users redirect to `/auth/login`.
misplace
#### App Modes & Header Actions
- Mode Switch: Donor/Patient toggle in `/(tabs)/profile` and surfaced in dashboard header for quick access. Mode changes emphasis/visibility of screens; permissions unchanged.
- Availability Toggle (Donors): quick switch in dashboard header and on Profile. Updates `users/{uid}/available` immediately; used by Donor List filtering and Inbox logic. Only visible when user is in Donor mode.

#### Mode Switching Behavior
- **Donor Mode**: Emphasizes donation-related features
  - Hides Donors List tab (not applicable for donors)
  - Hides Request Blood tab (not applicable for donors)
  - Shows Donor Inbox tab (Request To Me, All Requests)
  - Displays availability toggle in header and profile
  - Highlights "Become a Donor" actions and donation history
  - Shows donor-specific statistics and badges
  - Enables accepting urgent requests from dashboard
- **Patient Mode**: Emphasizes request-related features
  - Shows Donors List tab (find available donors)
  - Shows Request Blood tab (create blood requests)
  - Hides Donor Inbox tab
  - Hides availability toggle (not applicable)
  - Emphasizes "Request Blood" actions and request history
  - Shows patient-specific request management tools
  - Focuses on finding donors and managing requests
- **Mode Persistence**: User's selected mode persists across app sessions via local storage
- **Default Mode**: New users default to Patient mode; can switch during onboarding

#### Dashboard Header Layout
- Header structure (left to right): App logo/branding (left), Screen title (center), Action buttons (right)
- Action buttons area: Mode switch (Donor/Patient toggle), Availability toggle (donors only), spacing between elements
- Minimum header height: 60px to accommodate toggle switches without text overlap
- Action buttons should have adequate padding (8px minimum between elements)
- Screen title should be truncated with ellipsis if it conflicts with action buttons
- On smaller screens, consider showing only availability toggle and hide mode switch (accessible via Profile)

#### Screens & Flows
- Signup
  - Use auth layout. Show logo top-center with app name.
  - Inputs: Email, Password. Secondary: Login link.
  - On success: reset form, navigate to Onboarding.
- Login
  - Use auth layout. Logo top-center.
  - Inputs: Email, Password. Links: Create account, Forgot password.
  - If onboarding incomplete: redirect to Onboarding.
  - disable button and show loader while signing..
- Reset Password
  - Use auth layout. Input: Email. Button: Send Reset Email.
- Onboarding Profile (after signup/login)
  - Use auth layout; pre-fill available info.
  - Inputs: Full Name, Email (optional), Gender, Phone (+92 validation), Blood Group, City, CNIC (optional), Mode Selection (Donor/Patient radio buttons or toggle), Available as Donor (toggle - only visible if Donor mode selected).
  - Button: Save & Continue → navigate to Home (tabs).
  - Mode Selection: Defaults to Patient; explain benefits of each mode with brief descriptions
- Complete Profile (first login if incomplete)
  - Same fields as Onboarding; Email may be read-only if verified.
  - Include Mode Selection if not previously set
  - Availability toggle only shown for Donor mode selection
- Home (Dashboard)
  - Sections: Search (by blood group, city), Urgent Requests (patient name, city, blood group, time), Find Donors CTA.
  - Buttons: Request Blood (primary), Become a Donor.
  - Header: App branding; Mode toggle (Donor/Patient); Availability toggle (donors only).
  - **Urgent Requests Section** (Donors and NGOs only): 
    - Displays recent high-priority requests with countdown timers
    - Cards show patient name, blood group, city, hospital, time posted
    - Action buttons: "View Details" (opens full request), "Accept" (donors only)
    - "Accept" immediately assigns donor and updates request status to accepted
    - **Request Removal**: Accepted requests are immediately removed from urgent requests list
    - Only visible when user is in Donor mode or associated with an NGO
    - Only shows requests marked with `urgent: true` flag
- Donor List
  - Show users marked available as donors.
  - Filters: Blood Group (multi-select), City, Availability (active only).
  - **"Active Only" Filter Behavior**: When enabled, shows only donors with `available: true` status; when disabled, shows all donors regardless of availability status.
  - Cards: profile image, name, blood group, city, gender; actions (Call/SMS/WhatsApp/Request).
  - "Request" opens Request Blood with `requestedTo` prefilled.
- Request Blood
  - If `requested_to` provided: create targeted request; status `pending` until donor accepts/rejects. Notify donor (WhatsApp/push/deeplink).
  - If no `requested_to`: create general request; status `open` for donors to accept.
  - Inputs: Patient Name (default: current user's name), Required Blood Group (default: user's group), City (default: user's city), Gender (default: user's gender), Hospital/Location (text or map), Quantity (units), request_to (optional), Notes (optional), Urgent Flag (checkbox - marks request as urgent).
  - Button: Post Request.
  - **Request Cancellation**: Patient can cancel their own requests within 10 minutes of creation via "Cancel Request" button with confirmation dialog.
  - Location Picker: offer map picker and "Use current location for hospital"; persist `locationAddress`, `locationLat`, `locationLng` when available. Request location access only when user opts in; handle denial gracefully.
- Donor Inbox (visible in Donor mode)
  - Tabs: Request To Me (targeted/pending), All Requests (discoverable open requests).
  - Actions: Accept, Reject, View Patient Profile.
  - Logic: Accept on open requests assigns current user as `requestedTo` and sets status `accepted`; reject on targeted requests only by the targeted donor.
  - **All Requests Tab**: Shows all open requests (`status === 'open'`) that are discoverable by all donors, including both urgent and non-urgent requests.
  - **Automatic Donation Intent**: When a donor accepts a blood request, a donation record is automatically created with status "pending" to track the commitment. No separate action needed.

#### **"Request To Me" Function - Detailed Behavioral Specification**

##### **How "Request To Me" Works (Step-by-Step Behavior)**
1. **Targeted Request Creation Process**:
   - Patient navigates to Request Blood screen
   - Patient selects specific donor from Donor List (taps "Request" button)
   - Request Blood form opens with `requestedTo` field pre-filled with donor's UID
   - Patient fills required fields and submits
   - System creates request with status `pending` (not `open`)
   - System immediately triggers notification to targeted donor

2. **Donor Notification Behavior**:
   - **Firebase Realtime Database Listener**: Donor's inbox automatically updates via Firebase listener
   - **In-App Visual Indicator**: New request appears in "Request To Me" tab with unread badge
   - **No External Notifications**: Uses only Firebase free tier (no push notifications to avoid costs)

3. **Inbox Display Behavior**:
   - **"Request To Me" Tab**: Shows only requests where `requestedTo === currentUser.uid` AND `status === 'pending'`
   - **"All Requests" Tab**: Shows only requests where `status === 'open'` (discoverable by all donors)
   - **Real-time Updates**: Firebase listener automatically refreshes when new targeted requests arrive
   - **Empty State**: Shows "No targeted requests yet" when no pending requests exist

4. **User Acceptance Flow (Detailed Behavior)**:
   - **Step 1**: Donor opens app and switches to Donor mode
   - **Step 2**: System checks donor availability status (`available: true`)
   - **Step 3**: Donor navigates to Inbox tab
   - **Step 4**: Donor sees "Request To Me" tab with count badge showing number of pending requests
   - **Step 5**: Donor taps "Request To Me" tab to view targeted requests
   - **Step 6**: Donor sees list of targeted requests with patient details (name, blood group, city, hospital, notes)
   - **Step 7**: Accept button is enabled only if donor is available; disabled with tooltip if not available
   - **Step 8**: Donor taps "Accept" button on specific request
   - **Step 9**: Confirmation dialog appears: "Accept this blood request? You will be committed to donating blood."
   - **Step 10**: If donor confirms:
     - Request status changes from `pending` to `accepted`
     - `requestedTo` field is set to current donor's UID
     - `acceptedAt` timestamp is added to request
     - `acceptedBy` field is set to current donor's UID
     - Automatic donation record created in `donations/{donorUid}/{donationId}` with status `pending`
     - Patient receives in-app notification (via Firebase listener)
     - Request disappears from donor's "Request To Me" tab
     - Request disappears from "Urgent Requests" list (if it was urgent)
     - Request appears in both donor and patient "Accepted" history
   - **Step 11**: If donor cancels: No changes made, request remains in "Request To Me" tab

5. **User Rejection Flow (Detailed Behavior)**:
   - **Step 1-6**: Same as acceptance flow
   - **Step 7**: Donor taps "Reject" button on specific request
   - **Step 8**: Confirmation dialog appears: "Reject this blood request? The patient will be notified."
   - **Step 9**: If donor confirms:
     - Request status changes from `pending` to `rejected`
     - `requestedTo` field is set to current donor's UID
     - Patient receives in-app notification (via Firebase listener)
     - Request disappears from donor's "Request To Me" tab
     - Request appears in patient's "Rejected" history
   - **Step 10**: If donor cancels: No changes made, request remains in "Request To Me" tab

#### **Request Accept Flow - Detailed Behavioral Specification**

##### **Core Accept Flow Requirements**
- **Availability Check**: Donors can only accept requests when marked as available (`available: true`)
- **Button State Management**: Accept button is disabled/hidden when donor is not available
- **Request Removal**: Accepted requests are immediately removed from all request lists
- **History Visibility**: Accepted requests appear in both donor and patient history
- **Status Updates**: Request status changes from `pending`/`open` to `accepted`

##### **Step-by-Step Accept Flow Behavior**

1. **Pre-Accept Validation**:
   - **Step 1**: System checks if current user is in Donor mode
   - **Step 2**: System verifies donor's availability status (`users/{uid}/available === true`)
   - **Step 3**: System confirms request is still available for acceptance (`status === 'pending'` or `status === 'open'`)
   - **Step 4**: If any validation fails, Accept button is disabled with appropriate message

2. **Accept Button State Management**:
   - **Available Donor**: Accept button is enabled and visible
   - **Unavailable Donor**: Accept button is disabled with tooltip "You must be available to accept requests"
   - **Already Accepted**: Accept button is hidden, replaced with "Accepted" status indicator
   - **Request Expired**: Accept button is disabled with "Request no longer available" message

3. **Accept Action Execution**:
   - **Step 1**: User taps "Accept" button on request
   - **Step 2**: Confirmation dialog appears: "Accept this blood request? You will be committed to donating blood."
   - **Step 3**: If user confirms:
     - Request status changes from `pending`/`open` to `accepted`
     - `requestedTo` field is set to current donor's UID
     - `acceptedAt` timestamp is added to request
     - Automatic donation record created in `donations/{donorUid}/{donationId}` with status `pending`
     - Patient receives in-app notification (via Firebase listener)
   - **Step 4**: If user cancels: No changes made, request remains available

4. **Post-Accept UI Updates**:
   - **Request Lists**: Accepted request immediately disappears from:
     - Donor's "Request To Me" tab
     - Donor's "All Requests" tab
     - Urgent Requests list (if it was urgent)
     - Any other request discovery lists
   - **History Updates**: Accepted request appears in:
     - Donor's "Accepted" history tab
     - Patient's "Accepted" history tab
   - **Button States**: Accept button is replaced with "Accepted" status indicator

5. **Real-time Synchronization**:
   - **Firebase Listeners**: All connected clients receive real-time updates
   - **Immediate UI Updates**: No page refresh needed, changes appear instantly
   - **Cross-Device Sync**: Changes sync across all user's devices
   - **Offline Handling**: Changes are queued and applied when connection is restored

##### **Accept Flow Error Handling**

- **Donor Not Available**:
  - Error: "You must mark yourself as available to accept blood requests"
  - Action: Redirect to Profile to enable availability toggle
  - UI: Accept button disabled with clear explanation

- **Request Already Accepted**:
  - Error: "This request has already been accepted by another donor"
  - Action: Refresh request list to show current status
  - UI: Show "Accepted by [Donor Name]" status

- **Request Expired/Cancelled**:
  - Error: "This request is no longer available"
  - Action: Remove from request list
  - UI: Show "Request Cancelled" or "Request Expired" status

- **Network Error**:
  - Error: "Unable to accept request. Please check your connection"
  - Action: Retry mechanism with exponential backoff
  - UI: Show retry button and loading state

##### **Accept Flow Data Model Updates**

```json
{
  "requests/{id}": {
    "status": "accepted",
    "requestedTo": "donorUid",
    "acceptedAt": 1640995200000,
    "acceptedBy": "donorUid"
  },
  "donations/{donorUid}/{donationId}": {
    "id": "donationId",
    "requestId": "requestId",
    "status": "pending",
    "date": 1640995200000,
    "donorUid": "donorUid"
  }
}
```

##### **Accept Flow API Functions**

- `canAcceptRequest(requestId, donorUid)`: Check if donor can accept specific request
- `acceptRequest(requestId, donorUid)`: Execute accept action with full validation
- `getAcceptableRequests(donorUid)`: Get list of requests donor can accept
- `updateRequestStatus(requestId, status, donorUid)`: Update request status with validation

##### **Accept Flow UI Components**

- **Accept Button**: Dynamic button with state-based styling
- **Status Indicators**: Clear visual feedback for request states
- **Confirmation Dialogs**: User-friendly confirmation with clear consequences
- **Error Messages**: Helpful error messages with suggested actions
- **Loading States**: Visual feedback during async operations

##### **Notification System (Free Firebase Implementation)**
- **Primary Method**: Firebase Realtime Database listeners (completely free)
- **Implementation**: Each user has a `notifications/{uid}` node in Firebase
- **Notification Types**:
  - `new_targeted_request`: Created when patient targets specific donor
  - `request_accepted`: Created when donor accepts request
  - `request_rejected`: Created when donor rejects request
  - `donation_reminder`: Created for upcoming donation commitments
  - `request_fulfilled`: Created when donation is completed

- **Notification Behavior**:
  - **Creation**: Notifications created in Firebase when actions occur
  - **Delivery**: App listens to `notifications/{uid}` node for real-time updates
  - **Display**: In-app notification badge and list (no external push notifications)
  - **Marking Read**: User can mark notifications as read (updates `read: true` in Firebase)
  - **Cleanup**: Notifications older than 30 days are automatically filtered out

##### **Request Cancellation System (Detailed Behavior)**
- **Cancellation Window**: Patients can cancel their own requests within 10 minutes of creation
- **Cancellation Process**:
  - **Step 1**: Patient creates a blood request
  - **Step 2**: Within 10 minutes, "Cancel Request" button appears on request detail screen
  - **Step 3**: Patient taps "Cancel Request" button
  - **Step 4**: Confirmation dialog: "Cancel this request? This action cannot be undone."
  - **Step 5**: If patient confirms:
    - Request status changes from `pending`/`open` to `cancelled`
    - Request disappears from donor inbox and urgent requests list
    - Donors who were notified receive cancellation notification
    - Request appears in patient's "Cancelled" history
  - **Step 6**: If patient cancels: No changes made, request remains active

- **Cancellation Restrictions**:
  - **Time Limit**: Only cancellable within 10 minutes of creation
  - **Status Check**: Cannot cancel if already accepted by donor
  - **Creator Only**: Only the request creator can cancel their own requests
  - **Visual Indicator**: Cancel button shows remaining time (e.g., "Cancel (8 min left)")

##### **Soft Delete for History Management (Detailed Behavior)**
- **Implementation**: Add `deleted: true` and `deletedAt: timestamp` fields to records
- **User Actions**:
  - **Delete Request**: User can delete their own requests from history
  - **Delete Donation**: User can delete their own donation records
  - **Delete Comment**: User can delete their own comments or comments on their requests

- **Soft Delete Behavior**:
  - **Step 1**: User navigates to History tab
  - **Step 2**: User finds request/donation they want to delete
  - **Step 3**: User taps "Delete" button (trash icon)
  - **Step 4**: Confirmation dialog: "Delete this item? It will be removed from your history."
  - **Step 5**: If user confirms:
    - Record is marked with `deleted: true` and `deletedAt: currentTimestamp`
    - Record disappears from user's history view
    - Record remains in database for audit purposes
    - Other users' views are not affected
  - **Step 6**: If user cancels: No changes made

- **Data Retention Policy**:
  - **Soft Deleted Records**: Remain in database indefinitely for audit
  - **User Privacy**: Deleted records are hidden from user interface
  - **Admin Access**: Admins can view soft-deleted records if needed
  - **Recovery**: Soft-deleted records can be restored by admin if necessary

- **History Filtering**:
  - **Default View**: Shows only non-deleted records (`deleted !== true`)
  - **Admin View**: Can show all records including soft-deleted ones
  - **Performance**: Client-side filtering to avoid additional Firebase queries
- Request History (renamed from "Donation History")
  - **Patient Mode**: Shows all requests I created (posted) with status filtering
    - Tabs: All, Pending, Rejected, Accepted, Fulfilled, Cancelled
    - Each request is clickable to view full details
    - Links to donor profiles for accepted requests
  - **Donor Mode**: Shows all requests I accepted as a donor
    - Tabs: All, Pending, Accepted, Fulfilled, Cancelled
    - Each request is clickable to view full details
    - Shows my donation commitments and their status
  - **Clickable Items**: All history items are clickable to open detailed view
  - **Status Tracking**: Clear status indicators for each request
- Request Detail
  - Full request data and comments thread (name, timestamp, message). Actions based on role and status.
  - **Header Layout**: Consistent with other pages - app branding (left), screen title (center), action buttons (right).
  - **Action Button Visibility**: "Accept" button only visible when user is in Donor mode; hidden for Patient mode users.
  - **No Manual Donation Recording**: Donation records are automatically created when donors accept requests; no separate recording action needed.
- Donor Profile (public)
  - Public profile view with donation stats and availability indicator.
 - Profile (My Account)
  - Sections: My Profile, Settings.
  - **Scrollable Layout**: Must be scrollable when content overflows to ensure all content is accessible.
  - Actions: Availability toggle (mirrors header), Mode switch (Donor/Patient), Theme (System/Light/Dark) with local persistence, Logout.
  - Logout: sign out of auth, clear local caches/session, reset navigation to `/auth/login` (confirm dialog optional).
- Money Donations Tab (Stripe Integration)
  - **Purpose**: General monetary donations to support the blood bank platform and its operations, not direct person-to-person transfers.
  - **Donate Amount Screen**:
    - Amount input with predefined options (500, 1000, 2500, 5000 PKR) and custom amount field
    - Purpose selection (optional): Platform Support, Emergency Fund, Equipment, General
    - Stripe payment processing with secure checkout
    - Confirmation screen with receipt details
  - **Donation History Screen**:
    - List of all user's money donations with date, amount, purpose, and status
    - Each donation links to Stripe receipt for download/printing
    - Filter by date range and amount
    - Total donation statistics and impact summary
- Not Found
  - Friendly fallback for unknown routes.


#### Forms & Validation
- Request Blood required fields: Patient Name, Required Blood Group, City.
- Allowed Blood Groups: A+, A-, B+, B-, O+, O-, AB+, AB-.
- Allowed Genders: Male, Female, Other.
- Phone: must start with +92 and pass Pakistan validation.
- Quantity: positive integer (blood units). Trim all text inputs; reject whitespace-only values.

#### Data Model (Firebase RTDB)
- `users/{uid}` → UserProfile
  - { uid, name, email?, gender?, bloodGroup?, city?, phone?, cnic?, available?, mode?: 'donor'|'patient', themePreference?: 'system'|'light'|'dark', createdAt, updatedAt }
- `requests/{id}` → BloodRequest
  - { id, createdBy, patientName, requiredBloodGroup, city, gender?, hospital?, locationAddress?, locationLat?, locationLng?, unitsRequired?, neededBy?, notes?, requestedTo?, status, urgent?: boolean, acceptedAt?: number, acceptedBy?: string, createdAt, deleted?: boolean, deletedAt?: number }
- `donations/{uid}/{id}` → Donation
  - { id, requestId, status, date, deleted?: boolean, deletedAt?: number }
- `comments/{requestId}/{id}` → Comment
  - { id, uid, text, createdAt, deleted?: boolean, deletedAt?: number }
- `money_donations/{uid}/{id}` → MoneyDonation (Stripe integration)
  - { id, uid, amount, currency, purpose?, createdAt, receiptUrl?, stripePaymentId?, stripeSessionId?, deleted?: boolean, deletedAt?: number }
- `notifications/{uid}/{id}` → Notification (Free Firebase Implementation)
  - { id, uid, type, title, message, data?, read: boolean, createdAt, expiresAt?: number }
- `badges/{uid}/{id}` → DonorBadge (AI-Generated)
  - { id, uid, badgeId, name, description, icon, color, criteria, earnedAt, createdAt }
- `impact_stories/{uid}/{id}` → ImpactStory (AI-Generated)
  - { id, uid, type, title, content, statistics, visualElements, generatedAt, createdAt }
- `ai_analytics/{uid}` → DonorAnalytics (AI-Processed)
  - { uid, responseTime, successRate, donationCount, impactScore, lastAnalyzed, createdAt }

#### Client API Contract & Guardrails (implementation guide)
- All data access via `lib/*`. No direct Firebase in UI.
- Auth required for any write. Use ms epoch timestamps. Omit `undefined` fields.
- Naming: mutations `verbNoun`; queries `getX`/`listX`.
- Pagination: optional `limit` and `cursor` (keyset by RTDB key). Client filters allowed initially.

- Users (`lib/users`)
  - `saveUserProfile(partial)`: upsert current user; set `createdAt` on first write; always update `updatedAt`.
  - `getUserProfile(uid?)`: fetch by uid, default current; returns profile or null.
  - `listAvailableDonors(filters?, options?)`: filter by city, bloodGroup, gender, available (default true); returns items and next cursor.
  - `listAllUsers()`: dev/admin utility.
  - `setAvailability(available)`: fast toggle from header/profile; updates `available` and `updatedAt`.

- Requests (`lib/requests`)
  - `postRequest(input)`: targeted → status `pending`; general → `open`; returns request id.
  - `getRequestById(id)`: fetch one request.
  - `listMyRequests(uid?)`: requests created by user.
  - `listRequests(filters?, options?)`: browse with filters: status, city, requiredBloodGroup, createdBy, requestedTo, mineOnly, toMeOnly, openOnly, urgentOnly.
  - `listDonorInbox(options?)`: targeted-to-me (`pending`) + discoverable `open` requests.
  - `canAcceptRequest(requestId, donorUid)`: check if donor can accept specific request (availability + status validation).
  - `acceptRequest(requestId, donorUid)`: donor accepts with full validation; un-targeted requests assign current user; automatically creates donation record; removes from urgent requests list; updates status to `accepted`.
  - `rejectRequest(id)`: donor rejects; only targeted donor may reject targeted.
  - `cancelRequest(id)`: creator cancels; status `cancelled`; only allowed within 10 minutes of creation.
  - `markFulfilled(id)`: creator marks fulfilled; status `fulfilled`.
  - `getDonorStats(uid)`: totals for received/accepted/rejected.
  - `canCancelRequest(requestId)`: check if request can be cancelled (within 10 minutes and by creator).
  - `getAcceptableRequests(donorUid)`: get list of requests donor can accept (filters by availability + status).
  - `updateRequestStatus(requestId, status, donorUid)`: update request status with validation and proper state management.

- Donations (`lib/donations`)
  - `createDonationRecord(requestId, donorUid)`: automatically called when donor accepts a request; creates pending blood donation record; returns id.
  - `updateDonationStatus(donationId, status)`: update donation status (pending → completed/cancelled).
  - `listMyDonations(uid?)`: list blood donation records for user.
  - `createStripePaymentIntent({ amount, currency?, purpose? })`: call Node.js backend to create Stripe payment intent for money donation; returns client secret.
  - `confirmStripePayment({ paymentIntentId, paymentMethodId })`: confirm payment with Stripe using payment method.
  - `recordMoneyDonation({ amount, currency?, purpose?, stripePaymentId, receiptUrl? })`: record completed money donation after Stripe confirmation; returns id.
  - `listMyMoneyDonations(uid?)`: list money donations for user with filtering options (client-side only).

- Comments (`lib/comments`)
  - `addComment(requestId, uid, text)`: add a comment.
  - `listComments(requestId)`: list comments.
  - `deleteComment(requestId, commentId)`: author (or request creator) deletes.

- Notifications (`lib/notifications`) - Free Firebase Implementation
  - `createNotification(uid, type, title, message, data?)`: create notification for user.
  - `listNotifications(uid)`: fetch user's notifications (unread first, filtered by expiration).
  - `markNotificationRead(notificationId)`: mark notification as read.
  - `markAllNotificationsRead(uid)`: mark all user notifications as read.
  - `deleteNotification(notificationId)`: delete notification.
  - `sendTargetedRequestNotification(donorUid, requestId)`: send notification for new targeted request.
  - `sendRequestResponseNotification(patientUid, requestId, response)`: send notification for accept/reject.

- Soft Delete (`lib/softDelete`) - History Management
  - `softDeleteRequest(requestId)`: mark request as deleted (soft delete).
  - `softDeleteDonation(donationId)`: mark donation as deleted (soft delete).
  - `softDeleteComment(commentId, requestId)`: mark comment as deleted (soft delete).
  - `softDeleteMoneyDonation(donationId)`: mark money donation as deleted (soft delete).
  - `restoreRequest(requestId)`: restore soft-deleted request (admin only).
  - `restoreDonation(donationId)`: restore soft-deleted donation (admin only).
  - `listDeletedItems(uid, type)`: list soft-deleted items for admin recovery.

- AI Features (`lib/ai`) - Gemini API Integration
  - `analyzeDonorBehavior(uid)`: analyze donor data and suggest badges via Gemini API.
  - `getSmartDonorSelection(requestId)`: get AI-selected donors for notifications.
  - `generateImpactStory(uid, period)`: generate personalized impact story.
  - `updateDonorBadges(uid)`: update donor badges based on AI analysis.
  - `getDonorAnalytics(uid)`: get AI-processed donor analytics.
  - `createBadge(badgeData)`: create new badge in donor's profile.
  - `getImpactStories(uid)`: get all impact stories for donor.
  - `triggerSmartNotification(requestId)`: trigger AI-powered notification system.


#### Error Categories (UI-facing)
- auth/not-authenticated: sign-in required.
- auth/forbidden: lacks permission.
- input/invalid: validation failed; include field hint.
- data/not-found: record missing.
- net/unavailable: offline/network; show retry.

#### Security (rules intent summary)
- `users/{uid}`: owner read/write.
- `requests/{id}`: authenticated read; create only by creator; creator updates own; targeted donor accepts/rejects; donors may accept open requests (becoming `requestedTo`).
- `donations/{uid}` and `money_donations/{uid}`: owner read/write.
- `comments/{requestId}/{commentId}`: author can write/delete; all signed-in can read.

#### Payment Configuration (Stripe)
- All payments (money donations) are processed through Stripe using Node.js backend for security.
- Client-side configuration: `config/stripe.ts` with environment variables:
  - `EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY`: Stripe publishable key for client-side integration
- Server-side configuration (Node.js backend environment):
  - `STRIPE_SECRET_KEY`: Stripe secret key for server-side operations (secure)
  - `STRIPE_WEBHOOK_SECRET`: Webhook endpoint secret for payment confirmations
  - `FIREBASE_SERVICE_ACCOUNT`: Firebase service account key for database operations
- Payment flows:
  - Money donations: one-time payments to support platform operations (not direct person-to-person transfers) with receipt generation
- Node.js backend endpoints:
  - `POST /api/create-payment-intent`: Create Stripe payment intents for money donations
  - `POST /api/webhook`: Process Stripe webhook events for payment confirmations
- Receipt handling: Store Stripe receipt URLs in `money_donations` records
- Security: Never expose secret keys to client; all sensitive operations handled via Node.js backend

#### Node.js Backend Setup (Stripe Only)
- **Framework**: Express.js with TypeScript
- **Purpose**: Handle Stripe payment processing and webhooks only
- **Payment Processing**: Stripe SDK for payment intents and webhooks
- **Database**: Firebase Admin SDK for storing donation records after successful payments
- **Deployment**: Heroku, Railway, or similar cloud platform
- **Environment Variables**:
  - `STRIPE_SECRET_KEY`: Stripe secret key
  - `STRIPE_WEBHOOK_SECRET`: Webhook endpoint secret
  - `FIREBASE_SERVICE_ACCOUNT`: Firebase service account JSON
  - `PORT`: Server port (default: 3000)
- **API Endpoints**:
  - `POST /api/create-payment-intent`: Create Stripe payment intent
  - `POST /api/webhook`: Stripe webhook handler
  - `GET /api/health`: Health check endpoint

#### Theming & Branding

##### Theme System
- **System Theme Respect**: App automatically follows device light/dark theme by default
- **Manual Override**: In-app theme toggle in Profile settings (System/Light/Dark)
- **Theme Persistence**: User preference stored locally; fallback to system if unset
- **Theme Application**: Consistent theming across all screens, components, and navigation

##### Light Theme Specifications
- **Background Colors**: 
  - Primary background: #FFFFFF (pure white)
  - Secondary background: #F8F9FA (light gray)
  - Card backgrounds: #FFFFFF with subtle shadows
  - Input backgrounds: #F1F3F4
- **Text Colors**:
  - Primary text: #000000 (pure black)
  - Secondary text: #6C757D (medium gray)
  - Disabled text: #ADB5BD (light gray)
  - Link text: #007BFF (blue)
- **UI Elements**:
  - Borders: #E9ECEF (light gray)
  - Shadows: rgba(0,0,0,0.1)
  - Status bar: dark content on light background

##### Dark Theme Specifications
- **Background Colors**:
  - Primary background: #000000 (pure black)
  - Secondary background: #1A1A1A (dark gray)
  - Card backgrounds: #2D2D2D with subtle highlights
  - Input backgrounds: #3A3A3A
- **Text Colors**:
  - Primary text: #FFFFFF (pure white)
  - Secondary text: #B0B0B0 (light gray)
  - Disabled text: #666666 (medium gray)
  - Link text: #4A9EFF (lighter blue)
- **UI Elements**:
  - Borders: #404040 (medium gray)
  - Shadows: rgba(255,255,255,0.1)
  - Status bar: light content on dark background

##### Theme Switching Behavior
- **Immediate Application**: Theme changes apply instantly without app restart
- **Complete App Theme**: Theme changes affect the entire app, not just navigation elements
- **Component Updates**: All screens, modals, and components update simultaneously
- **Navigation Theme**: Tab bar, headers, and navigation elements update accordingly
- **Status Bar**: Automatically adjusts content color based on theme
- **Splash Screen**: Matches selected theme on app launch
- **Global Theme**: Background colors, text colors, and UI elements update throughout the entire application

##### Branding Elements
- Header shows `assets/images/logo.jpg` (with theme-appropriate variants if needed)
- App icon and favicon configured via `app.json`
- Logo visibility optimized for both light and dark backgrounds

#### Performance & Scalability
- Batch reads; debounce searches; avoid heavy listeners on tab roots.
- Plan fan-out indexes if lists grow:
  - `user_requests/{uid}/{requestId}: true`
  - `donor_requests/{uid}/{requestId}: true`
  - `open_requests/{requestId}: true`

#### Accessibility & UX
- High contrast, large touch targets, clear CTAs.
- **Scrollable Content**: All screens must support scrolling when content overflows to ensure accessibility on all device sizes.
- Announce status changes (accept/reject/fulfilled) where possible.

#### Telemetry (optional)
- Log key events (post request, accept/reject, fulfilled, money donated) without PII.

#### Seeder (dev)
- Purpose: populate a realistic dataset so flows can be tested end-to-end (Donor discovery, targeted/general requests, inbox actions, money donations).
- Behavior: destructive refresh. Deletes existing data under RTDB roots used by the app, then inserts the seed dataset only.
- How to run: `tsx scripts/seed.ts` (requires dev Firebase config). Optionally run with `SEED_EMAIL`/`SEED_PASSWORD` for authenticated writes; rules should allow seeding in dev.

- Dataset shape:
  - users/{uid}
    - 1 Patient (onboarding complete) in Karachi.
    - 6 Donors across Karachi/Lahore/Islamabad with varied genders and blood groups; 4 marked `available=true`, 2 `available=false`.
    - Example fields per user: { uid, name, email, gender, bloodGroup, city, phone, cnic?, available, createdAt, updatedAt }
  - requests/{id}
    - 1 open general request (city matches Patient), 1 targeted pending to an available donor, 1 accepted assigned to another donor.
    - Fields: { id, createdBy, patientName, requiredBloodGroup, city, gender?, hospital?, locationAddress?, locationLat?, locationLng?, unitsRequired?, neededBy?, notes?, requestedTo?, status, createdAt }
  - comments/{requestId}/{id}
    - 2–3 comments on the pending/accepted requests for UI testing.
    - Fields: { id, uid, text, createdAt }
  - donations/{uid}/{id}
    - For donors who accepted: create 1 blood donation intent with status "pending" or a past fulfilled record if needed for history.
    - Fields: { id, requestId, status, date }
  - money_donations/{uid}/{id}
    - Add 3–5 money donations across 2 users with varied amounts (e.g., 500, 1000, 2500 PKR) and optional purposes.
    - Fields: { id, uid, amount, currency: 'PKR', purpose?, createdAt, receiptUrl?, stripePaymentId?, stripeSessionId? }

- Index helpers (optional for scale testing):
  - user_requests/{uid}/{requestId}: true
  - donor_requests/{uid}/{requestId}: true
  - open_requests/{requestId}: true


#### Best Practices
- Only `lib/*` modules access Firebase; screens import these modules, not SDKs.
- Keep functions single-purpose (e.g., `acceptRequest` only changes assignee/status).
- Store ms epoch; convert to `Date` in UI only.
- Use optimistic UI where safe (availability toggle, comment post) and reconcile on settle.
- Plan for scalability with fan-out:
  - `user_requests/{uid}/{requestId}: true`
  - `donor_requests/{uid}/{requestId}: true`
  - `open_requests/{requestId}: true`
- Performance: batch reads, debounce search, avoid heavy listeners on tab roots.
- Accessibility: high contrast, large touch targets, announce status changes.
- Telemetry (optional): log key events (post, accept, reject, fulfill, money donate) without PII.
- Environment: document Firebase config and any env overrides in README; do not commit secrets.

#### **AI-Powered Features Plan (Gemini API via Backend)**

##### **Donor Badges & Gamification System**
- **AI Badge Recommendations**: Gemini analyzes donor behavior patterns and suggests personalized badges
- **Badge Categories**:
  - **Response Badges**: "Reliable Responder" (responds within 1 hour), "Quick Responder" (responds within 30 minutes)
  - **Donation Badges**: "Emergency Hero" (donates during critical hours), "Regular Donor" (monthly donations)
  - **Impact Badges**: "Life Saver" (saved 5+ lives), "Community Champion" (helps in multiple cities)
  - **Special Badges**: "Rare Blood Hero" (donates rare blood types), "Night Owl" (donates after hours)
- **Badge Behavior**:
  - **Automatic Assignment**: AI analyzes donation history, response times, and impact
  - **Real-time Updates**: Badges update as donor behavior changes
  - **Profile Display**: Badges shown on donor profile and in donor lists
  - **Motivation System**: Badges encourage repeat donations and better response rates

##### **Smart Notifications (AI-Powered Targeting)**
- **Intelligent Donor Selection**: Gemini analyzes donor availability, location, blood group, and response history
- **Smart Filtering Logic**:
  - **Location Priority**: Notify closest donors first (within 10km radius)
  - **Blood Group Match**: Only notify compatible blood group donors
  - **Availability Status**: Only notify donors marked as available
  - **Response History**: Prioritize donors with good response rates
  - **Time-based Filtering**: Consider donor's typical active hours
- **Notification Behavior**:
  - **Batch Size**: Maximum 10 donors per request (instead of notifying all 100)
  - **Priority Queue**: Closest + most responsive donors get notified first
  - **Fallback System**: If no response in 30 minutes, notify next batch
  - **Smart Timing**: Send notifications during donor's active hours

##### **Impact Summaries (NLP Storytelling)**
- **AI-Generated Stories**: Gemini creates personalized impact narratives
- **Story Types**:
  - **Personal Impact**: "Your 3 donations this year helped save 9 lives in Karachi"
  - **Community Impact**: "You're among the top 10% of donors in your city"
  - **Time-based Stories**: "This month, you responded to 2 emergency requests"
  - **Achievement Stories**: "You've maintained a 100% response rate for 6 months"
- **Story Generation**:
  - **Data Analysis**: AI analyzes donation history, response times, and patient outcomes
  - **Emotional Engagement**: Uses positive language and emotional triggers
  - **Visual Elements**: Stories include statistics, charts, and motivational messages
  - **Sharing Features**: Users can share their impact stories on social media

##### **Backend Architecture for AI Features**
- **Node.js Backend**: Express.js server handling Gemini API calls
- **Gemini API Integration**: Google's Gemini API for AI-powered features
- **API Endpoints**:
  - `POST /api/ai/analyze-donor-behavior`: Analyze donor data for badge recommendations
  - `POST /api/ai/smart-notifications`: Get smart donor selection for notifications
  - `POST /api/ai/generate-impact-story`: Generate personalized impact stories
  - `POST /api/ai/update-badges`: Update donor badges based on behavior
- **Data Processing**:
  - **Donor Analysis**: Process donation history, response times, location data
  - **Smart Filtering**: AI-powered donor selection for notifications
  - **Story Generation**: NLP processing for impact summaries
  - **Badge Logic**: Automated badge assignment based on behavior patterns

##### **AI Feature Implementation Details**

###### **Donor Badges System**
- **Badge Data Structure**:
  ```json
  {
    "badgeId": "reliable_responder",
    "name": "Reliable Responder",
    "description": "Responds to requests within 1 hour",
    "icon": "clock-icon",
    "color": "#4CAF50",
    "criteria": {
      "responseTime": "< 3600000", // 1 hour in milliseconds
      "minRequests": 5,
      "successRate": "> 0.8"
    },
    "earnedAt": "2024-01-15T10:30:00Z"
  }
  ```
- **Badge Assignment Process**:
  1. **Data Collection**: Gather donor's donation history, response times, success rates
  2. **AI Analysis**: Gemini analyzes patterns and suggests appropriate badges
  3. **Criteria Matching**: Check if donor meets badge requirements
  4. **Automatic Assignment**: Assign badges and update donor profile
  5. **Notification**: Notify donor of new badge achievement

###### **Smart Notifications System**
- **Donor Selection Algorithm**:
  1. **Filter Available Donors**: Only donors marked as available
  2. **Blood Group Matching**: Filter by compatible blood groups
  3. **Location Filtering**: Prioritize donors within 10km radius
  4. **Response History Analysis**: Rank by response rate and speed
  5. **Time-based Filtering**: Consider donor's active hours
  6. **AI Optimization**: Gemini selects top 10 most likely responders
- **Notification Queue Management**:
  - **Primary Batch**: Top 10 donors notified immediately
  - **Fallback System**: Next 10 donors notified after 30 minutes if no response
  - **Emergency Escalation**: All compatible donors notified for critical requests

###### **Impact Story Generation**
- **Story Data Structure**:
  ```json
  {
    "storyId": "impact_2024_q1",
    "type": "personal_impact",
    "title": "Your Impact This Quarter",
    "content": "Your 3 donations this year helped save 9 lives in Karachi...",
    "statistics": {
      "donations": 3,
      "livesSaved": 9,
      "responseTime": "45 minutes average",
      "rank": "Top 15% in your city"
    },
    "visualElements": ["chart", "badge", "timeline"],
    "generatedAt": "2024-01-15T10:30:00Z"
  }
  ```
- **Story Generation Process**:
  1. **Data Aggregation**: Collect donor's complete history
  2. **Pattern Analysis**: Identify key achievements and patterns
  3. **AI Processing**: Gemini generates personalized narrative
  4. **Emotional Enhancement**: Add motivational and emotional elements
  5. **Visual Integration**: Include charts, statistics, and visual elements
  6. **Delivery**: Present story in user's profile and history

##### **API Integration Specifications**
- **Gemini API Endpoints**:
  - **Badge Analysis**: `POST /v1/models/gemini-pro:generateContent`
  - **Smart Notifications**: `POST /v1/models/gemini-pro:generateContent`
  - **Story Generation**: `POST /v1/models/gemini-pro:generateContent`
- **Request Format**:
  ```json
  {
    "contents": [{
      "parts": [{
        "text": "Analyze this donor data and suggest appropriate badges: {donorData}"
      }]
    }],
    "generationConfig": {
      "temperature": 0.7,
      "maxOutputTokens": 1000
    }
  }
  ```
- **Response Processing**:
  - **JSON Parsing**: Extract structured data from Gemini responses
  - **Validation**: Ensure response meets expected format
  - **Database Updates**: Update Firebase with AI-generated content
  - **Error Handling**: Fallback to default behavior if AI fails

#### **Implementation Approach - Free Resources Only**

##### **Firebase Free Tier Usage**
- **Realtime Database**: Primary data storage (1GB free, 100 concurrent connections)
- **Authentication**: User management (unlimited users on free tier)
- **Hosting**: Static app hosting (10GB free)
- **No Cloud Functions**: Avoid serverless functions to stay within free limits
- **No Cloud Storage**: Use local storage for images and files

##### **Notification Strategy (Free Implementation)**
- **Primary Method**: Firebase Realtime Database listeners
- **No Push Notifications**: Avoid Firebase Cloud Messaging costs
- **In-App Only**: All notifications displayed within the app
- **Real-time Updates**: Instant updates via Firebase listeners
- **Offline Support**: Basic offline functionality using local storage

##### **Data Management Strategy**
- **Client-Side Filtering**: Filter data in the app to reduce Firebase reads
- **Pagination**: Implement client-side pagination to limit data transfer
- **Caching**: Use local storage to cache frequently accessed data
- **Soft Delete**: Mark records as deleted instead of removing them
- **Data Cleanup**: Automatically filter expired notifications client-side

##### **Performance Optimization**
- **Debounced Search**: Reduce Firebase queries during search
- **Batch Operations**: Group multiple operations to reduce API calls
- **Lazy Loading**: Load data only when needed
- **Image Optimization**: Compress images before storage
- **Minimal Dependencies**: Use only essential libraries to reduce bundle size

#### **Current Implementation Status**
- ✅ **Core Features**: User authentication, mode switching, basic request/accept flow
- ✅ **Targeted Requests**: Working correctly - targeted requests appear in donor inbox
- ✅ **Donor Inbox**: Properly displays targeted and discoverable requests
- ✅ **Header Actions**: Mode switch and availability toggle implemented
- ✅ **Theme System**: Light/dark theme support with persistence
- ✅ **Responsive Design**: Header adapts to screen sizes
- ✅ **Request Accept Flow**: Comprehensive accept flow with availability validation, button state management, and proper request removal
- 🔄 **In Progress**: Enhanced search, real-time updates, accessibility improvements
- 📋 **Planned**: Advanced filtering, notification system, offline support

#### **Recent Bug Fixes & Improvements**
- ✅ **Urgent Request Removal**: Accepted requests are immediately removed from urgent requests list
- ✅ **Request Cancellation**: Patients can cancel requests within 10 minutes of creation
- ✅ **Urgent Flag**: Added urgent flag to request data model for proper filtering
- ✅ **History Naming**: Renamed "Donation History" to "Request History" with proper mode-specific content
- ✅ **All Requests Display**: Fixed "All Requests" tab to show all open requests (urgent and non-urgent)
- ✅ **Clickable History**: All history items are now clickable to view full details
- ✅ **Active Filter Behavior**: Clarified "Active Only" filter behavior in donor list
- ✅ **Request Detail Actions**: "Accept" button only visible for donors, not patients
- ✅ **Header Consistency**: Request detail page header matches other pages layout
- ✅ **Accept Flow Validation**: Donors must be available to accept requests; accept button disabled when unavailable
- ✅ **Request Removal on Accept**: Accepted requests immediately disappear from all request lists
- ✅ **History Integration**: Accepted requests properly appear in both donor and patient history
- ✅ **Accept Flow API**: Added comprehensive API functions for accept flow validation and execution

#### **AI Features Implementation Timeline**

##### **Phase 1: Backend Setup (Week 1-2)**
- **Node.js Backend**: Set up Express.js server with Gemini API integration
- **API Endpoints**: Create AI-powered endpoints for badge analysis and smart notifications
- **Database Schema**: Add new tables for badges, impact stories, and AI analytics
- **Testing**: Test Gemini API integration and response processing

##### **Phase 2: Badge System (Week 3-4)**
- **Badge Logic**: Implement badge criteria and assignment algorithms
- **AI Integration**: Connect badge analysis to Gemini API
- **UI Components**: Create badge display components for profiles and donor lists
- **Real-time Updates**: Implement automatic badge updates based on behavior

##### **Phase 3: Smart Notifications (Week 5-6)**
- **Donor Selection**: Implement AI-powered donor selection algorithm
- **Notification Queue**: Create smart notification queuing system
- **Fallback System**: Implement fallback notification for non-responders
- **Performance Optimization**: Optimize for large donor databases

##### **Phase 4: Impact Stories (Week 7-8)**
- **Story Generation**: Implement AI-powered impact story generation
- **Data Analysis**: Create donor analytics and pattern recognition
- **Visual Elements**: Add charts, statistics, and visual story elements
- **Sharing Features**: Implement social media sharing for impact stories

##### **Cost Considerations**
- **Gemini API Costs**: 
  - **Free Tier**: 15 requests per minute, 1M tokens per month
  - **Paid Tier**: $0.0005 per 1K characters for input, $0.0015 per 1K characters for output
  - **Estimated Monthly Cost**: $10-50 for moderate usage (1000+ users)
- **Backend Hosting**:
  - **Free Options**: Railway, Render, Heroku (with limitations)
  - **Paid Options**: AWS, Google Cloud, DigitalOcean ($5-20/month)
- **Total Monthly Cost**: $15-70 for full AI features

#### **UI/UX Consistency Requirements**

##### **Header Layout Standardization**
- **Consistent Structure**: All pages must follow the same header layout pattern
  - Left: App logo/branding (40x40px with 8px border radius)
  - Center: Screen title (28px font, bold, theme-appropriate color)
  - Right: Action buttons (mode switch, availability toggle, etc.)
- **Minimum Height**: 60px to accommodate toggle switches without text overlap
- **Padding**: 16px horizontal padding for consistent spacing
- **Theme Support**: Headers must adapt to light/dark theme changes

##### **Action Button Visibility Rules**
- **Mode-Based Actions**: Action buttons visibility based on user's current mode
  - **Donor Mode**: Show availability toggle, accept request buttons
  - **Patient Mode**: Hide donor-specific actions, show request creation actions
- **Role-Based Actions**: Actions based on user's relationship to content
  - **Request Creator**: Can cancel, mark fulfilled, view donor profiles
  - **Targeted Donor**: Can accept/reject targeted requests
  - **General Donor**: Can accept open requests
  - **Non-Donor**: Cannot see accept buttons on request details

##### **Filter Behavior Specifications**
- **"Active Only" Filter**: 
  - **Enabled**: Shows only users with `available: true` status
  - **Disabled**: Shows all users regardless of availability status
  - **Visual Indicator**: Clear toggle state with descriptive text
  - **Persistence**: Filter state should persist during session

#### **Next Phase Improvements**
1. 🔄 **Enhanced Search**: Real-time search with debouncing for better performance
2. 🔄 **Real-time Updates**: Automatic refresh for new requests and status changes
3. 🔄 **Advanced Filtering**: Multi-criteria filtering for donors and requests
4. ✅ **Notification System**: In-app notifications using Firebase free tier
5. ✅ **AI Badge System**: Gamification with AI-powered badge recommendations
6. ✅ **Smart Notifications**: AI-optimized donor selection for notifications
7. ✅ **Impact Stories**: AI-generated personalized impact narratives
8. 📋 **Offline Support**: Data persistence for better user experience
9. 📋 **Accessibility**: Screen reader support and keyboard navigation