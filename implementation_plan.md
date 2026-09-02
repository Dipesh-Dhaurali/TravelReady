# Admin Panel Finalization Plan

## Goal Description
Finalize the admin dashboard for the TravelReady project so that it is fully functional, professional‑looking, and bug‑free before the hosting deadline. All admin features must correctly persist data to the database, handle image uploads, and mirror any essential user‑panel capabilities. The admin UI should use a consistent theme, proper navigation, and responsive design.

## User Review Required
> [!IMPORTANT] **Critical decisions needing your input**
> - **Image upload handling**: Should images be stored using Django's default `MEDIA_ROOT` with `FileField/ImageField` on the relevant models (e.g., `Package`, `Destination`, `Hotel`), or do you prefer a custom storage (e.g., S3)?
> - **Admin authentication**: Do you want a separate super‑admin login (different from user login) or reuse the existing `accounts` login with staff flag?  
> - **Feature parity**: Should the admin also expose the "My Bookings" view, payment verification, and quotation request management? Confirm any additional user‑panel features you want duplicated in admin.
> - **Theme choice**: The admin templates have been updated to use the new CSS classes (`admin-card`, `btn-admin-primary`, etc.). Do you want a dark mode variant or keep the current light theme?

## Open Questions
> [!CAUTION] **Potential blockers**
> 1. **Image upload size limits** – Do you have a max‑file‑size requirement?
> 2. **Payment integration** – The `payments:payment_page` URL currently expects a numeric `booking_id`. Should we adjust the URL regex to accept the alphanumeric IDs used by the system (`TRV-2026-00002`)?
> 3. **Namespace conflicts** – Some admin URLs (`/dashboard/admin/...`) clash with user dashboard URLs (`/dashboard/...`). Should we rename the admin namespace to `admin_dashboard` to avoid future `NoReverseMatch` errors?
> 4. **Testing scope** – Do you want automated Selenium/Playwright UI tests, or is manual functional testing sufficient before deployment?

## Proposed Changes
---
### 1️⃣ URL & View Clean‑up
- **Update root `urls.py`** to separate admin and user namespaces (`dashboard` vs `admin_dashboard`).
- **Fix `payment_page` URL regex** to accept alphanumeric booking IDs (`[A-Z0-9-]+`).
- **Add missing admin booking views** (`admin_bookings_list`, `admin_booking_detail`, `admin_booking_status_update`).
- **Add admin image upload endpoints** for packages, destinations, hotels.

### 2️⃣ Admin Templates & CSS
- Ensure every admin template extends `dashboard/base_admin.html` and uses the new CSS classes (`admin-card`, `btn-admin-primary`, `stat-card`, `extra-small`).
- Add a responsive sidebar component with active‑link detection for nested URLs.
- Add a dark‑mode toggle (optional, based on your answer).

### 3️⃣ Forms & Image Handling
- Add `ImageField` to `Package`, `Destination`, `Hotel` models if not present.
- Create/Update ModelForm classes to include `enctype="multipart/form-data"` in admin create/edit templates.
- Configure `MEDIA_URL` and `MEDIA_ROOT` in `settings.py` and add `django.conf.urls.static.static` in dev URLs.

### 4️⃣ Data Persistence Checks
- Write unit tests for each admin CRUD view to verify objects are saved, updated, and deleted correctly.
- Verify that image files are saved and displayed on both admin and user pages.

### 5️⃣ Synchronize Feature Set
- Mirror user‑panel functionalities in admin where appropriate:
  * Booking creation and status management
  * Payment verification and receipt generation
  * Quotation request handling
- Add admin‑only actions (approve/reject bookings, bulk email, export CSV).

### 6️⃣ Full Test Run
- Run `python manage.py check` and `python manage.py test`.
- Manual walkthrough:
  1. Log in as super‑admin → access admin dashboard.
  2. Create a package with an image → view on user side.
  3. Book the package → verify admin can see booking, change status, and generate receipt.
  4. Navigate all admin pages to ensure no 404/500 errors.
- Capture screenshots for the walkthrough artifact.

### 7️⃣ Deployment Prep
- Ensure static files are collected (`python manage.py collectstatic`).
- Verify `ALLOWED_HOSTS`, `DEBUG=False`, and proper database migrations.

## Verification Plan
### Automated Tests
- `manage.py test apps.packages.tests.AdminPackageTests`
- `manage.py test apps.bookings.tests.AdminBookingTests`
- `manage.py test apps.payments.tests.PaymentUrlTests`

### Manual Verification
- Log in as admin and walk through every navigation item.
- Upload images for packages/destinations and confirm they appear on the public site.
- Process a sample booking end‑to‑end (user → admin → payment).
- Validate that no `NoReverseMatch` errors appear in the console.

---
*Once you approve the plan and clarify the open questions, I will proceed with the implementation.*
