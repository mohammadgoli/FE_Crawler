import os
import json
import sqlite3
import mysql.connector
from pathlib import Path

# SQLite Database Path
DB_PATH = Path('FECrawler.db')


def init_db():
    # Initialize SQLite database
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                status INTEGER DEFAULT 0 -- 0: Not crawled, 1: Crawled, 2: Parsed, -1: Error
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS envato_parsed_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                meta_title TEXT,
                meta_description TEXT,
                description TEXT,
                name_of_file TEXT,
                name_of_creator TEXT,
                creator_link TEXT,
                breadcrumb TEXT,
                preview_link TEXT,
                tags TEXT,
                attributes TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS freepik_parsed_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                meta_title TEXT,
                meta_description TEXT,
                description TEXT,
                name_of_file TEXT,
                name_of_creator TEXT,
                creator_link TEXT,
                breadcrumb TEXT,
                preview_link TEXT,
                tags TEXT,
                attributes TEXT
            )
        ''')
        conn.commit()


def get_next_url_to_process():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT url FROM processed_urls WHERE status = 0 or status = 1 LIMIT 1')
        result = cursor.fetchone()
        return result[0] if result else None


def update_url_status(url, status):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE processed_urls SET status = ? WHERE url = ?', (status, url))
        conn.commit()


def add_processed_url(url):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR IGNORE INTO processed_urls (url) VALUES (?)', (url,))
        cursor.execute('SELECT id FROM processed_urls WHERE url = ?', (url,))
        result = cursor.fetchone()
        conn.commit()
        return result[0] if result else None


def save_parsed_data(data, crawler_type='freepik'):
    """
    Save parsed data into both SQLite (commented) and MySQL databases.
    """
    # Save data to SQLite
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if crawler_type == 'freepik':
            cursor.execute('''
                INSERT INTO freepik_parsed_data
                (url, meta_title, meta_description, description, name_of_file, name_of_creator,
                 creator_link, breadcrumb, preview_link, tags, attributes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('url'),
                data.get('meta_title'),
                data.get('meta_description'),
                data.get('description'),
                data.get('name_of_file'),
                data.get('name_of_creator'),
                data.get('creator_link'),
                data.get('breadcrumb'),
                data.get('preview_link'),
                json.dumps(data.get('tags')),  # Store as JSON string
                json.dumps(data.get('attributes'))  # Store as JSON string
            ))
        elif crawler_type == 'envato':
            cursor.execute('''
            INSERT INTO envato_parsed_data
            (url, meta_title, meta_description, description, name_of_file, name_of_creator,
             creator_link, breadcrumb, preview_link, tags, attributes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('url'),
                data.get('meta_title'),
                data.get('meta_description'),
                data.get('description'),
                data.get('name_of_file'),
                data.get('name_of_creator'),
                data.get('creator_link'),
                data.get('breadcrumb'),
                data.get('preview_link'),
                json.dumps(data.get('tags')),  # Store as JSON string
                json.dumps(data.get('attributes'))  # Store as JSON string
            ))
        conn.commit()
