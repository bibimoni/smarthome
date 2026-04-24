import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from app.services.sensor_service import SensorService


class TestSensorService:
    @patch('app.services.sensor_service.Sensor')
    def test_get_all_sensors(self, mock_sensor_class):
        mock_sensors = [MagicMock(), MagicMock()]
        mock_sensor_class.query.filter_by.return_value.all.return_value = mock_sensors
        
        result = SensorService.get_all_sensors()
        
        assert len(result) == 2
    
    @patch('app.services.sensor_service.Sensor')
    def test_get_sensor_by_id(self, mock_sensor_class):
        mock_sensor = MagicMock()
        mock_sensor_class.query.get.return_value = mock_sensor
        
        result = SensorService.get_sensor_by_id(1)
        
        assert result == mock_sensor
    
    @patch('app.services.sensor_service.Sensor')
    def test_get_sensor_by_feed_key(self, mock_sensor_class):
        mock_sensor = MagicMock()
        mock_sensor_class.query.filter_by.return_value.first.return_value = mock_sensor
        
        result = SensorService.get_sensor_by_feed_key('temperature')
        
        assert result == mock_sensor
    
    @patch('app.services.sensor_service.Sensor')
    def test_get_sensors_by_type(self, mock_sensor_class):
        mock_sensors = [MagicMock()]
        mock_sensor_class.query.filter_by.return_value.all.return_value = mock_sensors
        
        result = SensorService.get_sensors_by_type('temperature')
        
        assert len(result) == 1
    
    @patch('app.services.sensor_service.Sensor')
    @patch('app.services.sensor_service.SensorData')
    @patch('app.services.sensor_service.db')
    def test_record_sensor_data_success(self, mock_db, mock_data_class, mock_sensor_class):
        mock_sensor = MagicMock()
        mock_sensor.min_value = 0
        mock_sensor.max_value = 100
        mock_sensor_class.query.get.return_value = mock_sensor
        
        data, error = SensorService.record_sensor_data(1, 50.0)
        
        assert error == ''
        mock_db.session.add.assert_called_once()
    
    @patch('app.services.sensor_service.Sensor')
    def test_record_sensor_data_sensor_not_found(self, mock_sensor_class):
        mock_sensor_class.query.get.return_value = None
        
        data, error = SensorService.record_sensor_data(999, 50.0)
        
        assert data is None
        assert 'not found' in error
    
    @patch('app.services.sensor_service.Sensor')
    def test_record_sensor_data_below_min(self, mock_sensor_class):
        mock_sensor = MagicMock()
        mock_sensor.min_value = 0
        mock_sensor.max_value = 100
        mock_sensor_class.query.get.return_value = mock_sensor
        
        data, error = SensorService.record_sensor_data(1, -10.0)
        
        assert data is None
        assert 'below minimum' in error
    
    @patch('app.services.sensor_service.Sensor')
    def test_record_sensor_data_above_max(self, mock_sensor_class):
        mock_sensor = MagicMock()
        mock_sensor.min_value = 0
        mock_sensor.max_value = 100
        mock_sensor_class.query.get.return_value = mock_sensor
        
        data, error = SensorService.record_sensor_data(1, 150.0)
        
        assert data is None
        assert 'above maximum' in error
    
    @patch('app.services.sensor_service.SensorData')
    def test_get_latest_sensor_data(self, mock_data_class):
        mock_data = MagicMock()
        mock_data_class.query.filter_by.return_value.order_by.return_value.first.return_value = mock_data
        
        result = SensorService.get_latest_sensor_data(1)
        
        assert result == mock_data
    
    def test_get_sensor_data_history(self):
        from unittest.mock import ANY
        mock_data1 = MagicMock()
        mock_data2 = MagicMock()
        mock_result = [mock_data1, mock_data2]
        
        with patch('app.services.sensor_service.SensorData') as mock_data_class:
            mock_filter = MagicMock()
            mock_order = MagicMock()
            mock_data_class.sensor_id = MagicMock()
            mock_data_class.sensor_id.__eq__ = MagicMock(return_value=ANY)
            mock_data_class.recorded_at = MagicMock()
            mock_data_class.recorded_at.__ge__ = MagicMock(return_value=ANY)
            mock_data_class.recorded_at.asc = MagicMock(return_value='asc')
            mock_data_class.query.filter.return_value = mock_filter
            mock_filter.order_by.return_value = mock_order
            mock_order.all.return_value = mock_result
            
            result = SensorService.get_sensor_data_history(1, hours=24)
        
        assert len(result) == 2
    
    def test_get_sensor_data_range(self):
        from unittest.mock import ANY
        mock_data = MagicMock()
        mock_result = [mock_data]
        
        with patch('app.services.sensor_service.SensorData') as mock_data_class:
            mock_filter = MagicMock()
            mock_order = MagicMock()
            mock_data_class.sensor_id = MagicMock()
            mock_data_class.sensor_id.__eq__ = MagicMock(return_value=ANY)
            mock_data_class.recorded_at = MagicMock()
            mock_data_class.recorded_at.__ge__ = MagicMock(return_value=ANY)
            mock_data_class.recorded_at.__le__ = MagicMock(return_value=ANY)
            mock_data_class.recorded_at.asc = MagicMock(return_value='asc')
            mock_data_class.query.filter.return_value = mock_filter
            mock_filter.order_by.return_value = mock_order
            mock_order.all.return_value = mock_result
            
            start = datetime.utcnow() - timedelta(hours=1)
            end = datetime.utcnow()
            result = SensorService.get_sensor_data_range(1, start, end)
        
        assert len(result) == 1
    
    @patch('app.services.sensor_service.Sensor')
    def test_get_current_readings(self, mock_sensor_class):
        mock_sensor = MagicMock()
        mock_sensor.type = 'temperature'
        mock_sensor.id = 1
        mock_sensor.name = 'Temperature'
        mock_sensor.unit = '°C'
        mock_sensor.get_latest_data.return_value = None
        mock_sensor_class.query.filter_by.return_value.all.return_value = [mock_sensor]
        
        result = SensorService.get_current_readings()
        
        assert 'temperature' in result
    
    @patch('app.services.sensor_service.SensorData')
    def test_get_sensor_statistics_with_data(self, mock_data_class):
        mock_data1 = MagicMock(value=20.0)
        mock_data2 = MagicMock(value=30.0)
        mock_data3 = MagicMock(value=25.0)
        
        with patch.object(SensorService, 'get_sensor_data_history', return_value=[mock_data1, mock_data2, mock_data3]):
            result = SensorService.get_sensor_statistics(1, hours=24)
        
        assert result['min'] == 20.0
        assert result['max'] == 30.0
        assert result['avg'] == 25.0
        assert result['count'] == 3
    
    def test_get_sensor_statistics_no_data(self):
        with patch.object(SensorService, 'get_sensor_data_history', return_value=[]):
            result = SensorService.get_sensor_statistics(1, hours=24)
        
        assert result['min'] is None
        assert result['max'] is None
        assert result['avg'] is None
        assert result['count'] == 0
    
    @patch('app.services.sensor_service.SensorData')
    def test_cleanup_old_data(self, mock_data_class):
        mock_data_class.cleanup_old_data.return_value = 10
        
        result = SensorService.cleanup_old_data(90)
        
        assert result == 10
