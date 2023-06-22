# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

main= Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('src\\bitmaps', 'bitmaps'), ('src\\default_config.json', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
main_pyz = PYZ(main.pure, main.zipped_data, cipher=block_cipher)
main_exe = EXE(
    main_pyz,
    main.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo\\logo.ico'],
)
migrate = Analysis(
    ['src\\migratev2tov3.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
migrate_pyz = PYZ(migrate.pure, migrate.zipped_data, cipher=block_cipher)
migrate_exe = EXE(
    migrate_pyz,
    migrate.scripts,
    [],
    exclude_binaries=True,
    name='migratev2tov3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    main_exe,
    main.binaries,
    main.zipfiles,
    main.datas,
    migrate_exe,
    migrate.binaries,
    migrate.zipfiles,
    migrate.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SimpleClinicV3.1',
)
