# TravelReady — System Diagram Specifications (`images.md`)

This document provides exhaustive, step-by-step specifications for constructing the **Use Case Diagram** and **Entity-Relationship (ER) Diagram** for the **TravelReady** system. Use these specifications to easily draw the diagrams in tools such as **Draw.io**, **Lucidchart**, **StarUML**, or **Visual Paradigm**.

---










## 🎭 1. Use Case Diagram Specification

### 1.1 System Boundary & Actors

#### **System Boundary**: `TravelReady Web Application`

#### **Primary Actors**:
1. **Unregistered Visitor**:
   - An unauthenticated user browsing the public web portal.
2. **Registered Customer**:
   - An authenticated customer who registers, creates custom trips, books packages/tickets, makes payments, and tracks bookings.
3. **Travel Manager / Staff Admin**:
   - A non-technical agency staff member who manages inventory (destinations, hotels, packages), reviews custom trip requests, sets custom quotes, verifies payment receipts, and views sales analytics.

#### **Secondary / System Actors**:
4. **Superadmin**:
   - Low-level database and permission manager (built-in Django Admin).
5. **Payment Gateway / Bank**:
   - External entity for eSewa, Khalti, and Bank Transfer receipts.

---

### 1.2 Use Cases & Association Matrix

| Use Case ID | Use Case Name | Primary Actor(s) | Description | Includes / Extends |
|---|---|---|---|---|
| **UC-01** | Browse Destinations & Packages | Visitor, Customer | View inside/outside country destinations, hotels, activities, predefined packages. | None |
| **UC-02** | Register & Login | Visitor, Customer | Create an account or log in via session authentication. | None |
| **UC-03** | Calculate Live Package Price | Visitor, Customer | Dynamically recalculate trip cost based on days, travelers, hotel category, and activities via HTMX. | `<<extend>>` UC-01 |
| **UC-04** | Build Custom Trip | Customer | Select multiple destinations, allocate days per place, customize hotel tier, transport, and activities. | `<<include>>` UC-03 |
| **UC-05** | Save Custom Trip | Customer | Save a custom multi-destination itinerary to dashboard. | `<<include>>` UC-04 |
| **UC-06** | Submit Custom Quotation Request | Customer | Submit special route requirements, dietary requests, or budget targets for manager review. | None |
| **UC-07** | Book Tour Package / Custom Trip | Customer | Select dates, traveler counts, emergency contacts, and initialize checkout. | `<<include>>` UC-02 |
| **UC-08** | Book Standalone Ticket | Customer | Search and reserve Bus or Domestic/International Flight tickets. | `<<include>>` UC-02 |
| **UC-09** | Make Payment & Upload Receipt | Customer | Choose Full Payment or 30% Advance Deposit via eSewa, Khalti, or Bank Transfer (with voucher upload). | `<<include>>` UC-07 |
| **UC-10** | Track Booking Progress Timeline | Customer | View real-time 5-step visual progress bar (`Request Received` → `Trip Completed`). | None |
| **UC-11** | Download Digital Itinerary | Customer | Auto-generate and download a printable Day-by-Day itinerary schedule. | `<<extend>>` UC-10 |
| **UC-12** | Manage Wishlist & Profile | Customer | Save destinations to wishlist and update profile attributes/avatars. | None |
| **UC-13** | View Sales & Revenue Analytics | Travel Manager | View dashboard stat cards for total revenue, total bookings, pending payments, and quotes. | `<<include>>` UC-02 |
| **UC-14** | CRUD Destinations & Packages | Travel Manager, Superadmin | Add, edit, toggle, or delete destinations, hotels, transport routes, and packages. | None |
| **UC-15** | Process Custom Quotation Requests | Travel Manager | Review user custom requests, calculate custom prices, input admin notes, and send quotes. | None |
| **UC-16** | Verify Payments & Confirm Bookings | Travel Manager | Inspect uploaded bank deposit slips, approve/reject payments, mark booking `CONFIRMED`. | None |

---

