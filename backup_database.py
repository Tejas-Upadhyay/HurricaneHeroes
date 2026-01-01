import sqlite3
import sys

try:
    # Connect to database
    conn = sqlite3.connect('db.sqlite3')
    
    # Create backup file
    with open('backup.sql', 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)
    
    conn.close()
    
    # Get file size
    import os
    file_size = os.path.getsize('backup.sql')
    
    print(f"✓ Backup created successfully!")
    print(f"✓ File: backup.sql")
    print(f"✓ Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    print(f"✓ Location: {os.path.abspath('backup.sql')}")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)


