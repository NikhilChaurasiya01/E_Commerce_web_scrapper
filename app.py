import pandas as pd
import re
import math
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import json

# Helper function to find product name column
def find_product_name_column(df, possible_names=['title', 'name', 'product_title', 'product_name', 'item_name']):
    for col in possible_names:
        if col in df.columns:
            return col
    # Check for case-insensitive matches
    for col in df.columns:
        if col.lower() in [name.lower() for name in possible_names]:
            return col
    raise KeyError(f"No product name column found in DataFrame. Expected one of {possible_names}, got {list(df.columns)}")

# Helper function to find and rename URL column
def find_and_rename_url_column(df, possible_url_names=['url', 'product_url', 'link', 'product_link', 'web_url']):
    for col in possible_url_names:
        if col in df.columns:
            if col != 'url':
                df = df.rename(columns={col: 'url'})
            return df
    df['url'] = None
    return df 

# Helper function to find and rename image URL column
def find_and_rename_image_url_column(df, possible_image_url_names=['image_url', 'image', 'img_url', 'picture_url']):
    for col in possible_image_url_names:
        if col in df.columns:
            if col != 'image_url':
                df = df.rename(columns={col: 'image_url'})
            return df
    df['image_url'] = None
    return df

# Parsing functions for price and discount
def parse_price_str(price_str):
    if pd.isna(price_str):
        return None, None
    price_str = str(price_str).strip()
    price_match = re.search(r'₹?(\d[\d,]*(\.\d+)?)', price_str)
    price = float(price_match.group(1).replace(',', '')) if price_match else None
    discount_match = re.search(r'(\d+)%', price_str)
    discount = float(discount_match.group(1)) if discount_match else None
    return price, discount

def parse_price(price_str):
    if pd.isna(price_str):
        return None
    price_str = str(price_str).strip()
    match = re.search(r'(\d[\d,]*(\.\d+)?)', price_str)
    if match:
        price = match.group(1).replace(',', '')
        try:
            return float(price)
        except ValueError:
            return None
    return None

def parse_discount(discount_str):
    if pd.isna(discount_str):
        return None
    discount_str = str(discount_str).strip()
    match = re.search(r'(\d+)%', discount_str)
    return float(match.group(1)) if match else None