### 1.3 Use Case Diagram (Visual Diagram in Mermaid)

```mermaid
graph LR
    subgraph System Boundary: TravelReady Application
        UC1([UC-01: Browse Destinations & Packages])
        UC2([UC-02: Register & Login])
        UC3([UC-03: Calculate Live Price HTMX])
        UC4([UC-04: Build Custom Trip])
        UC5([UC-05: Save Custom Trip])
        UC6([UC-06: Submit Custom Quote Request])
        UC7([UC-07: Book Package / Custom Trip])
        UC8([UC-08: Book Standalone Bus/Flight Ticket])
        UC9([UC-09: Upload Payment Voucher])
        UC10([UC-10: Track Booking Timeline])
        UC11([UC-11: Download Digital Itinerary])
        UC12([UC-12: Manage Wishlist & Profile])
        UC13([UC-13: View Sales & Revenue Analytics])
        UC14([UC-14: CRUD Destinations & Packages])
        UC15([UC-15: Process Custom Quotes])
        UC16([UC-16: Verify Payments & Confirm Bookings])
    end

    %% Visitor Connections
    Visitor((Unregistered Visitor)) --> UC1
    Visitor --> UC2

    %% Customer Connections
    Customer((Registered Customer)) --> UC1
    Customer --> UC2
    Customer --> UC3
    Customer --> UC4
    Customer --> UC5
    Customer --> UC6
    Customer --> UC7
    Customer --> UC8
    Customer --> UC9
    Customer --> UC10
    Customer --> UC11
    Customer --> UC12

    %% Staff / Admin Connections
    Staff((Travel Manager / Staff)) --> UC13
    Staff --> UC14
    Staff --> UC15
    Staff --> UC16

    %% Relationships
    UC3 -. "<<extend>>" .-> UC1
    UC4 -. "<<include>>" .-> UC3
    UC5 -. "<<include>>" .-> UC4
    UC7 -. "<<include>>" .-> UC2
    UC8 -. "<<include>>" .-> UC2
    UC9 -. "<<include>>" .-> UC7
    UC11 -. "<<extend>>" .-> UC10
```



















---

## 🗂️ 2. Entity-Relationship (ER) Diagram Specification

### 2.1 Entities & Attributes Table

