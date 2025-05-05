import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [predictions, setPredictions] = useState([]);
  const [breedAnalysis, setBreedAnalysis] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    console.log('breedAnalysis updated:', breedAnalysis);
  }, [breedAnalysis]);

  useEffect(() => {
    console.log('predictions updated:', predictions);
  }, [predictions]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target.result);
      };
      reader.readAsDataURL(selectedFile);
      predictBreed(selectedFile);
    }
  };

  const predictBreed = async (file) => {
    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5001/service', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('API Response:', response.data);
      setPredictions(response.data.predictions || []);
      setBreedAnalysis(response.data.breed_analysis || null);
    } catch (error) {
      console.error('Error:', error);
      setError('오류가 발생했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <div className="card-header text-center">
          <h1 className="mb-0">
            <i className="fas fa-dog me-2"></i>강아지 품종 인식기
          </h1>
        </div>
        <div className="card-body">
          <div className="upload-section text-center">
            {preview && (
              <div className="preview-container d-block">
                <img src={preview} alt="Preview" className="preview d-block mx-auto" />
                <input
                  type="file"
                  id="fileInput"
                  accept="image/*"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                />
                <button
                  className="btn btn-primary mt-3 d-block mx-auto"
                  onClick={() => document.getElementById('fileInput').click()}
                >
                  <i className="fas fa-upload upload-icon"></i>사진 선택
                </button>
              </div>
            )}
            {!preview && (
              <div className="upload-container d-block">
                <input
                  type="file"
                  id="fileInput"
                  accept="image/*"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                />
                <button
                  className="btn btn-primary d-block mx-auto"
                  onClick={() => document.getElementById('fileInput').click()}
                >
                  <i className="fas fa-upload upload-icon"></i>사진 선택
                </button>
              </div>
            )}
            
            {loading && (
              <div className="loading">
                <i className="fas fa-spinner fa-spin"></i>
                <p className="mt-2">분석 중...</p>
              </div>
            )}

            {error && (
              <div className="alert alert-danger mt-3" role="alert">
                <i className="fas fa-exclamation-circle me-2"></i>
                {error}
              </div>
            )}
          </div>

          <div className="resultDiv">
            {predictions.length > 0 && (
              <div className="results mt-4">
                {predictions.map((prediction, index) => (
                  <div key={index} className="result-item">
                    <h5>
                      <i className="fas fa-paw me-2"></i>
                      {prediction.breed}
                    </h5>
                    <div className="d-flex align-items-center">
                      <span className="me-2">신뢰도:</span>
                      <div className="progress flex-grow-1">
                        <div
                          className="progress-bar"
                          role="progressbar"
                          style={{ width: `${prediction.confidence * 100}%` }}
                          aria-valuenow={prediction.confidence * 100}
                          aria-valuemin="0"
                          aria-valuemax="100"
                        >
                          {(prediction.confidence * 100).toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {breedAnalysis && (
              <div className="breed-analysis mt-4">
                <div className="result-item">
                  <h4 className="mb-3">
                    <i className="fas fa-info-circle me-2"></i>품종 상세 분석
                  </h4>
                  <div className="analysis-content">
                    <div className="personality-section">
                      <h5 className="text-primary">
                        <i className="fas fa-heart me-2"></i>성격 및 기질
                      </h5>
                      <div className="personality-content" style={{ whiteSpace: 'pre-wrap' }}>
                        {JSON.stringify(breedAnalysis).replace(/\\n/g, '\n')}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; 