import React, { useState } from 'react';
import { Box, TextField, Button, Paper, Typography, CircularProgress } from '@mui/material';
import { executeCurlCommand } from './utils/curlGenerator';

function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiLog, setApiLog] = useState('');

  const handleQuerySubmit = async () => {
    setLoading(true);
    setError(null);

    // Log the API call
    const apiUrl = 'http://localhost:5000/api/execute';
    const curlCommand = `curl -X POST ${apiUrl} -H "Content-Type: application/json" -d '{"query": "${query.replace(/"/g, '\\"')}"}'`;
    const logEntry = `\n=== API Request Details ===\nEndpoint: ${apiUrl}\nCURL Command:\n${curlCommand}\n===========================\n`;
    setApiLog(logEntry);

    try {
      const data = await executeCurlCommand(query);
      setResult(data);
      
      // Log the response
      const responseLog = `\n=== API Response ===\nGenerated SQL: ${data.sql}\n===================\n`;
      setApiLog(prev => prev + responseLog);
    } catch (err) {
      setError(err.message);
      setApiLog(prev => prev + `\n=== Error ===\n${err.message}\n=============\n`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, margin: '0 auto' }}>
      <Typography variant="h4" gutterBottom>
        SQL Query Generator
      </Typography>
      
      <TextField
        fullWidth
        multiline
        rows={4}
        variant="outlined"
        placeholder="Enter your question here..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        sx={{ mb: 2 }}
      />
      
      <Button
        variant="contained"
        onClick={handleQuerySubmit}
        disabled={loading || !query.trim()}
        sx={{ mb: 3 }}
      >
        {loading ? <CircularProgress size={24} /> : 'Generate SQL'}
      </Button>

      {apiLog && (
        <Paper sx={{ p: 2, mb: 3, backgroundColor: '#f5f5f5' }}>
          <Typography variant="h6" gutterBottom>
            API Log:
          </Typography>
          <Box
            component="pre"
            sx={{
              overflowX: 'auto',
              whiteSpace: 'pre-wrap',
              wordWrap: 'break-word',
              p: 1,
              fontFamily: 'monospace',
              fontSize: '0.875rem'
            }}
          >
            {apiLog}
          </Box>
        </Paper>
      )}

      {result && (
        <>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Generated SQL:
            </Typography>
            <Box
              component="pre"
              sx={{
                overflowX: 'auto',
                whiteSpace: 'pre-wrap',
                wordWrap: 'break-word',
                p: 1,
                backgroundColor: '#f5f5f5',
                borderRadius: 1
              }}
            >
              {result.sql}
            </Box>
          </Paper>

          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Results:
            </Typography>
            {result.data.length > 0 ? (
              <Box sx={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr>
                      {result.columns.map((column) => (
                        <th key={column} style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.data.map((row, i) => (
                      <tr key={i}>
                        {result.columns.map((column) => (
                          <td key={column} style={{ border: '1px solid #ddd', padding: '8px' }}>
                            {row[column]?.toString() || ''}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Box>
            ) : (
              <Typography>No results found</Typography>
            )}
          </Paper>
        </>
      )}

      {error && (
        <Paper sx={{ p: 2, mt: 2, backgroundColor: '#ffebee' }}>
          <Typography color="error">Error: {error}</Typography>
        </Paper>
      )}
    </Box>
  );
}

export default App;