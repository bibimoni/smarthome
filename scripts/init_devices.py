#!/usr/bin/env python3
"""
Device Initialization Script for YoloHome IoT System.

This script helps initialize new devices into the system.
It can be used to:
- Create default sensors and actuators for YoloBit
- Create Adafruit IO feeds
- Register devices to user accounts
- Set up default threshold rules

Usage:
    python scripts/init_devices.py [--user-email EMAIL] [--create-feeds]
"""

import os
import sys
import argparse
import secrets

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_app
from app.extensions import db
from app.models.user import User
from app.models.device import Sensor, Actuator
from app.models.automation import ThresholdRule
from app.services.device_service import DeviceService


def create_default_devices():
    """Create default sensors and actuators for YoloBit."""
    print("\n=== Creating Default Devices ===\n")
    
    # Create sensors
    sensors_created = 0
    for sensor_config in DeviceService.DEFAULT_SENSORS:
        existing = Sensor.query.filter_by(feed_key=sensor_config['feed_key']).first()
        if existing:
            print(f"  [SKIP] Sensor '{sensor_config['name']}' already exists")
            continue
        
        sensor = Sensor(**sensor_config)
        db.session.add(sensor)
        print(f"  [CREATE] Sensor: {sensor_config['name']} ({sensor_config['type']})")
        sensors_created += 1
    
    # Create actuators
    actuators_created = 0
    for actuator_config in DeviceService.DEFAULT_ACTUATORS:
        existing = Actuator.query.filter_by(feed_key=actuator_config['feed_key']).first()
        if existing:
            print(f"  [SKIP] Actuator '{actuator_config['name']}' already exists")
            continue
        
        actuator = Actuator(**actuator_config)
        db.session.add(actuator)
        print(f"  [CREATE] Actuator: {actuator_config['name']} ({actuator_config['type']})")
        actuators_created += 1
    
    db.session.commit()
    
    print(f"\n  Created {sensors_created} sensors, {actuators_created} actuators")
    return sensors_created + actuators_created


def create_default_threshold_rules():
    """Create some default threshold rules for demonstration."""
    print("\n=== Creating Default Threshold Rules ===\n")
    
    rules = [
        {
            'sensor_feed': 'temperature',
            'operator': '>',
            'threshold_value': 30.0,
            'actuator_feed': 'fan',
            'action_value': 'ON',
            'description': 'Turn on fan when temperature > 30°C'
        },
        {
            'sensor_feed': 'temperature',
            'operator': '<',
            'threshold_value': 25.0,
            'actuator_feed': 'fan',
            'action_value': 'OFF',
            'description': 'Turn off fan when temperature < 25°C'
        },
        {
            'sensor_feed': 'light',
            'operator': '<',
            'threshold_value': 1000.0,
            'actuator_feed': 'led',
            'action_value': 'ON',
            'description': 'Turn on LED when light < 1000'
        },
        {
            'sensor_feed': 'light',
            'operator': '>',
            'threshold_value': 2000.0,
            'actuator_feed': 'led',
            'action_value': 'OFF',
            'description': 'Turn off LED when light > 2000'
        }
    ]
    
    rules_created = 0
    for rule_config in rules:
        sensor = Sensor.query.filter_by(feed_key=rule_config['sensor_feed']).first()
        actuator = Actuator.query.filter_by(feed_key=rule_config['actuator_feed']).first()
        
        if not sensor or not actuator:
            print(f"  [SKIP] Rule '{rule_config['description']}' - missing sensor or actuator")
            continue
        
        # Check if rule already exists
        existing = ThresholdRule.query.filter_by(
            sensor_id=sensor.id,
            operator=rule_config['operator'],
            threshold_value=rule_config['threshold_value'],
            actuator_id=actuator.id
        ).first()
        
        if existing:
            print(f"  [SKIP] Rule already exists: {rule_config['description']}")
            continue
        
        rule = ThresholdRule(
            sensor_id=sensor.id,
            operator=rule_config['operator'],
            threshold_value=rule_config['threshold_value'],
            actuator_id=actuator.id,
            action_value=rule_config['action_value'],
            description=rule_config['description'],
            is_active=True
        )
        db.session.add(rule)
        print(f"  [CREATE] Rule: {rule_config['description']}")
        rules_created += 1
    
    db.session.commit()
    print(f"\n  Created {rules_created} threshold rules")
    return rules_created