# Parsing functions for product_name
def extract_product_details(product_name):
    if pd.isna(product_name) or not isinstance(product_name, str):
        return {key: None for key in ['brand', 'model', 'storage', 'ram', 'color', 'processor', 'screen_size', 'os', 'variants']}

    name = product_name.strip()
    details = {'brand': None, 'model': None, 'storage': None, 'ram': None, 'color': None, 
               'processor': None, 'screen_size': None, 'os': None, 'variants': None}

    # Comprehensive lists for matching
    brands = ['Apple', 'Samsung', 'HP', 'Dell', 'Lenovo', 'Asus', 'Acer', 'Poco', 'Realme', 
              'Xiaomi', 'Vivo', 'Oppo', 'OnePlus', 'Redmi', 'Nokia', 'Motorola', 'Sony', 'Honor', 'Google', 'LG']
    colors = ['Black', 'White', 'Silver', 'Gold', 'Grey', 'Blue', 'Red', 'Green', 'Purple', 
              'Pink', 'Yellow', 'Midnight', 'Starlight', 'Phantom', 'Space', 'Sierra', 'Cosmic', 'Rose', 'Graphite', 'Ocean', 'Sky']
    processors = ['Intel Core i3', 'Intel Core i5', 'Intel Core i7', 'Intel Core i9', 
                  'AMD Ryzen 3', 'AMD Ryzen 5', 'AMD Ryzen 7', 'Apple M1', 'Apple M2', 
                  'Snapdragon 8 Gen 1', 'Snapdragon 8 Gen 2', 'Snapdragon 778G', 
                  'Dimensity 9200', 'Dimensity 8200', 'A16 Bionic', 'A15 Bionic', 'Exynos 2100', 'Kirin 9000']
    os_list = ['Windows 11', 'Windows 10', 'macOS Ventura', 'macOS Monterey', 'Android 13', 
               'Android 12', 'Chrome OS', 'iOS 16', 'iOS 15']
    variants_list = ['Pro', 'Ultra', '5G', '4G', 'Gaming', '2-in-1', 'Max', 'Plus', 'Slim', 'Edge', 'Note', 'Book']

    # Helper function to remove matched text
    def remove_matched(text, pattern, group=0):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matched_text = match.group(group)
            text = text.replace(matched_text, '').strip()
            return text, matched_text
        return text, None

    # 1. Extract Brand
    words = name.split()
    for word in words:
        for brand in brands:
            if word.lower() == brand.lower():
                details['brand'] = brand
                name = name.replace(word, '', 1).strip()
                break
        if details['brand']:
            break

    # 2. Extract Screen Size
    name, screen_size = remove_matched(name, r'(\d+\.?\d*-inch|\d+\.?\d* inch)', 1)
    if screen_size:
        screen_size = screen_size.replace(' inch', '-inch').strip()
        details['screen_size'] = screen_size

    # 3. Extract Storage
    name, storage = remove_matched(name, r'(\d+\s?(GB|TB)\s?(SSD|HDD)?)', 1)
    details['storage'] = storage

    # 4. Extract RAM
    name, ram = remove_matched(name, r'(\d+\s?GB\s?(RAM|DDR4|DDR5)?)', 1)
    details['ram'] = ram

    # 5. Extract Processor
    for proc in processors:
        if re.search(rf'\b{proc}\b', name, re.IGNORECASE):
            details['processor'] = proc
            name = name.replace(proc, '').strip()
            break

    # 6. Extract Operating System
    for os in os_list:
        if re.search(rf'\b{os}\b', name, re.IGNORECASE):
            details['os'] = os
            name = name.replace(os, '').strip()
            break

    # 7. Extract Color
    for color in colors:
        if re.search(rf'\b{color}\b', name, re.IGNORECASE):
            details['color'] = color
            name = name.replace(color, '').strip()
            break

    # 8. Extract Variants/Features
    found_variants = []
    for variant in variants_list:
        if re.search(rf'\b{variant}\b', name, re.IGNORECASE):
            found_variants.append(variant)
            name = name.replace(variant, '').strip()
    details['variants'] = ', '.join(found_variants) if found_variants else None

    # 9. Extract Model (remaining text)
    name = re.sub(r'\s+', ' ', name).strip()
    name = re.sub(r'[\(\),]', '', name).strip()
    if name and not re.match(r'^\d+$', name):
        details['model'] = name
    else:
        details['model'] = None

    return details

# Standard columns
standard_cols = ['retailer', 'category', 'product_name', 'price', 'mrp', 'discount', 'url', 
                 'image_url', 'rating', 'reviews', 'offer', 'delivery', 'brand', 'model', 
                 'storage', 'ram', 'color', 'processor', 'screen_size', 'os', 'variants']

# Process each file
# Reliance Laptops
df_reliance_laptops = pd.read_csv('reliance_laptops.csv')
df_reliance_laptops = find_and_rename_url_column(df_reliance_laptops)
df_reliance_laptops = find_and_rename_image_url_column(df_reliance_laptops)
product_name_col = find_product_name_column(df_reliance_laptops)
df_reliance_laptops = df_reliance_laptops.rename(columns={product_name_col: 'product_name'})
df_reliance_laptops[['price', 'discount']] = df_reliance_laptops['price'].apply(lambda x: pd.Series(parse_price_str(x)))
df_reliance_laptops['retailer'] = 'Reliance'
df_reliance_laptops['category'] = 'laptops'
df_reliance_laptops['mrp'] = None
df_reliance_laptops['rating'] = None
df_reliance_laptops['reviews'] = None
df_reliance_laptops['offer'] = None
df_reliance_laptops['delivery'] = None
details = df_reliance_laptops['product_name'].apply(extract_product_details)
for col in ['brand', 'model', 'storage', 'ram', 'color', 'processor', 'screen_size', 'os', 'variants']:
    df_reliance_laptops[col] = details.apply(lambda x: x[col])
for col in standard_cols:
    if col not in df_reliance_laptops.columns:
        df_reliance_laptops[col] = None
df_reliance_laptops = df_reliance_laptops[standard_cols]

