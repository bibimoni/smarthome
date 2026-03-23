#!/usr/bin/env python3
"""
Development Setup Script for YoloHome Backend

This script sets up a development environment by:
1. Creating a user account (interactive)
2. Letting you add multiple devices of any type
3. Setting up automation rules

Usage:
    python scripts/dev_setup.py
"""

import os
import sys
from getpass import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_app
from app.extensions import db
from app.models.user import User
from app.models.device import Sensor, Actuator
from app.models.automation import ThresholdRule
from werkzeug.security import generate_password_hash


# Available YoloBit device types
SENSOR_TYPES = {
    '1': {'name': 'Temperature Sensor', 'type': 'temperature', 'unit': '°C', 'icon': '🌡️'},
    '2': {'name': 'Humidity Sensor', 'type': 'humidity', 'unit': '%', 'icon': '💧'},
    '3': {'name': 'Light Sensor', 'type': 'light', 'unit': 'lux', 'icon': '☀️'},
    '4': {'name': 'PIR Motion Sensor', 'type': 'pir', 'unit': 'boolean', 'icon': '🚶'},
}

ACTUATOR_TYPES = {
    '1': {'name': 'Fan', 'type': 'fan', 'icon': '🌀'},
    '2': {'name': 'LED', 'type': 'led', 'icon': '💡'},
    '3': {'name': 'RGB LED', 'type': 'rgb', 'icon': '🌈'},
    '4': {'name': 'LCD1602 Display', 'type': 'lcd', 'icon': '📺'},
}

# Locations for easy selection
LOCATIONS = [
    'Living Room',
    'Bedroom',
    'Kitchen',
    'Bathroom',
    'Garage',
    'Garden',
    'Office',
    'Hallway',
    'Custom',
]


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50 + "\n")


def print_success(message):
    """Print a success message."""
    print(f"✅ {message}")


def print_error(message):
    """Print an error message."""
    print(f"❌ {message}")


def print_info(message):
    """Print an info message."""
    print(f"ℹ️  {message}")


def print_device_list(devices, device_type='sensor'):
    """Print a list of devices."""
    if not devices:
        print("   No devices added yet.")
        return
    
    print(f"\n   Added {device_type}s:")
    for i, device in enumerate(devices, 1):
        print(f"   {i}. {device['name']} ({device['location']}) - Type: {device['type']}")


def get_user_input():
    """Get user registration details."""
    print_header("YoloHome Development Setup")
    print("This script will help you set up your development environment.\n")
    
    # Default credentials for quick setup
    print_info("Press Enter to use default credentials (dev@yolohome.com / dev1234)")
    email = input("📧 Enter your email: ").strip()
    
    # Use default if empty
    if not email:
        email = "dev@yolohome.com"
        password = "dev1234"
        first_name = "Dev"
        last_name = "User"
        print_success(f"Using default credentials: {email}")
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print_info(f"User {email} already exists.")
            return existing_user, False
        
        return {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name
        }, True
    
    # Validate email
    if '@' not in email or '.' not in email:
        print_error("Please enter a valid email address.")
        return get_user_input()
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print_info(f"User {email} already exists.")
        use_existing = input("Use existing account? (y/n): ").strip().lower()
        if use_existing == 'y':
            return existing_user, False
        else:
            print_info("Please use a different email.")
            return get_user_input()
    
    # Get password
    print_info("Press Enter to use default password: dev1234")
    password = getpass("🔑 Enter password (min 6 chars): ").strip()
    if not password:
        password = "dev1234"
        print_success("Using default password: dev1234")
    else:
        while len(password) < 6:
            print_error("Password must be at least 6 characters.")
            password = getpass("🔑 Enter password (min 6 chars): ").strip()
        
        confirm = getpass("🔑 Confirm password: ").strip()
        if password != confirm:
            print_error("Passwords do not match.")
            return get_user_input()
    
    # Get name
    first_name = input("👤 First name (optional): ").strip() or "User"
    last_name = input("👤 Last name (optional): ").strip() or ""
    
    return {
        'email': email,
        'password': password,
        'first_name': first_name,
        'last_name': last_name
    }, True


