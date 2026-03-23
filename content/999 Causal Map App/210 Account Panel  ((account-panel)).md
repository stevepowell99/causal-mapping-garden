<div class="user-guide-callout">
<strong>👤 What you can do here:</strong> View and manage your personal account settings. Change your password, update your project information, and control your privacy and security settings. This is also where you can export your data or delete your account if needed.
</div>

<span class="badge bg-info text-dark" style="margin-left:6px;">Making projects private requires a Private subscription</span>

User account management and project settings.

**Onboarding (first sign-up):** When you sign up, we ask a few questions including whether you want AI options switched on and active right at the start. If you choose No, there are no AI services at all (except basic MapCat help); you can change this anytime in Account settings. If you choose Yes, you get 10 free AI credits per month, and the Simple AI switch is turned on by default; you can turn it off later in Account settings.

**AI coding toggle ("AI options switched on and active"):** Turn on to use AI; turn off and there are no AI services at all (except basic MapCat help). You can change this anytime in Account settings. When you turn it **on**, a warning modal appears: your data is sent to AI providers when you use AI; it is **not** used to train models; OpenAI (GPT) may retain data for up to 30 days for abuse monitoring; Vertex AI and DashScope do not retain data; see our [privacy policy](https://www.causalmap.app/privacy-policy/). Credits when on depend on your plan (Free: 10, Private: 100, Pro: 1000, Team: 2000/month). **Plans without AI** (e.g. Private Manual) can turn on to try with 10 credits/month (free credits do not stack with paid AI plans).

**Account Features:**
- <i class="fas fa-user"></i> project information and settings
- <i class="fas fa-key"></i> Password and security management
- Account deletion and data export
- Subscription and billing information

### 2FA (beginner guide)

If your organisation asks you to use 2FA, do this in **Account → Two-factor authentication**:

1. Turn on **Require two-factor authentication on sign-in**.
2. Sign out, then sign in again.
3. If asked, scan the QR code in your authenticator app.
4. Enter the 6-digit code to finish setup.

If codes do not work:
- Try a different Causal Map entry in your authenticator (you may have old entries).
- Use **Delete all 2FA factors** in the same card, then sign out/in and set up again.

For strict org policy:
- Click **Require 2FA permanently**.
- This is one-way in the app UI and keeps 2FA locked on for that account.

### Image export resolution

Controls resolution for all image capture (map copy/download, bookmarks, pivot/table screenshots, PDF export). Options: 1× (default), 2×, 3×. Resets to 1× on page load. **1× is already very good** for most uses; higher values produce larger files and may hit clipboard limits on large maps.

### Subscriptions

#### Subscriptions List

Users without a subscription are either:
- anonymous (not logged in) (this is disabled at present)
- free (logged in)

Subscriptions (via LemonSqueezy) are available in the Account panel.

Admins can also create **manual subscriptions** (for testing/support). These are stored in the same `subscriptions_purchased` table but do **not** come from Lemon Squeezy.

The subscriptions list uses one row per type (private, pro, team) with seat-count, square radio buttons for monthly/annual and Manual/AI, and a live-updating price (from a JSON price file). Each row includes a text description.

<!-- Pricing details:
- Annual price = 8 × monthly rate
- Seats dropdown: 1–100
- Multi-seat discount: total × n^0.9
- Price display updates when Add AI is toggled to include AI price
-->

There are three dimensions to the subscriptions, 

Manual vs AI,  

Type:
- private
- pro
- team

Monthly vs Annual.

**AI credits (when you have AI):** Free users who opt in get 10 credits/month. Private AI: 100. Pro AI: 1000. Team: 2000. Credits renew at the start of each month and do not roll over. See [Responses Panel](../responses-panel/) for usage. Plans without AI (e.g. Private Manual) can turn on the AI toggle in Account to try with 10 credits/month. 

User can purchase multiples of one or more subs to distribute to colleagues. 

<!--
Types are selectable with options in the gallery; purchases are simulated for now to streamline evaluation.

Underlying storage uses Supabase tables. Each user can buy more than one subscription and allocate seats to colleagues' emails. Data captured includes manager email, subscriber emails (JSON), date, duration, and number of seats.


Each subscription row has a seat-count dropdown (1–100). After purchase, a modal collects subscriber emails, prefilling the first with the current user's email. 



--#### Subscriptions Table


The Subscriptions card shows a single simple table listing subscriptions where you are manager or subscriber, including manager email, subscriber emails, and other details, with an Edit button (for subscriptions you manage) that opens the subscriber-email modal.

**Renewals (Lemon Squeezy):** your renewal dates are synced automatically when you open/refresh the app while signed in. Admins can also manually trigger a sync per subscription from the table.


The subscriber-email modal pre-fills the first slot with the current user's email and validates against the purchased seat count, indicating if there are remaining seats or too many emails.


The admin tab includes a Subscriptions overview table (Tabulator) with header filters, sorting, and server-side pagination.

See also Gating in Technical dletails section below

Lemon Squeezy (LS) integration (first step):
- A new button appears in the Account tab: "Buy Private (Monthly, no AI) via Lemon Squeezy".
- On click, it opens the Lemon Squeezy checkout in a new tab for the Private/Monthly/Manual variant.
- On success, the app records the purchase using the existing subscriptions flow (same as the simulated purchase), so your allocation shows up immediately.

Frontend configuration (override in `webapp/env-config.local.js`):
```js
window.ENV = {
    LEMONSQUEEZY_STORE_DOMAIN: 'causal-map', // your LS store subdomain
    LS_VARIANT_ID_PRIVATE_MONTHLY_MANUAL: ''   // the variant ID slug or UUID
}
```

Notes:
- Only administrators can click purchase (same gating as the simulated buttons).
- We reuse the existing email collection modal to allocate the first seat.
- This is a minimal frontend-only integration (no webhooks yet). Renewals are synced on app load via an Edge Function; admins can manually force a sync for any subscription row.

<!--
Renewal sync (LS → Supabase DB):
- Edge Function: `supabase/functions/lemonsqueezy` action `sync_customer_subscriptions`
- Security: requires a valid Supabase user JWT; allowed only for:
  - admins, OR
  - the user syncing their own email
- What it updates: `subscriptions_purchased.end_date` only (do NOT sync LS `status` because DB has a strict check constraint)
- IMPORTANT: Manual/admin-created subscriptions exist and are not tied to LS. The sync is designed to be safe:
  - It will never set `end_date` earlier than the local row’s `start_date` (prevents end<start).
  - It will never shorten `end_date` (sync is renewal-only).
- Automatic trigger: app boot `loadProjects` calls `DataService.syncMyCustomerSubscriptions()` before computing `getEffectiveSubscriptionStatus()`
- Throttle: client-side localStorage TTL (currently 6 hours per user per mode) to avoid frequent LS API calls
- Admin UX: "Your subscriptions" table shows an admin-only "Sync LS" button per row (syncs by that row’s manager email)
-->

-->