# Reliance Mobiles
df_reliance_mobiles = pd.read_json('reliance_mobiles.json')
df_reliance_mobiles = find_and_rename_url_column(df_reliance_mobiles)
df_reliance_mobiles = find_and_rename_image_url_column(df_reliance_mobiles)
product_name_col = find_product_name_column(df_reliance_mobiles)
df_reliance_mobiles = df_reliance_mobiles.rename(columns={product_name_col: 'product_name'})
df_reliance_mobiles['price'] = df_reliance_mobiles['price'].apply(parse_price)
df_reliance_mobiles['mrp'] = df_reliance_mobiles['mrp'].apply(parse_price)
df_reliance_mobiles['discount'] = df_reliance_mobiles['discount'].apply(parse_discount)
df_reliance_mobiles['retailer'] = 'Reliance'
df_reliance_mobiles['category'] = 'mobiles'
df_reliance_mobiles['rating'] = None
df_reliance_mobiles['reviews'] = None
df_reliance_mobiles['offer'] = None
df_reliance_mobiles['delivery'] = None
details = df_reliance_mobiles['product_name'].apply(extract_product_details)
for col in ['brand', 'model', 'storage', 'ram', 'color', 'processor', 'screen_size', 'os', 'variants']:
    df_reliance_mobiles[col] = details.apply(lambda x: x[col])
for col in standard_cols:
    if col not in df_reliance_mobiles.columns:
        df_reliance_mobiles[col] = None
df_reliance_mobiles = df_reliance_mobiles[standard_cols]

# Amazon Laptops
df_amazon_laptops = pd.read_csv('amazon_laptops.csv')
df_amazon_laptops = find_and_rename_url_column(df_amazon_laptops)
df_amazon_laptops = find_and_rename_image_url_column(df_amazon_laptops)
product_name_col = find_product_name_column(df_amazon_laptops)
df_amazon_laptops = df_amazon_laptops.rename(columns={product_name_col: 'product_name'})
df_amazon_laptops[['price', 'discount']] = df_amazon_laptops['price'].apply(lambda x: pd.Series(parse_price_str(x)))
df_amazon_laptops['retailer'] = 'Amazon'
df_amazon_laptops['category'] = 'laptops'
df_amazon_laptops['mrp'] = None
df_amazon_laptops['rating'] = None
df_amazon_laptops['reviews'] = None
df_amazon_laptops['offer'] = None
df_amazon_laptops['delivery'] = None
details = df_amazon_laptops['product_name'].apply(extract_product_details)
for col in ['brand', 'model', 'storage', 'ram', 'color', 'processor', 'screen_size', 'os', 'variants']:
    df_amazon_laptops[col] = details.apply(lambda x: x[col])
for col in standard_cols:
    if col not in df_amazon_laptops.columns:
        df_amazon_laptops[col] = None
df_amazon_laptops = df_amazon_laptops[standard_cols]

# Amazon Mobiles
df_amazon_mobiles = pd.read_json('amazon_mobiles.json')
df_amazon_mobiles = find_and_rename_url_column(df_amazon_mobiles)
df_amazon_mobiles = find_and_rename_image_url_column(df_amazon_mobiles)
product_name_col = find_product_name_column(df_amazon_mobiles)
df_amazon_mobiles = df_amazon_mobiles.rename(columns={product_name_col: 'product_name'})
df_amazon_mobiles['price'] = df_amazon_mobiles['price'].apply(parse_price)
df_amazon_mobiles['rating'] = pd.to_numeric(df_amazon_mobiles['rating'], errors='coerce')
df_amazon_mobiles['reviews'] = pd.to_numeric(df_amazon_mobiles['reviews'], errors='coerce')
df_amazon_mobiles['retailer'] = 'Amazon'
df_amazon_mobiles['category'] = 'mobiles'
df_amazon_mobiles['mrp'] = None
df_amazon_mobiles['discount'] = None
df_amazon_mobiles['offer'] = None
df_amazon_mobiles['delivery'] = None
details = df_amazon_mobiles['product_name'].apply(extract_product_details)
for col in ['brand', 'model', 'storage', 'ram', 'color', 'processor', 'screen_size', 'os', 'variants']:
    df_amazon_mobiles[col] = details.apply(lambda x: x[col])
