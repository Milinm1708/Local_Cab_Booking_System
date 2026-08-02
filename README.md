# 🚕 LocalRide — Local Cab Booking Platform

A complete, Uber-style local cab booking website built **entirely on free and open
technology** — no paid map APIs, no paid services, no cloud billing.

- **Frontend:** HTML5, CSS3, vanilla JavaScript (+ Leaflet.js, Chart.js from free CDNs)
- **Backend:** Python 3 + Django 6
- **Database:** SQLite (zero configuration, single file)
- **Maps:** OpenStreetMap tiles + Nominatim geocoding + Leaflet.js (100% free, no API key)
- **Email:** Django's console backend (prints emails to the terminal — no SMTP needed)

---

## ✨ Features

### Customer
- Registration & login, profile editing with photo upload
- Book a ride: search or click-to-drop pickup/drop pins on a live Leaflet/OSM map
- Live fare & ETA estimate for Mini / Sedan / SUV before booking
- Ride history with search & status filters, cancel active rides
- Ride tracking page with a status stepper (Requested → Accepted → Ongoing → Completed)
- Rate & review completed rides (1–5 stars + comment)

### Driver
- Driver registration with license + vehicle details (pending admin approval)
- Driver dashboard: go online/offline, view & accept/skip nearby ride requests
- Manage ride status: Accept → Start → Complete
- Vehicle details management page
- Earnings page with total earnings, rating, and a completed-rides ledger

### Admin (custom admin panel, separate from Django's built-in `/django-admin/`)
- Dashboard with KPIs (riders, drivers, pending approvals, revenue) + Chart.js graphs
- Manage Users: search, block/unblock riders
- Manage Drivers: search & filter by status, **approve/reject** driver applications
- Manage Bookings: search & filter every ride on the platform
- Reports page: daily revenue trend chart + top-earning drivers

### Cross-cutting
- Dark/Light theme toggle (persisted via `localStorage`)
- Fully responsive layout (mobile / tablet / desktop)
- Toast notifications, loading spinner overlay, smooth CSS transitions
- Server-side form validation + friendly inline error messages
- Role-based access control (customer / driver / admin) via a custom decorator
- Console-based email notifications for booking, driver approval, contact form, etc.

---

## 🗂 Project Structure

```
localride/
├── manage.py
├── requirements.txt
├── db.sqlite3                  # pre-seeded SQLite database (safe to delete & reseed)
├── localride/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── core/                       # Home / About / Contact + seed_data command
│   ├── models.py               # ContactMessage
│   ├── views.py
│   ├── context_processors.py   # exposes is_customer / is_driver / is_admin_role
│   └── management/commands/seed_data.py
├── accounts/                   # Users, Drivers, Vehicles + all dashboards
│   ├── models.py                # User (custom AbstractUser), Driver, Vehicle
│   ├── forms.py
│   ├── views.py                 # registration, profile, all 3 dashboards, admin panel
│   ├── decorators.py             # @role_required('customer' | 'driver' | 'admin')
│   └── urls.py
├── rides/                       # Ride booking & lifecycle
│   ├── models.py                 # Ride, Payment, Review
│   ├── utils.py                   # haversine distance + fare formula
│   ├── views.py                   # book/cancel/accept/start/complete/review + fare API
│   └── urls.py
├── templates/
│   ├── base.html                  # navbar, footer, toasts, loader, dark-mode
│   ├── core/                      # home, about, contact
│   ├── accounts/                  # register, login, profile, vehicle, earnings
│   ├── rides/                     # book_ride (map), ride_history, ride_detail
│   ├── dashboards/                 # customer / driver / admin dashboards
│   └── admin_panel/                # manage_users, manage_drivers, manage_bookings, reports
├── static/
│   ├── css/style.css                # full design system (CSS variables, dark mode)
│   └── js/
│       ├── main.js                  # theme toggle, mobile nav, toasts, star rating
│       ├── map.js                   # Leaflet + Nominatim booking map & live fare calls
│       └── dashboard-charts.js      # Chart.js helpers (donut/bar/line)
└── media/                            # uploaded profile photos
```

---

## 🚀 Setup Instructions (step by step)

### 1. Prerequisites
- Python 3.10+ installed
- `pip` available on your PATH

### 2. Unzip & enter the project
```bash
unzip localride.zip
cd localride
```

### 3. (Recommended) Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Apply database migrations
The project ships with a ready-to-use `db.sqlite3`, but if you deleted it or want a
fresh database, run:
```bash
python manage.py migrate
```

### 6. Load sample/test data (optional but recommended)
This creates an admin, 5 riders, 5 drivers (with vehicles, 2 pending approval),
15 sample rides with payments & reviews:
```bash
python manage.py seed_data
```

