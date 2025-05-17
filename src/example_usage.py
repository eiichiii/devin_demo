#!/usr/bin/env python3
"""
Example script demonstrating how to use pg_to_csv.py with a mock PostgreSQL database.
This is for demonstration purposes only and doesn't require an actual database.
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pg_to_csv


def run_example():
    """Run an example export with mock data."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        output_file = temp_file.name
    
    sys.argv = [
        'pg_to_csv.py',
        '--host', 'localhost',
        '--port', '5432',
        '--dbname', 'example_db',
        '--user', 'example_user',
        '--password', 'example_pass',
        '--table', 'customers',
        '--output', output_file,
        '--delimiter', ',',
        '--encoding', 'utf-8'
    ]
    
    mock_data = [
        {'id': 1, 'name': '山田太郎', 'email': 'taro@example.com', 'active': True},
        {'id': 2, 'name': '佐藤花子', 'email': 'hanako@example.com', 'active': True},
        {'id': 3, 'name': '鈴木一郎', 'email': 'ichiro@example.com', 'active': False},
        {'id': 4, 'name': '田中美咲', 'email': 'misaki@example.com', 'active': True},
        {'id': 5, 'name': '伊藤健太', 'email': 'kenta@example.com', 'active': False}
    ]
    
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.description = [
            ('id', None, None, None, None, None, None),
            ('name', None, None, None, None, None, None),
            ('email', None, None, None, None, None, None),
            ('active', None, None, None, None, None, None)
        ]
        
        mock_cursor.fetchmany.side_effect = [mock_data, []]
        
        with patch('pg_to_csv.count_total_rows') as mock_count:
            mock_count.return_value = len(mock_data)
            
            try:
                pg_to_csv.main()
                print("\n\nExample completed successfully!")
                print(f"CSV file created at: {output_file}")
                
                print("\nContents of the CSV file:")
                with open(output_file, 'r', encoding='utf-8') as f:
                    print(f.read())
                    
            except SystemExit:
                print("Script exited with an error.")
            finally:
                if os.path.exists(output_file):
                    os.remove(output_file)


if __name__ == "__main__":
    run_example()
