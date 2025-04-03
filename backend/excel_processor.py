import sqlite3
import pandas as pd
import os
import shutil
import datetime
from typing import List, Dict
from fastapi import HTTPException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelSQLiteSync:
    def __init__(self, excel_path: str, db_path: str):
        """
        Initialize with manual synchronization only
        """
        self.excel_path = os.path.abspath(excel_path)
        self.db_path = os.path.abspath(db_path)
        self.backup_dir = os.path.abspath("backups")
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

        # Initial import from Excel to SQLite
        self.excel_to_sqlite()

    def _create_backup(self, file_path: str) -> str:
        """Create timestamped backup"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_path = os.path.join(self.backup_dir, f"{filename}.bak_{timestamp}")
        
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup at {backup_path}")
            return backup_path
        return ""

    def _ensure_file_writable(self, file_path: str):
        """Check file permissions"""
        if not os.path.exists(file_path):
            open(file_path, 'w').close()
        elif not os.access(file_path, os.W_OK):
            raise PermissionError(f"No write permissions for {file_path}")

    def excel_to_sqlite(self):
        """Import Excel to SQLite with proper column name conversion"""
        try:
            if not os.path.exists(self.excel_path):
                raise FileNotFoundError(f"Excel file not found at {self.excel_path}")

            backup_path = self._create_backup(self.db_path)
            xls = pd.ExcelFile(self.excel_path)
            
            with sqlite3.connect(self.db_path) as conn:
                for sheet in xls.sheet_names:
                    df = pd.read_excel(self.excel_path, sheet_name=sheet)
                    
                    # Convert column names to valid database fields
                    df.columns = [
                        col.strip()                     # Remove whitespace
                        .lower()                        # Convert to lowercase
                        .replace(' ', '_')              # Replace spaces with underscores
                        .replace('-', '_')              # Replace hyphens with underscores
                        .replace('(', '')               # Remove special characters
                        .replace(')', '')
                        .replace('/', '_')
                        .replace('\\', '_')
                        .replace('.', '_')
                        .replace('$', '')
                        .replace('%', 'percent')
                        for col in df.columns
                    ]
                    
                    # Ensure no empty column names
                    df.columns = [f'col_{i}' if col == '' else col for i, col in enumerate(df.columns)]
                    
                    # Save to database
                    df.to_sql(
                        name=sheet.lower().replace(' ', '_'),
                        con=conn,
                        if_exists='replace',
                        index=False
                    )
                    logger.info(f"Imported sheet {sheet} to database")

            return {
                "message": "Excel data imported to SQLite with standardized column names",
                "backup_path": backup_path
            }
        except Exception as e:
            logger.error(f"Excel import failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Excel import failed: {str(e)}"
            )

    def sqlite_to_excel(self):
        """Export SQLite to Excel"""
        try:
            self._ensure_file_writable(self.excel_path)
            backup_path = self._create_backup(self.excel_path)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [table[0] for table in cursor.fetchall()]
                
                with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
                    for table in tables:
                        df = pd.read_sql(f"SELECT * FROM {table}", conn)
                        df.to_excel(writer, sheet_name=table, index=False)
                        logger.info(f"Exported table {table} to Excel")

            return {
                "message": "SQLite data exported to Excel",
                "backup_path": backup_path
            }
        except Exception as e:
            logger.error(f"Excel export failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Excel export failed: {str(e)}"
            )

    def get_asset_by_tag(self, asset_tag: str) -> List[Dict]:
        """Get asset details by tag"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Find all tables containing asset_tag
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND sql LIKE '%asset_tag%'
                )
            """)
            
            assets = []
            for table in cursor.fetchall():
                table_name = table[0]
                cursor.execute(f"SELECT * FROM {table_name} WHERE asset_tag = ?", (asset_tag,))
                result = cursor.fetchone()
                if result:
                    asset_data = dict(result)
                    asset_data['_source_table'] = table_name
                    assets.append(asset_data)
            
            return assets

    def reassign_asset(self, asset_tag: str, updates: Dict) -> bool:
        """Reassign asset with given updates"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Find tables containing asset_tag
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND sql LIKE '%asset_tag%'
                )
            """)
            
            updated = False
            for table in cursor.fetchall():
                table_name = table[0]
                # Build update query
                set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
                values = list(updates.values())
                values.append(asset_tag)
                
                cursor.execute(
                    f"UPDATE {table_name} SET {set_clause} WHERE asset_tag = ?",
                    values
                )
                if cursor.rowcount > 0:
                    conn.commit()
                    updated = True
                    break
            
            return updated