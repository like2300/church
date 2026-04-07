# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os
import sys

block_cipher = None

# Collect Django and related modules
hiddenimports = collect_submodules('django')
hiddenimports += [
    'django.core.management.commands.runserver',
    'django.core.wsgi',
    'church',
    'core',
    'core.settings',
    'core.urls',
    'church.urls',
    'church.views',
    'church.models',
    'church.forms',
    'church.admin',
    'whitenoise',
    'whitenoise.middleware',
    'django_countries',
    'django_unfold',
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Data files to include - using the correct format for Windows
datas = []

# Add Django app directories (source;dest format for Windows)
datas += [('church', 'church')]
datas += [('core', 'core')]
datas += [('templates', 'templates')]
datas += [('static', 'static')]
datas += [('staticfiles', 'staticfiles')]

# Add media folder if it exists
if os.path.exists('media'):
    datas += [('media', 'media')]

# Add manage.py and database
datas += [('manage.py', '.')]
if os.path.exists('db.sqlite3'):
    datas += [('db.sqlite3', '.')]

# Add launcher
datas += [('launcher.py', '.')]

# Collect data from installed packages
try:
    datas += collect_data_files('django')
    datas += collect_data_files('whitenoise')
    datas += collect_data_files('PIL')
    datas += collect_data_files('django_countries')
except Exception as e:
    print(f"Warning: Could not collect some data files: {e}")

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'tkinter.test',
        'django.contrib.gis',
        'django.contrib.postgres',
        'jinja2',
        'docutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DhavantCroissance',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # FALSE pour production - pas de console visible
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
