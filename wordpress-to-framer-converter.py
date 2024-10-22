import xml.etree.ElementTree as ET
import csv
import logging
from datetime import datetime
import re
from html import unescape
import os
import requests
from tqdm import tqdm

# Set up logging
logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_wordpress_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        return root
    except ET.ParseError as e:
        logging.error(f"Error parsing XML file: {e}")
        return None

def extract_post_data(item, post_number, total_posts):
    try:
        title = item.find('.//title')
        title = title.text if title is not None else ''
        print(f"\nProcessing post {post_number}/{total_posts}: {title}")

        slug = item.find('./{http://wordpress.org/export/1.2/}post_name')
        slug = slug.text if slug is not None else ''

        content = item.find('.//content:encoded', namespaces={'content': 'http://purl.org/rss/1.0/modules/content/'})
        content = content.text if content is not None else ''

        print("Removing Gutenberg comments...")
        content = remove_gutenberg_comments(content)

        pub_date_elem = item.find('.//pubDate')
        if pub_date_elem is not None and pub_date_elem.text:
            pub_date = datetime.strptime(pub_date_elem.text, '%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%d')
        else:
            pub_date = ''
        
        author = item.find('./{http://purl.org/dc/elements/1.1/}creator')
        author = author.text if author is not None else ''

        tags = [tag.text for tag in item.findall('.//category[@domain="post_tag"]')]
        tags = ', '.join(tags) if tags else ''

        categories = [cat.text for cat in item.findall('.//category[@domain="category"]')]
        categories = ', '.join(categories) if categories else ''

        # Fetch description from rank_math_description meta field
        description = ''
        for meta in item.findall('.//wp:postmeta', namespaces={'wp': 'http://wordpress.org/export/1.2/'}):
            meta_key = meta.find('wp:meta_key', namespaces={'wp': 'http://wordpress.org/export/1.2/'})
            if meta_key is not None and meta_key.text == 'rank_math_description':
                meta_value = meta.find('wp:meta_value', namespaces={'wp': 'http://wordpress.org/export/1.2/'})
                if meta_value is not None:
                    description = meta_value.text
                    break

        description = unescape(description) if description else ''

        featured_image = ''
        thumbnail_id = item.find('.//wp:postmeta[wp:meta_key="_thumbnail_id"]/wp:meta_value', 
                                 namespaces={'wp': 'http://wordpress.org/export/1.2/'})
        if thumbnail_id is not None and thumbnail_id.text:
            print("Fetching featured image...")
            try:
                response = requests.get(f"https://example.com/wp-json/wp/v2/media/{thumbnail_id.text}")
                if response.status_code == 200:
                    media_data = response.json()
                    featured_image = media_data['guid']['rendered']
                    print(f"Featured image URL: {featured_image}")
                else:
                    print(f"Failed to fetch image. Status code: {response.status_code}")
            except requests.RequestException as e:
                logging.error(f"Error fetching featured image: {e}")
                print(f"Error fetching featured image: {e}")

        return {
            'Title': title,
            'Slug': slug,
            'Image': featured_image,
            'Author': author,
            'Date': pub_date,
            'Tag': tags,
            'Category': categories,
            'Description': description,
            'Content': content
        }
    except AttributeError as e:
        logging.error(f"Error extracting post data: {e}")
        print(f"Error extracting post data: {e}")
        return None

def remove_gutenberg_comments(content):
    if not content:
        return ''
    
    content = re.sub(r'<!-- /wp:.*?-->', '', content)
    content = re.sub(r'<!-- wp:.*?-->', '', content)
    
    return content.strip()

def convert_to_csv(xml_file, csv_file_base):
    root = parse_wordpress_xml(xml_file)
    if root is None:
        return
    
    posts = []
    items = root.findall('.//item')
    
    print(f"Found {len(items)} items in the XML file. Processing all published posts.")
    
    for index, item in enumerate(tqdm(items, desc="Processing posts", unit="post")):
        post_type = item.find('./{http://wordpress.org/export/1.2/}post_type')
        post_status = item.find('./{http://wordpress.org/export/1.2/}status')
        
        if (post_type is not None and post_type.text == 'post' and 
            post_status is not None and post_status.text == 'publish'):
            post_data = extract_post_data(item, index + 1, len(items))
            if post_data:
                posts.append(post_data)
    
    if not posts:
        logging.error("No valid published posts found in the XML file")
        print("No valid published posts found in the XML file")
        return
    
    try:
        file_number = 1
        current_size = 0
        current_posts = []
        total_exported = 0

        for post in tqdm(posts, desc="Writing to CSV", unit="post"):
            post_size = sum(len(str(value).encode('utf-8')) for value in post.values())
            
            if current_size + post_size > 5 * 1024 * 1024 or len(current_posts) >= 100:
                write_csv(f"{csv_file_base}_{file_number}.csv", current_posts)
                file_number += 1
                current_size = 0
                current_posts = []
                total_exported += len(current_posts)

            current_size += post_size
            current_posts.append(post)

        if current_posts:
            write_csv(f"{csv_file_base}_{file_number}.csv", current_posts)
            total_exported += len(current_posts)

        print(f"\nSuccessfully converted {total_exported} published posts to {file_number} CSV file(s).")
    except IOError as e:
        logging.error(f"Error writing to CSV file: {e}")
        print(f"Error writing to CSV file: {e}")

def write_csv(filename, posts):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Title', 'Slug', 'Image', 'Author', 'Date', 'Tag', 'Category', 'Description', 'Content'])
            writer.writeheader()
            for post in posts:
                writer.writerow(post)
        print(f"Created file: {filename}")
    except IOError as e:
        logging.error(f"Error writing to CSV file {filename}: {e}")
        print(f"Error writing to CSV file {filename}: {e}")

if __name__ == "__main__":
    xml_file = "sab.WordPress.Post.xml"  # Replace with your XML file path
    csv_file_base = "framer_blog_posts"  # Base name for output CSV files
    convert_to_csv(xml_file, csv_file_base)