for col in standard_cols:
    if col not in df_amazon_mobiles.columns:
        df_amazon_mobiles[col] = None
df_amazon_mobiles = df_amazon_mobiles[standard_cols]

# Croma Mobiles
df_croma_mobiles = pd.read_csv('croma_limited.csv')
df_croma_mobiles = find_and_rename_url_column(df_croma_mobiles)
df_croma_mobiles = find_and_rename_image_url_column(df_croma_mobiles, possible_image_url_names=['image'])
df_croma_mobiles = df_croma_mobiles.rename(columns={'name': 'product_name'})
df_croma_mobiles['price'] = df_croma_mobiles['price'].apply(parse_price)
df_croma_mobiles['rating'] = pd.to_numeric(df_croma_mobiles['rating'], errors='coerce')
df_croma_mobiles['retailer'] = 'Croma'
df_croma_mobiles['category'] = 'mobiles'
df_croma_mobiles['mrp'] = None
df_croma_mobiles['discount'] = None
df_croma_mobiles['reviews'] = None
df_croma_mobiles['offer'] = None
df_croma_mobiles['delivery'] = None
details = df_croma_mobiles['product_name'].apply(extract_product_details)
for col in ['brand', 'model', 'storage', 'ram', 'color', 'processor', 'screen_size', 'os', 'variants']:
    df_croma_mobiles[col] = details.apply(lambda x: x[col])
for col in standard_cols:
    if col not in df_croma_mobiles.columns:
        df_croma_mobiles[col] = None
df_croma_mobiles = df_croma_mobiles[standard_cols]

# Flipkart Mobiles
df_flipkart_mobiles = pd.read_json('flipkart_mobiles.json')
df_flipkart_mobiles = find_and_rename_url_column(df_flipkart_mobiles)
df_flipkart_mobiles = find_and_rename_image_url_column(df_flipkart_mobiles)
product_name_col = find_product_name_column(df_flipkart_mobiles)
df_flipkart_mobiles = df_flipkart_mobiles.rename(columns={product_name_col: 'product_name'})
df_flipkart_mobiles['price'] = df_flipkart_mobiles['price'].apply(parse_price)
df_flipkart_mobiles['rating'] = pd.to_numeric(df_flipkart_mobiles['rating'], errors='coerce')
df_flipkart_mobiles['retailer'] = 'Flipkart'
df_flipkart_mobiles['category'] = 'mobiles'
df_flipkart_mobiles['mrp'] = None
df_flipkart_mobiles['discount'] = None
df_flipkart_mobiles['reviews'] = None
df_flipkart_mobiles['offer'] = None
df_flipkart_mobiles['delivery'] = None
details = df_flipkart_mobiles['product_name'].apply(extract_product_details)
for col in ['brand', 'model', 'storage', 'ram', 'color', 'processor', 'screen_size', 'os', 'variants']:
    df_flipkart_mobiles[col] = details.apply(lambda x: x[col])
for col in standard_cols:
    if col not in df_flipkart_mobiles.columns:
        df_flipkart_mobiles[col] = None
df_flipkart_mobiles = df_flipkart_mobiles[standard_cols]

# Flipkart Laptops
df_flipkart_laptops = pd.read_json('flipkart_laptops.json')
df_flipkart_laptops = find_and_rename_url_column(df_flipkart_laptops)
df_flipkart_laptops = find_and_rename_image_url_column(df_flipkart_laptops)
product_name_col = find_product_name_column(df_flipkart_laptops)
df_flipkart_laptops = df_flipkart_laptops.rename(columns={product_name_col: 'product_name'})
df_flipkart_laptops['price'] = df_flipkart_laptops['price'].apply(parse_price)
df_flipkart_laptops['rating'] = pd.to_numeric(df_flipkart_laptops['rating'], errors='coerce')
df_flipkart_laptops['retailer'] = 'Flipkart'
df_flipkart_laptops['category'] = 'laptops'
df_flipkart_laptops['mrp'] = None
df_flipkart_laptops['discount'] = None
df_flipkart_laptops['reviews'] = None
df_flipkart_laptops['offer'] = None
df_flipkart_laptops['delivery'] = None
details = df_flipkart_laptops['product_name'].apply(extract_product_details)
for col in ['brand', 'model', 'storage', 'ram', 'color', 'processor', 'screen_size', 'os', 'variants']:
    df_flipkart_laptops[col] = details.apply(lambda x: x[col])
