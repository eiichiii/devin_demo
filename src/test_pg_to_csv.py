#!/usr/bin/env python3
"""
Test script for pg_to_csv.py that mocks the PostgreSQL connection
to verify basic functionality without an actual database.
"""

import argparse
import csv
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import pg_to_csv

original_count_total_rows = pg_to_csv.count_total_rows
def mock_count_total_rows(cursor, query, args):
    return None
pg_to_csv.count_total_rows = mock_count_total_rows


class TestPgToCsv(unittest.TestCase):
    """Test cases for pg_to_csv.py"""

    def setUp(self):
        """Set up test fixtures"""
        self.output_file = "test_output.csv"
        
        self.args = argparse.Namespace(
            host='localhost',
            port=5432,
            dbname='testdb',
            user='testuser',
            password='testpass',
            table='testtable',
            sql=None,
            output=self.output_file,
            delimiter=',',
            quotechar='"',
            encoding='utf-8',
            no_header=False,
            batch_size=10000
        )

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    @patch('psycopg2.connect')
    def test_table_export(self, mock_connect):
        """Test exporting a table"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.description = [
            ('id', None, None, None, None, None, None),
            ('name', None, None, None, None, None, None),
            ('email', None, None, None, None, None, None)
        ]
        
        mock_data = [
            {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
            {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'},
            {'id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com'}
        ]
        
        mock_cursor.fetchmany.side_effect = [mock_data, []]
        
        pg_to_csv.export_data(self.args)
        
        mock_connect.assert_called_once_with(
            host='localhost',
            port=5432,
            dbname='testdb',
            user='testuser',
            password='testpass'
        )
        
        mock_cursor.execute.assert_called()
        
        self.assertTrue(os.path.exists(self.output_file))
        
        with open(self.output_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
            self.assertEqual(len(rows), 3)
            
            self.assertEqual(rows[0]['name'], 'John Doe')
            self.assertEqual(rows[1]['email'], 'jane@example.com')
            self.assertEqual(rows[2]['id'], '3')  # CSV reader returns strings

    @patch('psycopg2.connect')
    def test_sql_export(self, mock_connect):
        """Test exporting with a custom SQL query"""
        self.args.table = None
        self.args.sql = "SELECT id, name, email FROM testtable WHERE id > 1"
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.description = [
            ('id', None, None, None, None, None, None),
            ('name', None, None, None, None, None, None),
            ('email', None, None, None, None, None, None)
        ]
        
        mock_data = [
            {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'},
            {'id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com'}
        ]
        
        mock_cursor.fetchmany.side_effect = [mock_data, []]
        
        pg_to_csv.export_data(self.args)
        
        self.assertTrue(os.path.exists(self.output_file))
        
        with open(self.output_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
            self.assertEqual(len(rows), 2)
            
            self.assertEqual(rows[0]['id'], '2')
            self.assertEqual(rows[1]['name'], 'Bob Johnson')

    @patch('psycopg2.connect')
    def test_no_header(self, mock_connect):
        """Test exporting without a header row"""
        self.args.no_header = True
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.description = [
            ('id', None, None, None, None, None, None),
            ('name', None, None, None, None, None, None)
        ]
        
        mock_data = [
            {'id': 1, 'name': 'John Doe'},
            {'id': 2, 'name': 'Jane Smith'}
        ]
        
        mock_cursor.fetchmany.side_effect = [mock_data, []]
        
        pg_to_csv.export_data(self.args)
        
        self.assertTrue(os.path.exists(self.output_file))
        
        with open(self.output_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            
            self.assertEqual(len(rows), 2)
            
            self.assertIn('John Doe', rows[0])


if __name__ == '__main__':
    unittest.main()
