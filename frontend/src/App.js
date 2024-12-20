import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Loader from './components/Loader';
import { MdCloudUpload, MdDelete } from 'react-icons/md';
import Copy from './components/Copy';
import axios from 'axios'; 
import './App.css';

function App() {
  const [image, setImage] = useState(null);
  const [text, setText] = useState(null);
  const [progress, setProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [additionalText, setAdditionalText] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleDrop = (event) => {
    event.preventDefault();
    setIsLoading(true);
    const file = event.dataTransfer.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        const arrayBuffer = reader.result;
        const blob = new Blob([arrayBuffer], { type: file.type });
        setImage(blob); // Set the Blob object directly
      };
      reader.readAsArrayBuffer(file);
    }
    setIsLoading(false);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleChange = (event) => {
    setIsLoading(true);
    const file = event.target.files[0];
    setImage(file); 
    setIsLoading(false);
  };

  const deleteImage = () => {
    setIsLoading(true);
    setImage(null);
    setIsLoading(false);
  };

  const handleClick = async () => {
    if (!image) {
      setErrorMessage('Please upload the image!');
      return;
    }
  
    try {
      const formData = new FormData();
      formData.append('image', image); 
      console.log(image);
      const response = await axios.post('http://127.0.0.1:5000/convert', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Access-Control-Allow-Origin': '*'
        }
      });
      console.log(response.data.confidence);
      setText(response.data.text);
      setAdditionalText(response.data.correction)
      setConfidence(response.data.confidence)
      setErrorMessage(null);
    } catch (error) {
      if (error.response && error.response.data && error.response.data.error) {
      
        setErrorMessage(error.response.data.error); 
      } else {
        setErrorMessage('Error Converting Image To Text . Please Try Again.'); 

      }
    }
  };

  useEffect(() => {
    setText(text);
    setAdditionalText(additionalText);
    setConfidence(confidence)
  }, [text, additionalText, confidence]);

  return (
    <>
      <div className="menu">
        <ul>
          <li>IMAGE TO TEXT WEBSITE</li>
        </ul>
      </div>
      <div className="App" onDrop={handleDrop} onDragOver={handleDragOver}>
      
      </div>
      
      <header>
        <h1 className="header">Image to Text Converter</h1>
      </header>
      <div className="container">
      {errorMessage && <div className="error-message">{errorMessage}</div>}
        <div
          className="group"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {isLoading ? (
            <Loader />
          ) : (
            <>
              {!image ? (
                <>
                  <label className="label">
                    <div className="file-inner-container">
                      <MdCloudUpload className="upload-icon" />
                      <p className="upload-text">Click here to upload</p>
                      <p className="upload-text">DRAG    &      DROP</p>
                    </div>
                    <input
                      type="file"
                      name="uploadimage"
                      onChange={handleChange}
                      className="upload"
                    />
                  </label>
                </>
              ) : (
                <div className="dispaly-image">
                  <img
                    src={image instanceof Blob ? URL.createObjectURL(image) : image}
                    alt="uploaded"
                    className="uploaded-image"
                  />
                  <MdDelete className="delete-icon" onClick={deleteImage} />
                </div>
              )}
            </>
          )}
        </div>
        <button onClick={handleClick} className="btn">
          Convert to text
        </button>
        {progress < 100 && progress > 0 && (
          <div>
            <div className="progress-label">Progress ({progress}%)</div>
            <div className="progress-bar">
              <div className="progress" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        )}

        {text && (
          <>
          <span className="container">
          <label className="label"> Text
          <Copy text={text} /> 
          </label>
          </span>
          <span className="container">
          <label className="label"> Auto Correct
         
          <Copy text={additionalText} /> {}
          </label>
          </span>
          <span className="container">
          <label className="label"> Probability 
          <Copy text={confidence}/>{}
          </label>
          </span>
    
          </>
        )}
      </div>
    </>
  );
}

export default App;