for col in standard_cols:
    if col not in df_flipkart_laptops.columns:
        df_flipkart_laptops[col] = None
df_flipkart_laptops = df_flipkart_laptops[standard_cols]

# Croma Laptops
df_croma_laptops = pd.read_json('croma_laptops.json')
df_croma_laptops = find_and_rename_url_column(df_croma_laptops)
df_croma_laptops = find_and_rename_image_url_column(df_croma_laptops)
product_name_col = find_product_name_column(df_croma_laptops)
df_croma_laptops = df_croma_laptops.rename(columns={product_name_col: 'product_name'})
df_croma_laptops['price'] = df_croma_laptops['current_price'].apply(parse_price)
df_croma_laptops['mrp'] = df_croma_laptops['original_price'].apply(parse_price)
df_croma_laptops['discount'] = df_croma_laptops['discount'].apply(parse_discount)
df_croma_laptops['rating'] = pd.to_numeric(df_croma_laptops['rating'], errors='coerce')
df_croma_laptops['reviews'] = pd.to_numeric(df_croma_laptops['reviews'], errors='coerce')
df_croma_laptops['offer'] = df_croma_laptops['offer']
df_croma_laptops['delivery'] = df_croma_laptops['delivery']
df_croma_laptops['retailer'] = 'Croma'
df_croma_laptops['category'] = 'laptops'
details = df_croma_laptops['product_name'].apply(extract_product_details)
for col in ['brand', 'model', 'storage', 'ram', 'color', 'processor', 'screen_size', 'os', 'variants']:
    df_croma_laptops[col] = details.apply(lambda x: x[col])
for col in standard_cols:
    if col not in df_croma_laptops.columns:
        df_croma_laptops[col] = None
df_croma_laptops = df_croma_laptops[standard_cols]

# Concatenate all dataframes
all_df = pd.concat([
    df_reliance_laptops,
    df_reliance_mobiles,
    df_amazon_laptops,
    df_amazon_mobiles,
    df_croma_mobiles,
    df_flipkart_mobiles,
    df_flipkart_laptops,
    df_croma_laptops
], ignore_index=True)

# Convert to list of dicts
products = all_df.to_dict(orient='records')

# Save the data as JSON
with open('products.json', 'w') as json_file:
    json.dump(products, json_file, indent=4)

# Convert the list of dictionaries back to a DataFrame
df = pd.DataFrame(products)

# Save the data as CSV
df.to_csv('products.csv', index=False)

