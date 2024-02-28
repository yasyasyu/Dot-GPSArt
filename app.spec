# -*- mode: python ; coding: utf-8 -*-



a = Analysis(
    [
        'app.py',
        'pages/app_download.py',
        'pages/app_view.py'
    ],
    
    pathex=[],
    binaries=[],
    datas=[
        ('pages/app_download.py','pages/app_download'),
        ('pages/app_view.py','pages/app_view'),
        ('C:/Users/yas_yasyu/anaconda3/envs/geox/Lib/site-packages/dash', 'dash'),
        ('C:/Users/yas_yasyu/anaconda3/envs/geox/Lib/site-packages/dash_leaflet', 'dash_leaflet'),
        ('C:/Users/yas_yasyu/anaconda3/envs/geox/Lib/site-packages/dash_core_components', 'dash_core_components'),
        ('C:/Users/yas_yasyu/anaconda3/envs/geox/Lib/site-packages/dash_extensions', 'dash_extensions'),
        ('C:/Users/yas_yasyu/anaconda3/envs/geox/Lib/site-packages/dash_html_components', 'dash_html_components')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
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
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
