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

  const handleDrop = (event) => {
    event.preventDefault();
    setIsLoading(true);
    const file = event.dataTransfer.files[0];
    setImage(URL.createObjectURL(file));
    setIsLoading(false);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleChange = (event) => {
    setIsLoading(true);
    setImage(URL.createObjectURL(event.target.files[0]));
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
      formData.append('image', image);
      const response = await axios.post('http://localhost:4002/convert', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setText(response.data.text);
    } catch (error) {
      console.error('Error occurred:', error);
      toast.error('Error converting image to text. Please try again.');
    }
  };

  useEffect(() => {
    setText(text);
  }, [text]);

  return (
    <>
   <div className="menu">
        <ul>
          <li>IMAGE TO TEXT WEBSITE</li>
        </ul>
      </div>
      <div className="App" onDrop={handleDrop} onDragOver={handleDragOver}>
      
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
                <>
                  <div className="dispaly-image">
                    <img src={image} alt="uploaded" className="uploaded-image" />
                    <MdDelete className="delete-icon" onClick={deleteImage} />
                  </div>
                </>
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

        {text && <Copy text={text} />}
      </div>
    </>
  );
}

export default App;
