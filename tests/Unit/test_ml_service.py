from unittest.mock import patch,MagicMock
from app.services.model_service import predict_flower

def test_predict_flower_cache_hit():
    fake_data = {"sepal_length": 5.1, "sepal_width": 3.5 , "petal_length":3.1,"petal_width":2.6}

    with patch("app.services.model_service.make_cache_key", return_value="key"), \
         patch("app.services.model_service.get_cached_prediction", return_value={"prediction": 1}), \
         patch("app.services.model_service.get_model") as mock_model:

        result = predict_flower(fake_data)

        assert result == {"prediction": 1}
        mock_model.assert_not_called()

def test_predict_flower_cache_miss():
    fake_data = {"sepal_length": 6.2, "sepal_width": 3.1}

    mock_model = MagicMock()
    mock_model.predict.return_value = [2]

    with patch("app.services.model_service.make_cache_key", return_value="key"), \
         patch("app.services.model_service.get_cached_prediction", return_value=None), \
         patch("app.services.model_service.set_cached_prediction") as mock_set_cache, \
         patch("app.services.model_service.get_model", return_value=mock_model):

        result = predict_flower(fake_data)

        assert result == {"prediction": 2}
        mock_model.predict.assert_called_once()
        mock_set_cache.assert_called_once_with("key", {"prediction": 2})

def test_predict_flower_cache_key_consistency():
    data = {"sepal_length": 5.0, "sepal_width": 3.6}

    with patch("app.services.model_service.make_cache_key", return_value="same-key") as mock_key, \
         patch("app.services.model_service.get_cached_prediction", return_value={"prediction": 0}):

        result1 = predict_flower(data)
        result2 = predict_flower(data)

        assert result1 == result2
        assert mock_key.call_count == 2

def test_predict_flower_output_safety():
    fake_data = {"sepal_length": 7.1, "sepal_width": 3.0}

    mock_model = MagicMock()
    mock_model.predict.return_value = [1.0]  # float output from ML model

    with patch("app.services.model_service.make_cache_key", return_value="key"), \
         patch("app.services.model_service.get_cached_prediction", return_value=None), \
         patch("app.services.model_service.set_cached_prediction"), \
         patch("app.services.model_service.get_model", return_value=mock_model):

        result = predict_flower(fake_data)

        assert isinstance(result, dict)
        assert "prediction" in result
        assert isinstance(result["prediction"], int)