def create_demo_user(email: str = None):
    """Create a demo user for testing."""
    print("\n=== Creating Demo User ===\n")
    
    if not email:
        email = 'demo@yolohome.com'
    
    existing = User.query.filter_by(email=email).first()
    if existing:
        print(f"  [SKIP] User '{email}' already exists")
        print(f"  User ID: {existing.id}")
        return existing
    
    user = User(
        email=email,
        first_name='Demo',
        last_name='User',
        is_active=True,
        is_verified=True
    )
    user.set_password('demo1234')
    
    db.session.add(user)
    db.session.commit()
    
    print(f"  [CREATE] User: {email}")
    print(f"  Password: demo1234")
    print(f"  User ID: {user.id}")
    
    return user


def generate_device_token():
    """Generate a unique device token for device authentication."""
    return secrets.token_urlsafe(32)


def print_device_info():
    """Print information about configured devices."""
    print("\n=== Device Information ===\n")
    
    sensors = Sensor.query.filter_by(is_active=True).all()
    actuators = Actuator.query.filter_by(is_active=True).all()
    
    print("Sensors:")
    for sensor in sensors:
        latest = sensor.get_latest_data()
        print(f"  - {sensor.name} ({sensor.type})")
        print(f"    Feed: {sensor.feed_key}")
        print(f"    Unit: {sensor.unit}")
        if latest:
            print(f"    Current: {latest.value} {sensor.unit}")
    
    print("\nActuators:")
    for actuator in actuators:
        print(f"  - {actuator.name} ({actuator.type})")
        print(f"    Feed: {actuator.feed_key}")
        print(f"    Current: {actuator.current_value}")
        print(f"    Mode: {actuator.mode}")


def print_adafruit_feed_names(app):
    """Print Adafruit feed names for configuration."""
    print("\n=== Adafruit IO Feed Names ===\n")
    
    username = app.config.get('ADAFRUIT_AIO_USERNAME')
    
    sensors = Sensor.query.filter_by(is_active=True).all()
    actuators = Actuator.query.filter_by(is_active=True).all()
    
    print("Configure these feeds in Adafruit IO:\n")
    
    print("Sensors (publish from YoloBit):")
    for sensor in sensors:
        print(f"  - {username}/feeds/{sensor.feed_key}")
    
    print("\nActuators (subscribe on YoloBit):")
    for actuator in actuators:
        print(f"  - {username}/feeds/{actuator.feed_key}")
    
    print(f"\nAdafruit IO Username: {username}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Initialize YoloHome devices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/init_devices.py
    python scripts/init_devices.py --user-email user@example.com
    python scripts/init_devices.py --show-info
        """
    )
    
    parser.add_argument(
        '--user-email',
        type=str,
        help='Create a demo user with this email'
    )
    parser.add_argument(
        '--create-defaults',
        action='store_true',
        default=True,
        help='Create default devices and threshold rules'
    )
    parser.add_argument(
        '--show-info',
        action='store_true',
        help='Show device information after initialization'
    )
    parser.add_argument(
        '--generate-token',
        action='store_true',
        help='Generate a device authentication token'
    )
    
    args = parser.parse_args()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Create tables if not exist
        print("\nInitializing database...")
        db.create_all()
        
        if args.create_defaults:
            create_default_devices()
            create_default_threshold_rules()
        
        if args.user_email:
            create_demo_user(args.user_email)
        
        if args.generate_token:
            token = generate_device_token()
            print(f"\n=== Generated Device Token ===\n")
            print(f"  Token: {token}")
            print(f"\n  Use this token to authenticate your YoloBit device.")
        
        if args.show_info:
            print_device_info()
            print_adafruit_feed_names(app)
        
        if not any([args.create_defaults, args.user_email, args.generate_token, args.show_info]):
            # Default: create everything
            create_default_devices()
            create_default_threshold_rules()
            create_demo_user()
            print_device_info()
            print_adafruit_feed_names(app)
    
    print("\n=== Initialization Complete ===\n")


if __name__ == '__main__':
    main()