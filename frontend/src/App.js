import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Loader from './components/Loader';
import { MdCloudUpload, MdDelete } from 'react-icons/md';
import Copy from './components/Copy';
import axios from 'axios'; // Import axios
import './App.css';

function App() {
  const [image, setImage] = useState(null);
  const [text, setText] = useState(null);
  const [progress, setProgress] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [additionalText, setAdditionalText] = useState(null); // Add the additional text state with a more descriptive initial value
  const [confidence, setConfidence] = useState(null);

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
    setImage(file); // Set the file object directly
    setIsLoading(false);
  };

  const deleteImage = () => {
    setIsLoading(true);
    setImage(null);
    setIsLoading(false);
  };

  const handleClick = async () => {
    if (!image) {
      toast.error('Please upload the image!');
      return;
    }
  
    try {
      const formData = new FormData();
      formData.append('image', image); // Append the file directly
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
    } catch (error) {
      if (error.response && error.response.data && error.response.data.error) {
        // Display the error message from the server response
        toast.error(error.response.data.error);
      } else {
        console.error('Error occurred:', error);
        toast.error('Error converting image to text. Please try again.');
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
            <Copy text={text} /> {/* Display the extracted text */}
            <Copy text={additionalText} /> {}
            <Copy text={confidence}/>{}
           
          </>
        )}
      </div>
    </>
  );
}

export default App;
