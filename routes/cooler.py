from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
import math

cooler_bp = Blueprint('cooler', __name__, url_prefix='/cooler')

# Structured Data from user's list
COLD_STORAGES = [
    {"id": 1, "name": "A Hampannagouda Cold Storage", "type": "Cold Storage", "address": "Sy.No.232, Jalihal Village", "manager": "A Hampannagouda", "mobile": "8600000000", "capacity": "86 MT", "lat": 16.1817, "lng": 75.6958},
    {"id": 2, "name": "A R Bagwan Cold Storage", "type": "Cold Storage", "address": "APMC YARD, Bagalkot", "manager": "A R Bagwan", "mobile": "9880000068", "capacity": "Unknown", "lat": 16.1850, "lng": 75.7000},
    {"id": 3, "name": "Bagalkot Milk Union Co-Op Ltd", "type": "Cold Storage", "address": "VIDYAGIRI INDL AREA", "manager": "Mahesh", "mobile": "9440000099", "capacity": "20 MT", "lat": 16.1680, "lng": 75.6550},
    {"id": 10, "name": "Green Food Park", "type": "Cold Storage", "address": "KIADB INDL AREA", "manager": "Parashu B", "mobile": "9440000023", "capacity": "2400 MT", "lat": 16.1900, "lng": 75.7100},
    {"id": 13, "name": "KSWC Warehouse", "type": "Warehouse", "address": "Bagalkot Town", "manager": "Government", "mobile": "08354-220000", "capacity": "5000 MT", "lat": 16.1800, "lng": 75.6900},
    {"id": 14, "name": "KSWC (Muchakandi)", "type": "Warehouse", "address": "Sy. No. 134, Muchakandi Village", "manager": "KSWC Manager", "mobile": "08354-221000", "capacity": "2152 MT", "lat": 16.1500, "lng": 75.6800},
    # Note: I am adding more data points below in the JS directly for performance
]

@cooler_bp.route('/')
@login_required
def index():
    return render_template('cooler/map.html')

@cooler_bp.route('/api/facilities')
@login_required
def get_facilities():
    return jsonify(COLD_STORAGES)
