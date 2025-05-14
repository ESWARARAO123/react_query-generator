import React, { useState, useRef, useEffect } from 'react';
import { Box, TextField, Button, Paper, Typography, CircularProgress, Grid, Avatar } from '@mui/material';
import { executeCurlCommand } from './utils/curlGenerator';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const chatEndRef = useRef(null);

  // Scroll to bottom whenever conversations change
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversations]);

  const handleQuerySubmit = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    
    // Add user query to conversation
    const userMessage = {
      type: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString()
    };
    setConversations(prev => [...prev, userMessage]);
    
    // Log API request (for system message)
    const apiUrl = 'http://localhost:5000/api/execute';
    const curlCommand = `curl -X POST ${apiUrl} -H "Content-Type: application/json" -d '{"query": "${query.replace(/"/g, '\\"')}"}'`;
    const apiLog = `Endpoint: ${apiUrl}\nCURL: ${curlCommand}`;
    
    try {
      const data = await executeCurlCommand(query);
      
      // Add system response to conversation
      const systemMessage = {
        type: 'system',
        content: data,
        sql: data.sql,
        apiLog: apiLog,
        timestamp: new Date().toLocaleTimeString()
      };
      setConversations(prev => [...prev, systemMessage]);
    } catch (err) {
      // Add error message to conversation
      const errorMessage = {
        type: 'system',
        error: err.message,
        apiLog: apiLog,
        timestamp: new Date().toLocaleTimeString()
      };
      setConversations(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setQuery(''); // Clear input after submission
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuerySubmit();
    }
  };

  return (
    <Box sx={{ 
      p: 3, 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh',
      maxWidth: 1200, 
      margin: '0 auto'
    }}>
      <Typography variant="h4" gutterBottom>
        SQL Query Generator
      </Typography>
      
      {/* Chat history - scrollable area */}
      <Paper 
        sx={{ 
          flex: 1, 
          mb: 2, 
          overflow: 'auto', 
          p: 2,
          bgcolor: '#f8f9fa'
        }}
      >
        {conversations.length === 0 ? (
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            height: '100%',
            color: 'text.secondary'
          }}>
            <Typography variant="body1">
              Ask a question to generate SQL queries from natural language
            </Typography>
          </Box>
        ) : (
          conversations.map((msg, index) => (
            <Box 
              key={index} 
              sx={{ 
                display: 'flex', 
                mb: 2,
                justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start'
              }}
            >
              <Grid 
                container 
                spacing={1}
                justifyContent={msg.type === 'user' ? 'flex-end' : 'flex-start'}
                sx={{ maxWidth: '80%' }}
              >
                <Grid item>
                  <Avatar 
                    sx={{ 
                      bgcolor: msg.type === 'user' ? 'primary.main' : 'secondary.main',
                      width: 32,
                      height: 32
                    }}
                  >
                    {msg.type === 'user' ? <PersonIcon /> : <SmartToyIcon />}
                  </Avatar>
                </Grid>
                <Grid item xs>
                  <Paper 
                    sx={{ 
                      p: 2, 
                      bgcolor: msg.type === 'user' ? 'primary.light' : 'white',
                      color: msg.type === 'user' ? 'white' : 'text.primary',
                      borderRadius: 2,
                      ...(msg.error && { bgcolor: '#ffebee' })
                    }}
                  >
                    {msg.type === 'user' ? (
                      <Typography>{msg.content}</Typography>
                    ) : msg.error ? (
                      <>
                        <Typography color="error" gutterBottom>Error: {msg.error}</Typography>
                        <Typography variant="caption" component="div" sx={{ mt: 1, color: 'text.secondary' }}>
                          {msg.apiLog}
                        </Typography>
                      </>
                    ) : (
                      <>
                        <Typography variant="subtitle2" gutterBottom>Generated SQL:</Typography>
                        <Box
                          component="pre"
                          sx={{
                            overflowX: 'auto',
                            whiteSpace: 'pre-wrap',
                            wordWrap: 'break-word',
                            p: 1,
                            bgcolor: '#f5f5f5',
                            borderRadius: 1,
                            fontSize: '0.8rem',
                            mb: 2
                          }}
                        >
                          {msg.sql}
                        </Box>
                        
                        {msg.content.data.length > 0 ? (
                          <Box sx={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                              <thead>
                                <tr>
                                  {msg.content.columns.map((column) => (
                                    <th key={column} style={{ border: '1px solid #ddd', padding: '6px', textAlign: 'left', fontSize: '0.8rem' }}>
                                      {column}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {msg.content.data.map((row, i) => (
                                  <tr key={i}>
                                    {msg.content.columns.map((column) => (
                                      <td key={column} style={{ border: '1px solid #ddd', padding: '6px', fontSize: '0.8rem' }}>
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
                        
                        <Typography variant="caption" component="div" sx={{ mt: 1, color: 'text.secondary' }}>
                          {msg.apiLog}
                        </Typography>
                      </>
                    )}
                    <Typography variant="caption" display="block" sx={{ mt: 1, textAlign: 'right', color: msg.type === 'user' ? 'rgba(255,255,255,0.7)' : 'text.secondary' }}>
                      {msg.timestamp}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          ))
        )}
        <div ref={chatEndRef} />
      </Paper>
      
      {/* Input area */}
      <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          variant="outlined"
          placeholder="Ask a question..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          sx={{ mr: 2 }}
        />
        <Button
          variant="contained"
          onClick={handleQuerySubmit}
          disabled={loading || !query.trim()}
          sx={{ height: '56px', minWidth: '100px' }}
        >
          {loading ? <CircularProgress size={24} /> : 'Send'}
        </Button>
      </Paper>
    </Box>
  );
}

export default App;