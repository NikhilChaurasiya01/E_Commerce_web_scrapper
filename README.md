# SmartCompare - Product Price Comparison Platform

A modern, responsive web application for comparing laptop and mobile phone prices across multiple retailers (Amazon, Flipkart, Croma, Reliance Digital).

## Features

- 🔍 **Smart Search** - Real-time product search across 5,196+ products
- 🏪 **Multi-Store Comparison** - Compare prices from 4 major retailers
- ⚖️ **Product Comparison** - Compare up to 4 products side-by-side
- ❤️ **Wishlist** - Save favorite products with localStorage persistence
- 🎨 **Dark/Light Theme** - Toggle between dark and light modes
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- 🔄 **Advanced Filters** - Filter by store, category, brand, price range, and rating
- 📊 **Smart Sorting** - Sort by price, rating, discount, or name
- 🖼️ **Image Optimization** - Lazy loading with fallback placeholders
- 📄 **Pagination** - Efficient browsing with 30 products per page

## Tech Stack

**Backend:**
- Python 3.12
- Flask (Web Framework)
- Pandas (Data Processing)
- Flask-CORS (Cross-Origin Resource Sharing)
- Gunicorn (Production Server)

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- Font Awesome 6.4.0 (Icons)
- Google Fonts (Inter)

## Data Sources

- **Retailers**: Amazon, Flipkart, Croma, Reliance Digital
- **Categories**: Laptops (1,995 products), Mobiles (3,201 products)
- **Total Products**: 5,196

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/rdxhacnikhil/Smartdemo.git
cd Smartdemo
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Open in browser**
```
http://127.0.0.1:5000
```

## Deployment on Render

1. **Push to GitHub** (if not already done)
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/rdxhacnikhil/Smartdemo.git
git push -u origin main
```

2. **Deploy on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: smartcompare (or your preferred name)
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
   - Click "Create Web Service"

## Project Structure

```
├── app.py                          # Flask backend server
├── index.html                      # Main frontend application
├── products_cleaned.csv            # Clean product data
├── requirements.txt                # Python dependencies
├── README.md                       # Documentation
├── .gitignore                      # Git ignore rules
└── cleaning code for project product.ipynb  # Data cleaning notebook
```

## API Endpoints

### GET `/api/products`
Fetch paginated products with filters

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Products per page (default: 30)
- `search` (string): Search query
- `store` (string): Filter by retailer
- `category` (string): Filter by category
- `brand` (string): Filter by brand
- `min_price` (float): Minimum price
- `max_price` (float): Maximum price
- `min_rating` (float): Minimum rating
- `sort_by` (string): Sorting option (price_asc, price_desc, rating_desc, discount_desc, name_asc)

**Response:**
```json
{
  "products": [...],
  "pagination": {
    "page": 1,
    "limit": 30,
    "total_products": 5196,
    "total_pages": 174,
    "has_next": true,
    "has_prev": false
  }
}
```

### GET `/api/stats`
Get statistics and metadata

**Response:**
```json
{
  "total_products": 5196,
  "stores": ["Amazon", "Flipkart", "Croma", "Reliance"],
  "categories": ["laptops", "mobiles"],
  "brands": [...],
  "price_range": {
    "min": 499,
    "max": 399999,
    "avg": 25847
  },
  "store_counts": {...}
}
```

## Features in Detail

### Smart Missing Data Handling
- Only displays product specifications that have values
- Hides empty fields instead of showing "N/A" or placeholders
- Comparison table dynamically shows only relevant fields
- Clean, professional appearance

### Responsive Design
- Mobile-first approach
- Adapts to all screen sizes
- Touch-friendly controls
- Optimized images with lazy loading

### Performance Optimizations
- Server-side pagination
- Debounced search (500ms delay)
- Lazy image loading
- Efficient data filtering
- Skeleton loading states

## Browser Support

- ✅ Chrome (Latest)
- ✅ Firefox (Latest)
- ✅ Safari (Latest)
- ✅ Edge (Latest)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Author

**Nikhil Kumar**
- GitHub: [@rdxhacnikhil](https://github.com/rdxhacnikhil)

## Acknowledgments

- Product data sourced from major Indian retailers
- Icons by Font Awesome
- Fonts by Google Fonts