print("Data saved as products.json and products.csv")
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        # Try to load cleaned data first
        try:
            df = pd.read_csv('products_cleaned.csv')
            # Filter only laptops and mobiles
            df = df[df['category'].isin(['laptops', 'mobiles'])]
            print(f"✓ Loaded cleaned data: {len(df)} products (laptops & mobiles only)")
        except FileNotFoundError:
            # Fallback to original file
            df = pd.read_csv('products_filled.csv')
            # Filter only laptops and mobiles
            df = df[df['category'].isin(['laptops', 'mobiles'])]
            print(f"✓ Loaded original data: {len(df)} products (laptops & mobiles only)")
        
        # Clean the data before sending
        # Remove rows with missing critical fields (including image_url)
        df = df[df['product_name'].notna() & df['price'].notna() & df['image_url'].notna()]
        # Also filter out empty image URLs
        df = df[df['image_url'].str.strip() != '']
        
        # Fill missing values with defaults
        df['rating'] = df['rating'].fillna(0)
        df['discount'] = df['discount'].fillna(0)
        df['brand'] = df['brand'].fillna('Unknown')
        df['ram'] = df['ram'].fillna('N/A')
        df['storage'] = df['storage'].fillna('N/A')
        df['processor'] = df['processor'].fillna('N/A')
        df['url'] = df['url'].fillna('')
        df['image_url'] = df['image_url'].fillna('')
        df['delivery'] = df['delivery'].fillna('')
        df['offer'] = df['offer'].fillna('')
        df['reviews'] = df['reviews'].fillna(0)
        df['mrp'] = df['mrp'].fillna(0)
        df['screen_size'] = df['screen_size'].fillna('')
        df['os'] = df['os'].fillna('')
        df['color'] = df['color'].fillna('')
        df['model'] = df['model'].fillna('')
        df['variants'] = df['variants'].fillna('')
        
        # Ensure price is numeric
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df[df['price'] > 0]  # Remove invalid prices
        
        # Add source field from retailer if not exists
        if 'source' not in df.columns and 'retailer' in df.columns:
            df['source'] = df['retailer']
        
        # Get pagination and filter parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 30, type=int)
        search = request.args.get('search', '', type=str)
        store = request.args.get('store', '', type=str)
        category = request.args.get('category', '', type=str)
        brand = request.args.get('brand', '', type=str)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        min_rating = request.args.get('min_rating', type=float)
        sort_by = request.args.get('sort_by', '', type=str)
        
        # Apply filters
        if search:
            df = df[df['product_name'].str.contains(search, case=False, na=False)]
        if store:
            df = df[df['retailer'].str.lower() == store.lower()]
        if category:
            df = df[df['category'].str.contains(category, case=False, na=False)]
        if brand:
            df = df[df['brand'].str.contains(brand, case=False, na=False)]
        if min_price is not None:
            df = df[df['price'] >= min_price]
        if max_price is not None:
            df = df[df['price'] <= max_price]
        if min_rating is not None:
            df = df[df['rating'] >= min_rating]
        
        # Apply sorting
        if sort_by == 'price_asc':
            df = df.sort_values('price', ascending=True)
        elif sort_by == 'price_desc':
            df = df.sort_values('price', ascending=False)
        elif sort_by == 'rating_desc':
            df = df.sort_values('rating', ascending=False, na_position='last')
        elif sort_by == 'discount_desc':
            df = df.sort_values('discount', ascending=False, na_position='last')
        elif sort_by == 'name_asc':
            df = df.sort_values('product_name', ascending=True)
        
        # Calculate pagination
        total_products = len(df)
        total_pages = math.ceil(total_products / limit)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # Get paginated data
        df_page = df.iloc[start_idx:end_idx]
        
        # Replace NaN with None for proper JSON serialization
        df_page = df_page.replace({pd.NA: None, float('nan'): None})
        
        # Convert DataFrame to list of dictionaries
        products = df_page.to_dict(orient='records')
        
        # Clean up any remaining NaN values and remove irrelevant empty fields
        for product in products:
            # Replace NaN with None
            for key, value in product.items():
                if isinstance(value, float) and math.isnan(value):
                    product[key] = None
            
            # Remove completely empty or useless fields
            keys_to_remove = []
            for key, value in product.items():
                if value is None or value == '' or value == 'N/A' or (isinstance(value, float) and value == 0.0 and key in ['rating', 'reviews']):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                if key not in ['product_name', 'price', 'retailer', 'category', 'image_url']:  # Keep essential fields
                    del product[key]
        
        print(f"✓ Returning {len(products)} products (page {page}/{total_pages})")
        return jsonify({
            'products': products,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_products': total_products,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })
    
    except FileNotFoundError:
        return jsonify({"error": "Product data file not found"}), 404
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    try:
        df = pd.read_csv('products_cleaned.csv')
        # Filter only laptops and mobiles
        df = df[df['category'].isin(['laptops', 'mobiles'])]
        # Filter only products with images
        df = df[df['image_url'].notna() & (df['image_url'].str.strip() != '')]
        
        stats = {
            'total_products': len(df),
            'stores': df['retailer'].unique().tolist(),
            'categories': df['category'].unique().tolist(),
            'brands': sorted(df['brand'].dropna().unique().tolist()),
            'price_range': {
                'min': float(df['price'].min()),
                'max': float(df['price'].max()),
                'avg': float(df['price'].mean())
            },
            'store_counts': df['retailer'].value_counts().to_dict()
        }
        
        return jsonify(stats)
    except Exception as e:
        print(f"✗ Stats Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Run the server
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)