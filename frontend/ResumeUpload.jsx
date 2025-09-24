import React, { useState } from 'react';
import axios from 'axios';

function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first");

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log(res.data);
      setResponse(res.data);
    } catch (err) {
      console.error(err.response?.data || err.message);
      alert('Upload failed: ' + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div>
      <h2>Upload Your Resume</h2>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload Resume</button>
      {response && (
        <div>
          <h3>Parsed Data:</h3>
          <pre>{JSON.stringify(response.data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default ResumeUpload;