| Entity Name | Entity Type | Primary Key (PK) | Attributes & Types | Foreign Keys (FK) & Target Entity |
|---|---|---|---|---|
| **User** | Strong | `id` (Integer) | `username` (Var), `email` (Var), `password` (Var), `is_staff` (Bool) | None (Built-in Django Auth User) |
| **UserProfile** | Weak | `id` (Integer) | `phone` (Var), `address` (Text), `profile_picture` (Image), `date_of_birth` (Date) | `user_id` → `User.id` (1:1 Unique) |
| **Destination** | Strong | `id` (Integer) | `name` (Var), `slug` (Slug), `destination_type` (Enum), `location` (Var), `district` (Var), `base_visit_cost` (Decimal), `best_season` (Var), `status` (Var) | None |
| **DestinationGallery** | Weak | `id` (Integer) | `image` (Image) | `destination_id` → `Destination.id` (N:1) |
| **Hotel** | Strong | `id` (Integer) | `name` (Var), `category` (Enum), `per_night_rate` (Decimal), `room_types` (Var) | `destination_id` → `Destination.id` (N:1) |
| **Activity** | Strong | `id` (Integer) | `title` (Var), `adult_price` (Decimal), `child_price` (Decimal), `duration_hours` (Decimal) | `destination_id` → `Destination.id` (N:1) |
| **Transportation** | Strong | `id` (Integer) | `route_origin` (Var), `vehicle_type` (Enum), `per_person_price` (Decimal), `per_vehicle_price` (Decimal) | `destination_id` → `Destination.id` (N:1) |
| **PredefinedPackage** | Strong | `id` (Integer) | `title` (Var), `slug` (Slug), `package_type` (Enum), `base_days` (Int), `base_price` (Decimal), `per_day_extra_cost` (Decimal), `is_popular` (Bool) | `destination_id` → `Destination.id` (N:1), `hotel_id` → `Hotel.id` (N:1) |
| **PackageActivity** | Join | `id` (Integer) | Join table for Many-to-Many activities | `package_id` → `PredefinedPackage.id`, `activity_id` → `Activity.id` |
| **CustomTrip** | Strong | `id` (Integer) | `trip_name` (Var), `total_days` (Int), `hotel_category` (Enum), `adults_count` (Int), `children_count` (Int), `total_price` (Decimal), `status` (Enum) | `user_id` → `User.id` (N:1) |
| **CustomTripDestination**| Join | `id` (Integer) | `stay_duration_days` (Int), `order` (Int) | `custom_trip_id` → `CustomTrip.id` (N:1), `destination_id` → `Destination.id` (N:1) |
| **CustomQuotationRequest**| Strong | `id` (Integer) | `desired_route` (Text), `travellers_count` (Int), `budget` (Decimal), `admin_quoted_price` (Decimal), `generated_itinerary` (Text), `status` (Enum) | `user_id` → `User.id` (N:1) |
| **Booking** | Strong | `id` (Integer) | `booking_id` (Var: `TRV-YYYY-XXXXX`), `travel_date` (Date), `return_date` (Date), `adults_count` (Int), `children_count` (Int), `total_cost` (Decimal), `status` (Enum), `payment_verified` (Bool) | `user_id` → `User.id` (N:1), `package_id` → `PredefinedPackage.id` (Optional N:1), `custom_trip_id` → `CustomTrip.id` (Optional N:1) |
| **StandaloneTicket** | Strong | `id` (Integer) | `ticket_number` (Var: `TKT-YYYY-XXXXX`), `ticket_type` (Enum), `origin` (Var), `destination` (Var), `travel_date` (Date), `price` (Decimal), `status` (Enum) | `user_id` → `User.id` (N:1) |
| **TicketSchedule** | Strong | `id` (Integer) | `ticket_type` (Enum), `operator_name` (Var), `origin` (Var), `destination` (Var), `departure_time` (Time), `price_per_person` (Decimal), `available_seats` (Int) | None |
| **Payment** | Strong | `id` (Integer) | `payment_ref` (Var: `PAY-YYYYMMDD-XXXXX`), `amount` (Decimal), `payment_option` (Enum), `payment_method` (Enum), `transaction_ref` (Var), `payment_receipt` (Image), `verification_status` (Enum) | `booking_id` → `Booking.id` (Optional N:1), `ticket_id` → `StandaloneTicket.id` (Optional N:1), `user_id` → `User.id` (N:1) |
| **Wishlist** | Join | `id` (Integer) | `added_at` (DateTime) | `user_id` → `User.id` (N:1), `destination_id` → `Destination.id` (N:1) |

---

### 2.2 Entity Relationships & Cardinalities Summary

1. **User to UserProfile**: `1 : 1` (One User has exactly One Profile).
2. **User to Booking**: `1 : N` (One User can place zero or many Bookings).
3. **User to CustomTrip**: `1 : N` (One User can construct zero or many Custom Trips).
4. **User to CustomQuotationRequest**: `1 : N` (One User can request zero or many Quotations).
5. **User to StandaloneTicket**: `1 : N` (One User can reserve zero or many Tickets).
6. **User to Wishlist**: `1 : N` (One User can save zero or many Wishlist items).
7. **Destination to Hotel**: `1 : N` (One Destination has one or many Hotels).
8. **Destination to Activity**: `1 : N` (One Destination offers zero or many Activities).
9. **Destination to Transportation**: `1 : N` (One Destination has zero or many Transportation routes).
10. **Destination to DestinationGallery**: `1 : N` (One Destination has zero or many Gallery Images).
11. **Destination to PredefinedPackage**: `1 : N` (One Destination features zero or many Predefined Packages).
12. **PredefinedPackage to Hotel**: `N : 1` (Many Packages can specify One Hotel tier).
13. **PredefinedPackage to Activity**: `M : N` (Many Packages contain Many Activities).
14. **CustomTrip to CustomTripDestination**: `1 : N` (One Custom Trip consists of ordered Destination stays).
15. **Booking to Payment**: `1 : N` (One Booking can have initial partial deposit + final balance Payments).
16. **StandaloneTicket to Payment**: `1 : N` (One Ticket booking has one or more Payments).

