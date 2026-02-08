import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [shortUrl, setShortUrl] = useState('');
  const [urls, setUrls] = useState([]);
  const [loading, setLoading] = useState(false);

  const shortenUrl = async () => {
    if (!url.trim()) {
      alert('Please enter a URL');
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/shorten', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      
      const data = await response.json();
      setShortUrl(data.short_url);
      setUrl('');
      fetchUrls();
    } catch (error) {
      alert('Failed to shorten URL');
    } finally {
      setLoading(false);
    }
  };

  const fetchUrls = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/urls');
      const data = await response.json();
      setUrls(data);
    } catch (error) {
      console.error('Failed to fetch URLs');
    }
  };

  useEffect(() => {
    fetchUrls();
  }, []);

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-container">
          <h1>🔗 URL Shortener</h1>
        </div>
      </nav>

      <div className="container">
        <div className="hero">
          <h2>Shorten Your URLs Instantly</h2>
          <p>Create short, memorable links in seconds</p>
        </div>

        <div className="card">
          <h3>Enter Your Long URL</h3>
          <div className="form-group">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/very-long-url"
              className="url-input"
            />
            <button
              onClick={shortenUrl}
              disabled={loading}
              className="submit-btn"
            >
              {loading ? 'Shortening...' : 'Shorten URL'}
            </button>
          </div>
          
          {shortUrl && (
            <div className="result">
              <h4>Your Short URL:</h4>
              <a href={shortUrl} target="_blank" rel="noopener noreferrer" className="short-url">
                {shortUrl}
              </a>
              <button
                onClick={() => navigator.clipboard.writeText(shortUrl)}
                className="copy-btn"
              >
                Copy
              </button>
            </div>
          )}
        </div>

        <div className="card">
          <h3>Recent URLs</h3>
          {urls.length === 0 ? (
            <p className="no-data">No URLs yet. Create your first one!</p>
          ) : (
            <div className="url-list">
              {urls.map((item) => (
                <div key={item.id} className="url-item">
                  <div className="url-info">
                    <a href={item.short_url} target="_blank" rel="noopener noreferrer" className="url-short">
                      {item.short_code}
                    </a>
                    <p className="clicks">{item.clicks} clicks</p>
                  </div>
                  <button
                    onClick={() => navigator.clipboard.writeText(item.short_url)}
                    className="copy-btn"
                  >
                    Copy
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <footer>
        <p>© {new Date().getFullYear()} URL Shortener</p>
      </footer>
    </div>
  );
}

export default App;