# Zestreet 🍜
### Global Street Food Intelligence Platform

Zestreet is a full-stack street food analytics dashboard built on a structured MySQL database of **4,259 dishes across 11 countries**. It provides interactive data visualisation, dish exploration with filtering, and complete CRUD management — all within a single-page application with authentication.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Getting Started](#getting-started)
- [Pages & Functionality](#pages--functionality)
- [SQL Queries Reference](#sql-queries-reference)
- [CRUD Operations](#crud-operations)
- [Demo Credentials](#demo-credentials)
- [Project Structure](#project-structure)

---

## Features

- **Authentication** — Login-gated access with demo credentials
- **Dashboard** — Live KPI cards, 6 charts, and 2 deep insight tables all derived from the live dataset
- **Explore** — Filter dishes by country, city, food type, cooking method, and price range
- **Manage** — Full CRUD: Add, Update, Delete, and View All dishes with instant platform-wide sync
- **Live sync** — Every change in Manage instantly reflects across Dashboard KPIs, charts, Explore cards, and filter dropdowns

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React JSX / Vanilla HTML+CSS+JS |
| Charts | Chart.js 4.4.1 (Recharts alternative) |
| Database | MySQL 8.x |
| Backend (assumed) | Node.js / Express or Python / Flask |
| Styling | Custom CSS — no framework |

---

## Database Schema

```sql
-- Master tables
countries     (country_id PK, country_name)
cities        (city_id PK, city_name, country_id FK)
cooking_methods (method_id PK, method_name)
food_types    (type_id PK, type_name)

-- Main table
food_items (
  food_id      INT AUTO_INCREMENT PRIMARY KEY,
  dish_name    VARCHAR(150),
  ingredients  TEXT,
  description  TEXT,
  price        FLOAT,
  rating       FLOAT,
  city_id      INT FK → cities,
  method_id    INT FK → cooking_methods,
  type_id      INT FK → food_types
)

-- Denormalised analytics view (no duplicates)
final_food_items (
  dish_name, city_name, country_name,
  method_name, type_name,
  price FLOAT,   -- AVG per group
  rating FLOAT   -- AVG per group
)
```

The `final_food_items` table is the source of truth for all dashboard queries. It is created by averaging `price` and `rating` across duplicate `(dish, city, country, method, type)` combinations.

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-org/zestreet.git
cd zestreet
```

### 2. Set up the database

```bash
mysql -u root -p < schema.sql
mysql -u root -p street_food_db < seed_data.sql
```

### 3. Install backend dependencies

```bash
npm install        # Node/Express
# or
pip install -r requirements.txt   # Python/Flask
```

### 4. Configure environment

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=street_food_db
PORT=3000
```

### 5. Start the server

```bash
npm start
# or
python app.py
```

### 6. Open the app

```
http://localhost:3000
```

---

## Pages & Functionality

### Login Page
- Split layout: white illustration panel (left) + dark green form panel (right)
- Smooth SVG wave divider between panels
- Credential validation against the user store
- Demo credentials displayed inline for quick access

### Dashboard
KPI cards (live, recalculate on every data change):

| Card | Metric |
|------|--------|
| Total Dishes | `COUNT(*)` from `final_food_items` |
| Avg Rating | `AVG(rating)` |
| Avg Price | `AVG(price)` |
| Top Country | Country with the most dish entries |

Chart sections:

| Section | Charts |
|---------|--------|
| User Preferences | Price vs Rating (bar), Veg vs Non-Veg (donut) |
| Health Insights | Healthy vs Unhealthy (donut), Fried food % by country (horizontal bar) |
| Market Insights | City diversity — top 10 cities (bar), Value for money index — rating÷price (horizontal bar) |
| Deep Insights | Overpriced foods table (price − rating gap), Hidden gems table (rating > 4 & price < avg) |

### Explore Page
- Left filter panel: Country → City (cascades), Food Type, Cooking Method, Max Price slider
- Right card grid: pastel colour-cycled cards with dish name, city, country flag, price, star rating, VEG/NON-VEG indicator, and cooking method badge
- Click any card to open a detail popup (price, rating, method, full ingredients, tags)
- Country dropdown dynamically updates to only show countries present in the current dataset

### Manage Page
Four operations via left sidebar:

| Operation | Description |
|-----------|-------------|
| Add Dish | Free-text country/city inputs, method & type dropdowns, price, rating, ingredients (description optional) |
| Update Dish | Select from existing dishes → pre-fill all fields → edit and save |
| Delete Dish | Select dish → preview warning → confirm permanent deletion |
| View All | Full table with inline Edit and Delete buttons per row |

All operations trigger `syncAll()` which immediately updates KPIs, charts, Explore cards, filter dropdowns, and the View All table.

---

## SQL Queries Reference

### KPI Queries

```sql
-- Total dishes
SELECT COUNT(*) AS total_dishes FROM final_food_items;

-- Average rating
SELECT ROUND(AVG(rating), 2) AS avg_rating FROM final_food_items;

-- Average price
SELECT ROUND(AVG(price), 2) AS avg_price FROM final_food_items;

-- Top country
SELECT country_name, COUNT(*) AS total
FROM final_food_items
GROUP BY country_name
ORDER BY total DESC
LIMIT 1;
```

### Chart Queries

```sql
-- Price vs Rating (bracket averages)
SELECT
  CASE
    WHEN price < 2    THEN 'Cheap'
    WHEN price <= 4   THEN 'Moderate'
    ELSE 'Expensive'
  END AS price_category,
  ROUND(AVG(rating), 2) AS avg_rating
FROM final_food_items
GROUP BY price_category;

-- Veg vs Non-Veg distribution
SELECT type_name, COUNT(*) AS total_items
FROM final_food_items
GROUP BY type_name;

-- Healthy vs Unhealthy
SELECT
  CASE
    WHEN method_name IN ('Grilled','Boiled','Steamed') THEN 'Healthy'
    ELSE 'Unhealthy'
  END AS health_category,
  COUNT(*) AS total_dishes
FROM final_food_items
GROUP BY health_category;

-- Fried food % by country
SELECT
  country_name,
  ROUND(COUNT(CASE WHEN method_name = 'Fried' THEN 1 END) * 100.0 / COUNT(*), 2) AS fried_percentage
FROM final_food_items
GROUP BY country_name
ORDER BY fried_percentage DESC;

-- City diversity (top 10)
SELECT city_name, COUNT(*) AS total_dishes
FROM final_food_items
GROUP BY city_name
ORDER BY total_dishes DESC
LIMIT 10;

-- Value for money (rating ÷ price)
SELECT dish_name, price, rating,
  ROUND(rating / price, 2) AS value_score
FROM final_food_items
WHERE price > 0
ORDER BY value_score DESC
LIMIT 10;
```

### Deep Insight Queries

```sql
-- Overpriced foods (price − rating gap)
SELECT dish_name, price, rating,
  ROUND(price - rating, 2) AS gap
FROM final_food_items
ORDER BY gap DESC
LIMIT 10;

-- Hidden gems (high rating, low price)
SELECT dish_name, rating, price
FROM final_food_items
WHERE rating > 4
  AND price < (SELECT AVG(price) FROM final_food_items)
ORDER BY rating DESC
LIMIT 10;
```

### Filter / Explore Query

```sql
SELECT *
FROM final_food_items
WHERE country_name  = 'India'         -- optional
  AND city_name     = 'Mumbai'        -- optional
  AND type_name     = 'Vegetarian'    -- optional
  AND method_name   = 'Fried'         -- optional
  AND price BETWEEN 1 AND 5;          -- optional
```

---

## CRUD Operations

### Add Dish (INSERT)

```sql
-- Step 1: resolve foreign keys
SET @city_id   = (SELECT ci.city_id FROM cities ci
                  JOIN countries co ON ci.country_id = co.country_id
                  WHERE ci.city_name = 'Mumbai' AND co.country_name = 'India' LIMIT 1);
SET @method_id = (SELECT method_id FROM cooking_methods WHERE method_name = 'Fried' LIMIT 1);
SET @type_id   = (SELECT type_id   FROM food_types        WHERE type_name  = 'Vegetarian' LIMIT 1);

-- Step 2: insert
INSERT INTO food_items (dish_name, ingredients, description, price, rating, city_id, method_id, type_id)
VALUES ('My Special Dish', 'Cheese, Spices', 'Custom created dish', 3.5, 4.7,
        @city_id, @method_id, @type_id);
```

### Update Dish (UPDATE)

```sql
SET @city_id   = (SELECT ci.city_id FROM cities ci
                  JOIN countries co ON ci.country_id = co.country_id
                  WHERE ci.city_name = 'Delhi' AND co.country_name = 'India' LIMIT 1);
SET @method_id = (SELECT method_id FROM cooking_methods WHERE method_name = 'Grilled' LIMIT 1);
SET @type_id   = (SELECT type_id   FROM food_types        WHERE type_name  = 'Vegetarian' LIMIT 1);

UPDATE food_items
SET dish_name   = 'Updated Special Dish',
    ingredients = 'Updated ingredients',
    description = 'Updated description',
    price       = 2.8,
    rating      = 4.3,
    city_id     = @city_id,
    method_id   = @method_id,
    type_id     = @type_id
WHERE food_id = 1;
```

### Delete Dish (DELETE)

```sql
DELETE FROM food_items
WHERE food_id = (
  SELECT food_id FROM (
    SELECT f.food_id FROM food_items f
    JOIN cities ci   ON f.city_id    = ci.city_id
    JOIN countries co ON ci.country_id = co.country_id
    WHERE f.dish_name   = 'My Special Dish'
      AND ci.city_name  = 'Mumbai'
      AND co.country_name = 'India'
    LIMIT 1
  ) AS temp
);
```

---

## Demo Credentials

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `food123` |

---

## Project Structure

```
zestreet/
├── README.md
├── schema.sql                  # Database setup + table creation
├── seed_data.sql               # Initial 4,259 dish records
├── frontend/
│   ├── index.html              # Single-page app entry point
│   ├── StreetFoodDashboard.jsx # Main React component
│   └── styles/
│       └── main.css
├── backend/
│   ├── server.js               # Express API server
│   ├── routes/
│   │   ├── kpi.js              # KPI endpoints
│   │   ├── charts.js           # Chart data endpoints
│   │   ├── explore.js          # Filter/search endpoint
│   │   └── manage.js           # CRUD endpoints
│   └── db.js                   # MySQL connection pool
└── docs/
    └── api.md                  # API endpoint documentation
```

### API Endpoints (assumed)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/kpi` | Total dishes, avg rating, avg price, top country |
| GET | `/api/charts/price-rating` | Avg rating per price bracket |
| GET | `/api/charts/veg` | Veg vs non-veg counts |
| GET | `/api/charts/health` | Healthy vs unhealthy counts |
| GET | `/api/charts/fried` | Fried % per country |
| GET | `/api/charts/cities` | Top 10 cities by dish count |
| GET | `/api/charts/value` | Value-for-money index |
| GET | `/api/insights/overpriced` | Top overpriced dishes |
| GET | `/api/insights/gems` | Hidden gems |
| GET | `/api/explore` | Filtered dish list |
| POST | `/api/dishes` | Add new dish |
| PUT | `/api/dishes/:id` | Update dish |
| DELETE | `/api/dishes/:id` | Delete dish |

---

## Dataset

The dataset (`street_food.csv`) contains 4,259 rows with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| Dish Name | VARCHAR | Name of the street food item |
| Country | VARCHAR | Country of origin |
| Region/City | VARCHAR | City where the dish is commonly found |
| Ingredients | TEXT | Comma-separated ingredient list |
| Description | TEXT | Short dish description |
| Cooking Method | VARCHAR | One of 9 methods (Fried, Grilled, Baked, etc.) |
| Typical Price (USD) | FLOAT | Price in USD ($0.20 – $5.00 in dataset) |
| Vegetarian | VARCHAR | "Yes" or "No" |
| Rating | FLOAT | Rating from 1.0 to 5.0 |

---

*Built for the Zestreet Global Street Food Intelligence Platform — 2025*