### 7. Run the development server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your browser.

### 8. Log in with demo accounts
| Role   | Username  | Password      | Notes                                  |
|--------|-----------|---------------|-----------------------------------------|
| Admin  | `admin`   | `admin123`    | Full custom admin panel + Django admin |
| Rider  | `rider1`  | `rider12345`  | `rider2`…`rider5` also available        |
| Driver | `driver1` | `driver12345` | `driver1`–`driver3` are pre-approved; `driver4`/`driver5` are pending, to test the approval flow |

Django's built-in admin is also available at **`/django-admin/`** using the same
`admin` / `admin123` credentials.

### 9. Watch email notifications
This project uses Django's **console email backend** — booking confirmations, driver
approval emails, and contact-form notifications are printed directly into the terminal
running `runserver`. No SMTP setup required.

---

## 🧭 Using the App

1. **As a rider:** Sign up → *Book a Ride* → search/click pickup & drop on the map →
   pick Mini/Sedan/SUV → see live fare → *Confirm booking* → track status on the
   ride detail page → rate once completed.
2. **As a driver:** Sign up (submits for approval) → once an admin approves you,
   go *Online* → accept a pending request → *Start ride* → *Complete ride* → see
   earnings update instantly.
3. **As an admin:** Log in as `admin` → dashboard KPIs & charts → *Manage Drivers* to
   approve/reject applicants → *Manage Users* to block/unblock riders → *Manage
   Bookings* to audit every ride → *Reports* for revenue trends.

---

## 💰 How Fare Estimation Works (no paid pricing API)

1. **Distance** — the great-circle (haversine) distance between pickup and drop
   coordinates, computed server-side in `rides/utils.py`.
2. **Duration** — distance ÷ an assumed average city speed (28 km/h).
3. **Fare formula:**
   ```
   fare = (BASE_FARE + PER_KM_RATE × distance_km + PER_MIN_RATE × duration_min) × vehicle_multiplier
   ```
   Defaults (edit in `localride/settings.py`):
   - `FARE_BASE = 40`, `FARE_PER_KM = 12`, `FARE_PER_MIN = 1.5`
   - Multipliers: Mini `1.0`, Sedan `1.35`, SUV `1.75`

The live map calls `/rides/fare-estimate/` (AJAX/JSON) on every pin move or vehicle
selection so riders always see the price before confirming.

---

## 🗺️ About the Maps

- Map tiles: `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png` (OpenStreetMap, free)
- Geocoding & reverse-geocoding: `nominatim.openstreetmap.org` (OpenStreetMap's free
  search service — please keep usage light/personal per their
  [usage policy](https://operations.osmfoundation.org/policies/nominatim/))
- Routing on the map is drawn as a straight dashed line between pickup and drop for
  simplicity; distance/fare math uses the great-circle distance. If you want real
  road-routing, you can self-host an OSRM instance (also free/open-source) and swap
  the polyline logic in `static/js/map.js`.

---

## 🛠 Extending the Project

- **Real routing:** self-host OSRM or GraphHopper (both open-source) and call them
  from `map.js` instead of drawing a straight line.
- **Real-time updates:** add Django Channels + WebSockets for live driver location
  and instant ride-status pushes instead of manual page refresh.
- **Payments:** the `Payment` model already supports `cash` / `wallet` / `card` —
  wire up a sandbox payment gateway if needed.
- **Production deployment:** set `DEBUG = False`, configure `ALLOWED_HOSTS`, generate
  a new `SECRET_KEY`, switch to PostgreSQL if you outgrow SQLite, run
  `python manage.py collectstatic`, and serve behind Gunicorn + Nginx.

---

## 📋 Database Models Summary

| Model      | App      | Key fields |
|------------|----------|------------|
| `User`     | accounts | custom `AbstractUser` + `role` (customer/driver/admin), phone, address, photo |
| `Driver`   | accounts | license, experience, status, `is_approved`, `total_earnings` |
| `Vehicle`  | accounts | type (mini/sedan/suv), make/model, plate, color, seats |
| `Ride`     | rides    | pickup/drop address + lat/lng, distance, fare, status, timestamps |
| `Payment`  | rides    | amount, method, status, linked 1:1 to `Ride` |
| `Review`   | rides    | rating (1–5), comment, linked 1:1 to `Ride` |
| `ContactMessage` | core | name, email, subject, message (from the Contact page) |

---

## ⚠️ Disclaimer

This is a learning / portfolio / final-year project. It is **not** a production ride-
dispatch system — there's no real-time driver location tracking, no payment
processing, and no production-grade security hardening. Treat `SECRET_KEY`, `DEBUG`,
and `ALLOWED_HOSTS` accordingly before deploying anywhere public.
