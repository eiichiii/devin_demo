#!/usr/bin/env python3
"""
PostgreSQL to CSV Exporter

This script exports data from a PostgreSQL database table or SQL query to a CSV file.
It provides command-line options for database connection, query specification, and CSV formatting.
"""

import argparse
import csv
import os
import sys
import time
from typing import Dict, List, Optional, Union

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Export PostgreSQL data to CSV')

    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', type=int, default=5432, help='Database port')
    parser.add_argument('--dbname', required=True, help='Database name')
    parser.add_argument('--user', required=True, help='Database user')
    parser.add_argument('--password', help='Database password')

    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument('--table', help='Table name to export')
    query_group.add_argument('--sql', help='SQL query to execute')

    parser.add_argument('--output', required=True, help='Output CSV file path')

    parser.add_argument('--delimiter', default=',', help='CSV delimiter')
    parser.add_argument('--quotechar', default='"', help='CSV quote character')
    parser.add_argument('--encoding', default='utf-8', help='Output file encoding')
    parser.add_argument('--no-header', action='store_true', help='Do not include header row')

    parser.add_argument('--batch-size', type=int, default=10000,
                        help='Number of rows to fetch in each batch')

    return parser.parse_args()


def connect_to_database(args) -> psycopg2.extensions.connection:
    """Establish connection to the PostgreSQL database."""
    try:
        print(f"Connecting to database {args.dbname} on {args.host}:{args.port}...")

        conn_params = {
            'host': args.host,
            'port': args.port,
            'dbname': args.dbname,
            'user': args.user
        }

        if args.password:
            conn_params['password'] = args.password

        conn = psycopg2.connect(**conn_params)
        print("Database connection established successfully.")
        return conn

    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}", file=sys.stderr)
        sys.exit(1)


def get_query(args) -> sql.Composed:
    """Construct the SQL query based on input arguments."""
    if args.table:
        return sql.SQL("SELECT * FROM {}").format(sql.Identifier(args.table))
    else:
        return sql.SQL(args.sql)


def count_total_rows(cursor, query: sql.Composed, args) -> Optional[int]:
    """
    Attempt to count the total number of rows that will be exported.
    Returns None if counting is not possible (e.g., for complex queries).
    """
    try:
        if args.table and not args.sql:
            try:
                count_query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(args.table))
                cursor.execute(count_query)
                return cursor.fetchone()[0]
            except Exception:
                return None
        return None
    except Exception:
        # If we can't count for any reason, just return None
        return None


def export_data(args):
    """Export data from PostgreSQL to CSV file."""
    conn = connect_to_database(args)

    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = get_query(args)

                total_rows = count_total_rows(cursor, query, args)
                if total_rows:
                    print(f"Exporting approximately {total_rows:,} rows...")
                else:
                    print("Exporting data (row count unknown)...")

                cursor.execute(query)

                with open(args.output, 'w', newline='', encoding=args.encoding) as csvfile:
                    if cursor.description:
                        fieldnames = [desc[0] for desc in cursor.description]

                        writer = csv.DictWriter(
                            csvfile,
                            fieldnames=fieldnames,
                            delimiter=args.delimiter,
                            quotechar=args.quotechar,
                            quoting=csv.QUOTE_MINIMAL
                        )

                        if not args.no_header:
                            writer.writeheader()

                        start_time = time.time()
                        rows_processed = 0

                        while True:
                            rows = cursor.fetchmany(args.batch_size)
                            if not rows:
                                break

                            writer.writerows(rows)
                            rows_processed += len(rows)

                            elapsed = time.time() - start_time
                            if total_rows:
                                percentage = min(100, rows_processed * 100 / total_rows)
                                print(f"\rProgress: {rows_processed:,}/{total_rows:,} rows ({percentage:.1f}%) - "
                                      f"Elapsed: {elapsed:.1f}s", end='', flush=True)
                            else:
                                print(f"\rRows exported: {rows_processed:,} - Elapsed: {elapsed:.1f}s",
                                      end='', flush=True)

                        elapsed = time.time() - start_time
                        print(f"\nExport completed: {rows_processed:,} rows exported in {elapsed:.2f} seconds.")
                        print(f"Output file: {os.path.abspath(args.output)}")
                    else:
                        print("No data returned from query.")

    except psycopg2.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"I/O error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


def main():
    """Main entry point for the script."""
    args = parse_arguments()
    export_data(args)


if __name__ == "__main__":
    main()
