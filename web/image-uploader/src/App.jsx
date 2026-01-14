import { useEffect } from 'react';
import './App.css'
import './ImageUploader.jsx'
import ImageUploader from './ImageUploader.jsx'

function App() {
  useEffect(() => {
    // Prevent files from being opened when dropped outside the box
    const preventDefault = (e) => e.preventDefault();
    window.addEventListener("dragover", preventDefault);
    window.addEventListener("drop", preventDefault);

    return () => {
      window.removeEventListener("dragover", preventDefault);
      window.removeEventListener("drop", preventDefault);
    };
  }, []);

  return (
    <>
      <ImageUploader></ImageUploader>
    </>
  )
}

export default App