---

### 2.3 Visual Entity-Relationship Diagram (Mermaid Format)

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string email
        string password
        boolean is_staff
    }

    USER_PROFILE {
        int id PK
        int user_id FK
        string phone
        text address
        string profile_picture
        date date_of_birth
    }

    DESTINATION {
        int id PK
        string name
        string slug
        string destination_type
        string location
        string district
        decimal base_visit_cost
        string best_season
        string status
    }

    HOTEL {
        int id PK
        int destination_id FK
        string name
        string category
        decimal per_night_rate
    }

    ACTIVITY {
        int id PK
        int destination_id FK
        string title
        decimal adult_price
        decimal child_price
    }

    TRANSPORTATION {
        int id PK
        int destination_id FK
        string route_origin
        string vehicle_type
        decimal per_person_price
        decimal per_vehicle_price
    }

    PREDEFINED_PACKAGE {
        int id PK
        int destination_id FK
        int hotel_id FK
        string title
        string package_type
        int base_days
        decimal base_price
    }

    CUSTOM_TRIP {
        int id PK
        int user_id FK
        string trip_name
        int total_days
        string hotel_category
        int adults_count
        int children_count
        decimal total_price
        string status
    }

    CUSTOM_TRIP_DESTINATION {
        int id PK
        int custom_trip_id FK
        int destination_id FK
        int stay_duration_days
        int order
    }

    CUSTOM_QUOTATION_REQUEST {
        int id PK
        int user_id FK
        text desired_route
        int travellers_count
        decimal budget
        decimal admin_quoted_price
        string status
    }

    BOOKING {
        int id PK
        string booking_id
        int user_id FK
        int package_id FK
        int custom_trip_id FK
        date travel_date
        date return_date
        decimal total_cost
        string status
        boolean payment_verified
    }

    STANDALONE_TICKET {
        int id PK
        string ticket_number
        int user_id FK
        string ticket_type
        string origin
        string destination
        date travel_date
        decimal price
        string status
    }

    PAYMENT {
        int id PK
        string payment_ref
        int booking_id FK
        int ticket_id FK
        int user_id FK
        decimal amount
        string payment_option
        string payment_method
        string verification_status
    }

    USER ||--|| USER_PROFILE : "has"
    USER ||--o{ BOOKING : "places"
    USER ||--o{ CUSTOM_TRIP : "builds"
    USER ||--o{ CUSTOM_QUOTATION_REQUEST : "submits"
    USER ||--o{ STANDALONE_TICKET : "reserves"

    DESTINATION ||--o{ HOTEL : "contains"
    DESTINATION ||--o{ ACTIVITY : "offers"
    DESTINATION ||--o{ TRANSPORTATION : "connects"
    DESTINATION ||--o{ PREDEFINED_PACKAGE : "belongs to"

    PREDEFINED_PACKAGE }|--|| HOTEL : "includes"
    PREDEFINED_PACKAGE }|--|{ ACTIVITY : "includes"

    CUSTOM_TRIP ||--o{ CUSTOM_TRIP_DESTINATION : "contains stays"
    CUSTOM_TRIP_DESTINATION }|--|| DESTINATION : "targets"

    BOOKING }|--o| PREDEFINED_PACKAGE : "books package"
    BOOKING }|--o| CUSTOM_TRIP : "books custom trip"
    BOOKING ||--o{ PAYMENT : "settles via"

    STANDALONE_TICKET ||--o{ PAYMENT : "settles via"
```

---
*Generated for TravelReady design reference (`images.md`).*