def select_location():
    """Let user select a location for the device."""
    print("\n   Select location:")
    for i, loc in enumerate(LOCATIONS, 1):
        print(f"   [{i}] {loc}")
    
    choice = input("\n   👉 Location (1-9): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(LOCATIONS) - 1:
            return LOCATIONS[idx]
        elif idx == len(LOCATIONS) - 1:
            # Custom location
            custom = input("   Enter custom location: ").strip()
            return custom or "Unknown"
    except ValueError:
        pass
    
    return "Main Room"


def add_sensors_menu():
    """Interactive menu to add multiple sensors."""
    sensors = []
    
    while True:
        print_header("Add Sensors")
        print_device_list(sensors, 'sensor')
        
        print("\n   Available Sensor Types:")
        for key, sensor in SENSOR_TYPES.items():
            print(f"   [{key}] {sensor['icon']} {sensor['name']}")
        
        print("\n   [A] Add a sensor")
        print("   [D] Remove a sensor")
        print("   [Q] Done adding sensors")
        
        choice = input("\n   👉 Your choice: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'd':
            if sensors:
                print_device_list(sensors, 'sensor')
                try:
                    idx = int(input("   Enter number to remove: ").strip()) - 1
                    if 0 <= idx < len(sensors):
                        removed = sensors.pop(idx)
                        print_success(f"Removed {removed['name']}")
                except ValueError:
                    print_error("Invalid number")
        elif choice == 'a' or choice in SENSOR_TYPES:
            if choice == 'a':
                type_choice = input("   Select type (1-4): ").strip()
            else:
                type_choice = choice
            
            if type_choice in SENSOR_TYPES:
                sensor_type = SENSOR_TYPES[type_choice]
                
                # Get custom name
                default_name = f"{sensor_type['name']}"
                custom_name = input(f"   Name (default: {default_name}): ").strip()
                name = custom_name or default_name
                
                # Get location
                location = select_location()
                
                sensors.append({
                    'name': name,
                    'type': sensor_type['type'],
                    'unit': sensor_type['unit'],
                    'location': location,
                    'icon': sensor_type['icon']
                })
                print_success(f"Added {name} in {location}")
        else:
            print_error("Invalid choice")
    
    return sensors


def add_actuators_menu():
    """Interactive menu to add multiple actuators."""
    actuators = []
    
    while True:
        print_header("Add Actuators")
        print_device_list(actuators, 'actuator')
        
        print("\n   Available Actuator Types:")
        for key, actuator in ACTUATOR_TYPES.items():
            print(f"   [{key}] {actuator['icon']} {actuator['name']}")
        
        print("\n   [A] Add an actuator")
        print("   [D] Remove an actuator")
        print("   [Q] Done adding actuators")
        
        choice = input("\n   👉 Your choice: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'd':
            if actuators:
                print_device_list(actuators, 'actuator')
                try:
                    idx = int(input("   Enter number to remove: ").strip()) - 1
                    if 0 <= idx < len(actuators):
                        removed = actuators.pop(idx)
                        print_success(f"Removed {removed['name']}")
                except ValueError:
                    print_error("Invalid number")
        elif choice == 'a' or choice in ACTUATOR_TYPES:
            if choice == 'a':
                type_choice = input("   Select type (1-4): ").strip()
            else:
                type_choice = choice
            
            if type_choice in ACTUATOR_TYPES:
                actuator_type = ACTUATOR_TYPES[type_choice]
                
                # Get custom name
                default_name = f"{actuator_type['name']}"
                custom_name = input(f"   Name (default: {default_name}): ").strip()
                name = custom_name or default_name
                
                # Get location
                location = select_location()
                
                actuators.append({
                    'name': name,
                    'type': actuator_type['type'],
                    'location': location,
                    'icon': actuator_type['icon']
                })
                print_success(f"Added {name} in {location}")
        else:
            print_error("Invalid choice")
    
    return actuators


def create_user(user_data):
    """Create a new user account."""
    user = User(
        email=user_data['email'],
        password_hash=generate_password_hash(user_data['password']),
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        is_active=True,
        is_verified=True  # Auto-verify in development
    )
    db.session.add(user)
    db.session.commit()
    return user


def create_sensors(user, sensors):
    """Create sensors for the user."""
    created = []
    for sensor_data in sensors:
        sensor = Sensor(
            user_id=user.id,
            name=sensor_data['name'],
            sensor_type=sensor_data['type'],
            unit=sensor_data['unit'],
            location=sensor_data['location'],
            is_active=True,
            min_threshold=0.0,
            max_threshold=100.0 if sensor_data['type'] == 'humidity' else 50.0
        )
        db.session.add(sensor)
        created.append(sensor)
    
    db.session.commit()
    return created


def create_actuators(user, actuators):
    """Create actuators for the user."""
    created = []
    for actuator_data in actuators:
        actuator = Actuator(
            user_id=user.id,
            name=actuator_data['name'],
            actuator_type=actuator_data['type'],
            location=actuator_data['location'],
            is_active=True,
            mode='auto',
            current_state='off'
        )
        db.session.add(actuator)
        created.append(actuator)
    
    db.session.commit()
    return created


def create_default_thresholds(user, sensors, actuators):
    """Create default threshold rules for the user."""
    rules = []
    
    # Group sensors by type
    temp_sensors = [s for s in sensors if s.sensor_type == 'temperature']
    humidity_sensors = [s for s in sensors if s.sensor_type == 'humidity']
    light_sensors = [s for s in sensors if s.sensor_type == 'light']
    
    # Group actuators by type
    fans = [a for a in actuators if a.actuator_type == 'fan']
    leds = [a for a in actuators if a.actuator_type == 'led']
    
    # Create temperature -> fan rules
    for i, temp_sensor in enumerate(temp_sensors):
        if i < len(fans):
            fan = fans[i]
            rule = ThresholdRule(
                user_id=user.id,
                name=f"Auto {fan.name} on High Temp",
                description=f"Turn on {fan.name} when {temp_sensor.name} exceeds 30°C",
                sensor_id=temp_sensor.id,
                condition="greater_than",
                threshold_value=30.0,
                actuator_id=fan.id,
                action="on",
                action_value="75",
                is_active=True
            )
            db.session.add(rule)
            rules.append(rule)
    
    # Create humidity -> fan rules
    for i, humidity_sensor in enumerate(humidity_sensors):
        if i < len(fans):
            fan = fans[min(i, len(fans)-1)]
            rule = ThresholdRule(
                user_id=user.id,
                name=f"Auto {fan.name} on High Humidity",
                description=f"Turn on {fan.name} when {humidity_sensor.name} exceeds 70%",
                sensor_id=humidity_sensor.id,
                condition="greater_than",
                threshold_value=70.0,
                actuator_id=fan.id,
                action="on",
                action_value="50",
                is_active=True
            )
            db.session.add(rule)
            rules.append(rule)
    
    # Create light -> LED rules
    for i, light_sensor in enumerate(light_sensors):
        if i < len(leds):
            led = leds[i]
            rule = ThresholdRule(
                user_id=user.id,
                name=f"Auto {led.name} on Low Light",
                description=f"Turn on {led.name} when {light_sensor.name} is below 300 lux",
                sensor_id=light_sensor.id,
                condition="less_than",
                threshold_value=300.0,
                actuator_id=led.id,
                action="on",
                is_active=True
            )
            db.session.add(rule)
            rules.append(rule)
    
    db.session.commit()
    return rules


def print_summary(user, sensors, actuators, rules):
    """Print a summary of the setup."""
    print_header("Setup Complete! 🎉")
    
    print("📋 Account Details:")
    print(f"   Email: {user.email}")
    print(f"   Name: {user.first_name} {user.last_name}")
    print()
    
    print("📡 Sensors Created:")
    if sensors:
        for s in sensors:
            print(f"   • {s.name} (ID: {s.id})")
            print(f"     Type: {s.sensor_type}, Location: {s.location}")
    else:
        print("   None")
    print()
    
    print("🔌 Actuators Created:")
    if actuators:
        for a in actuators:
            print(f"   • {a.name} (ID: {a.id})")
            print(f"     Type: {a.actuator_type}, Location: {a.location}")
    else:
        print("   None")
    print()
    
    print("⚙️  Automation Rules Created:")
    if rules:
        for r in rules:
            print(f"   • {r.name}")
    else:
        print("   None")
    print()
    
    print("=" * 50)
    print("  Quick Start Guide")
    print("=" * 50)
    print()
    print("1. Start the server:")
    print("   flask run")
    print()
    print("2. Login to get your access token:")
    print(f"   curl -X POST http://localhost:5000/api/auth/login \\")
    print(f"        -H 'Content-Type: application/json' \\")
    print(f"        -d '{{\"email\": \"{user.email}\", \"password\": \"YOUR_PASSWORD\"}}'")
    print()
    print("3. Use the token in subsequent requests:")
    print("   curl http://localhost:5000/api/sensors \\")
    print("        -H 'Authorization: Bearer YOUR_TOKEN'")
    print()
    print("4. API Documentation: See API.md")
    print()


def main():
    """Main entry point."""
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Create tables if not exist
        db.create_all()
        
        try:
            # Get user input
            user_data, is_new = get_user_input()
            
            if is_new:
                # Create user
                user = create_user(user_data)
                print_success(f"Account created for {user.email}")
            else:
                user = user_data
                print_success(f"Using existing account: {user.email}")
            
            # Add sensors interactively
            selected_sensors = add_sensors_menu()
            
            # Add actuators interactively
            selected_actuators = add_actuators_menu()
            
            if not selected_sensors and not selected_actuators:
                print_error("No devices selected. Nothing to do.")
                return
            
            # Create devices
            sensors = create_sensors(user, selected_sensors)
            print_success(f"Created {len(sensors)} sensor(s)")
            
            actuators = create_actuators(user, selected_actuators)
            print_success(f"Created {len(actuators)} actuator(s)")
            
            # Create default automation rules
            rules = create_default_thresholds(user, sensors, actuators)
            print_success(f"Created {len(rules)} automation rule(s)")
            
            # Print summary
            print_summary(user, sensors, actuators, rules)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup cancelled by user.")
        except Exception as e:
            print_error(f"Setup failed: {str(e)}")
            raise


if __name__ == '__main__':
    main()