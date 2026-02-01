#!/usr/bin/env python3
"""
G4 - Automatic Migration Script
Updates code to match the real PostgreSQL schema
"""

import os
import shutil
from pathlib import Path

def backup_old_files():
    """Backup original files"""
    print("=" * 60)
    print("G4 - AUTOMATIC MIGRATION SCRIPT")
    print("=" * 60)
    print("\n[STEP 1] Backing up original files...")
    
    src_dir = Path("src")
    backup_dir = Path("backup_old_schema")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "database.py",
        "preprocessor.py",
        "scoring_engine.py",
        "roi_calculator.py"
    ]
    
    for filename in files_to_backup:
        src_file = src_dir / filename
        if src_file.exists():
            backup_file = backup_dir / filename
            shutil.copy2(src_file, backup_file)
            print(f"  ✓ Backed up: {filename} → backup_old_schema/{filename}")
        else:
            print(f"  ⚠ Not found: {filename} (skipping)")
    
    print("\n✓ Backup complete")

def migrate_files():
    """Replace old files with updated versions"""
    print("\n[STEP 2] Migrating to new schema...")
    
    src_dir = Path("src")
    
    migrations = {
        "database_updated.py": "database.py",
        "preprocessor_updated.py": "preprocessor.py",
        "scoring_engine_updated.py": "scoring_engine.py",
        "roi_calculator_updated.py": "roi_calculator.py"
    }
    
    for updated_file, target_file in migrations.items():
        src_path = src_dir / updated_file
        target_path = src_dir / target_file
        
        if src_path.exists():
            # Remove old file if exists
            if target_path.exists():
                target_path.unlink()
            
            # Rename updated file to target name
            shutil.move(str(src_path), str(target_path))
            print(f"  ✓ Migrated: {updated_file} → {target_file}")
        else:
            print(f"  ✗ Missing: {updated_file}")
    
    print("\n✓ Migration complete")

def verify_migration():
    """Verify that migration was successful"""
    print("\n[STEP 3] Verifying migration...")
    
    src_dir = Path("src")
    
    required_files = [
        "database.py",
        "preprocessor.py",
        "scoring_engine.py",
        "roi_calculator.py"
    ]
    
    all_ok = True
    for filename in required_files:
        filepath = src_dir / filename
        if filepath.exists():
            # Check if file contains new column names
            with open(filepath, 'r') as f:
                content = f.read()
                if 'global_active_power_kw' in content or 'ts' in content:
                    print(f"  ✓ {filename} - using new schema")
                else:
                    print(f"  ⚠ {filename} - might still use old schema")
                    all_ok = False
        else:
            print(f"  ✗ {filename} - missing!")
            all_ok = False
    
    if all_ok:
        print("\n✓ Verification successful - all files updated")
    else:
        print("\n⚠ Verification found issues - please check manually")
    
    return all_ok

def test_imports():
    """Test that imports work"""
    print("\n[STEP 4] Testing imports...")
    
    try:
        from src.database import DatabaseConnection
        print("  ✓ database.DatabaseConnection")
        
        from src.preprocessor import DataPreprocessor
        print("  ✓ preprocessor.DataPreprocessor")
        
        from src.anomaly_detector import AnomalyDetector
        print("  ✓ anomaly_detector.AnomalyDetector")
        
        from src.roi_calculator import ROICalculator
        print("  ✓ roi_calculator.ROICalculator")
        
        print("\n✓ All imports successful")
        return True
        
    except Exception as e:
        print(f"\n✗ Import error: {e}")
        return False

def main():
    """Main migration function"""
    try:
        # Step 1: Backup
        backup_old_files()
        
        # Step 2: Migrate
        migrate_files()
        
        # Step 3: Verify
        if not verify_migration():
            print("\n⚠ WARNING: Verification found issues")
            print("Please check the files manually")
            return
        
        # Step 4: Test imports
        if not test_imports():
            print("\n⚠ WARNING: Import test failed")
            print("Please check for Python errors")
            return
        
        # Success
        print("\n" + "=" * 60)
        print("✓ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review the changes in backup_old_schema/")
        print("2. Test database connection: python src/database.py")
        print("3. Train the model: python train_model.py")
        print("4. Run scoring: python src/scoring_engine.py --mode once")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        print("\nTo restore original files:")
        print("  cp backup_old_schema/*.py src/")

if __name__ == "__main__":
    main()
