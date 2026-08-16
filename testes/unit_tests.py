import pytest
from app.services.forecast import Forecast

def test_forecast_init():
    f = Forecast(nr_simulations=10, backlog_min=5, backlog_max=10, capacity=80, throughput=[1,2,3,4])
    assert f.nr_simulations == 10
    assert f.backlog_min == 5
    assert f.backlog_max == 10
    assert f.capacity == 80
    assert f.throughput == [1,2,3,4]

def test_run_simulation_returns_list_of_ints():
    f = Forecast(nr_simulations=5, backlog_min=5, backlog_max=5, capacity=100, throughput=[1,2,3,4])
    result = f.run_simulations()
    assert isinstance(result, list)
    assert len(result) == 5
    assert all(isinstance(x, int) for x in result)

def test_calculate_percentiles_correct_values():
    data = [1, 2, 3, 4, 5]
    percentiles = [0, 50, 100]
    expected = {0: 1, 50: 3, 100: 5}
    result = Forecast.calculate_percentiles(data, percentiles)
    assert result == expected

def test_calculate_percentiles_empty_input_raises():
    with pytest.raises(ValueError):
        Forecast.calculate_percentiles([], [50])
    with pytest.raises(ValueError):
        Forecast.calculate_percentiles([1,2,3,4], [])

def test_format_forecast_response_structure():
    f = Forecast(nr_simulations=10, backlog_min=1, backlog_max=2, capacity=100, throughput=[1,2,3,4])
    response = f.format_forecast_response(throughput_forecast=[1,2,3,4], p50=5, p75=7, p85=8, p95=10)
    assert response['Backlog-min'] == 1
    assert response['Backlog-max'] == 2
    assert response['Throughput'] == [1,2,3,4]
    assert response['Throughput-Forecast'] == [1,2,3,4]
    assert response['Simulations'] == 10
    assert response['Percentil-50'] == 5
    assert response['Percentil-75'] == 7
    assert response['Percentil-85'] == 8
    assert response['Percentil-95'] == 10